import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.devil_advocate_agent import devil_advocate_agent
from agents.lead_intelligence_agent import lead_intelligence_agent
from orchestrator import ESCALATION_THRESHOLD, _resolve_debate, run_pipeline
from state import AgentPosition, SirclesState
from tools.mock_tools import enrich_company, enrich_contact, fetch_new_leads, score_icp


def make_position(agent_name, recommendation, confidence, evidence=None, reasoning="test"):
    return AgentPosition(
        agent_name=agent_name,
        recommendation=recommendation,
        confidence=confidence,
        evidence=evidence or ["test evidence"],
        reasoning=reasoning,
    )


def initial_state(lead: dict) -> SirclesState:
    return {
        "raw_lead": lead,
        "enriched_contact": None,
        "enriched_company": None,
        "icp_score": None,
        "lead_intelligence_position": None,
        "devil_advocate_position": None,
        "debate_record": None,
        "final_disposition": None,
        "outreach_draft": None,
        "crm_record": None,
        "onboarding_record": None,
        "marketing_brief": None,
        "trace": [],
        "needs_human_review": False,
        "human_review_reason": "",
    }


def make_state_with_positions(li_rec, li_conf, da_rec, da_conf) -> SirclesState:
    lead = fetch_new_leads()[0]
    state = initial_state(lead)
    enriched_contact = enrich_contact(lead["email"])
    enriched_company = enrich_company(lead["domain"])
    icp_result = score_icp(enriched_contact, enriched_company)
    return {
        **state,
        "enriched_contact": enriched_contact,
        "enriched_company": enriched_company,
        "icp_score": icp_result["icp_score"],
        "lead_intelligence_position": make_position("Lead Intelligence Agent", li_rec, li_conf),
        "devil_advocate_position": make_position("Devil's Advocate Agent", da_rec, da_conf),
    }


class TestResolutionRule:
    def test_consensus_both_agree(self):
        state = make_state_with_positions("pursue", 0.85, "pursue", 0.78)
        result = _resolve_debate(state)
        assert result["final_disposition"] == "pursue"
        assert result["debate_record"].escalated is False
        assert "CONSENSUS" in result["debate_record"].resolution_rule

    def test_higher_confidence_wins(self):
        state = make_state_with_positions("pursue", 0.85, "skip", 0.55)
        result = _resolve_debate(state)
        assert result["final_disposition"] == "pursue"
        assert result["debate_record"].winner.agent_name == "Lead Intelligence Agent"
        assert result["debate_record"].loser.recommendation == "skip"

    def test_devil_advocate_can_win(self):
        state = make_state_with_positions("pursue", 0.55, "skip", 0.82)
        result = _resolve_debate(state)
        assert result["final_disposition"] == "skip"
        assert result["debate_record"].winner.agent_name == "Devil's Advocate Agent"

    def test_dissent_is_recorded(self):
        state = make_state_with_positions("pursue", 0.85, "skip", 0.55)
        result = _resolve_debate(state)
        full_trace = " ".join(result["trace"])
        assert result["debate_record"].loser.recommendation == "skip"
        assert "Recorded dissent" in full_trace

    def test_escalation_on_small_gap(self):
        gap = ESCALATION_THRESHOLD - 0.01
        state = make_state_with_positions("pursue", 0.70, "skip", 0.70 - gap)
        result = _resolve_debate(state)
        assert result["final_disposition"] == "escalate"
        assert result["needs_human_review"] is True
        assert result["debate_record"].escalated is True

    def test_escalation_preserves_both_positions(self):
        state = make_state_with_positions("pursue", 0.60, "skip", 0.55)
        result = _resolve_debate(state)
        assert result["lead_intelligence_position"] is not None
        assert result["devil_advocate_position"] is not None
        assert "Winner: none" in " ".join(result["trace"])


class TestLeadIntelligenceAgent:
    def test_output_has_required_fields(self):
        state = initial_state(fetch_new_leads()[0])
        result = lead_intelligence_agent(state)
        assert result["enriched_contact"] is not None
        assert result["enriched_company"] is not None
        assert result["icp_score"] is not None
        assert result["lead_intelligence_position"] is not None

    def test_position_has_valid_confidence(self):
        for lead in fetch_new_leads():
            result = lead_intelligence_agent(initial_state(lead))
            assert 0.0 <= result["lead_intelligence_position"].confidence <= 1.0

    def test_position_has_evidence(self):
        result = lead_intelligence_agent(initial_state(fetch_new_leads()[0]))
        assert result["lead_intelligence_position"].evidence

    def test_position_has_valid_recommendation(self):
        valid = {"pursue", "nurture", "skip", "escalate"}
        for lead in fetch_new_leads():
            result = lead_intelligence_agent(initial_state(lead))
            assert result["lead_intelligence_position"].recommendation in valid

    def test_clear_pursue_lead(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "clear_pursue")
        result = lead_intelligence_agent(initial_state(lead))
        assert result["icp_score"] >= 0.60
        assert result["lead_intelligence_position"].recommendation == "pursue"

    def test_clear_skip_lead(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "clear_skip")
        result = lead_intelligence_agent(initial_state(lead))
        assert result["lead_intelligence_position"].recommendation == "skip"


class TestDevilAdvocateDisagreement:
    def test_competitor_case_produces_disagreement(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "ambiguous_competitor")
        state = lead_intelligence_agent(initial_state(lead))
        state = devil_advocate_agent(state)
        assert state["lead_intelligence_position"].recommendation != state["devil_advocate_position"].recommendation


class TestEndToEnd:
    def test_clear_pursue_full_pipeline(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "clear_pursue")
        state = run_pipeline(lead)
        assert state["final_disposition"] == "pursue"
        assert state["outreach_draft"] is not None
        assert state["crm_record"].deal_stage == "qualified_lead"

    def test_clear_skip_no_outreach(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "clear_skip")
        state = run_pipeline(lead)
        assert state["final_disposition"] == "skip"
        assert state["outreach_draft"] is None
        assert state["crm_record"].deal_stage == "disqualified"

    def test_all_leads_have_crm_record(self):
        for lead in fetch_new_leads():
            state = run_pipeline(lead)
            assert state["crm_record"] is not None

    def test_all_leads_have_full_trace(self):
        for lead in fetch_new_leads():
            state = run_pipeline(lead)
            assert len(state["trace"]) > 8

    def test_onboarding_agent_produces_structured_artifact(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "clear_pursue")
        state = run_pipeline(lead)
        onboarding = state["onboarding_record"]
        assert onboarding is not None
        assert onboarding.status == "prepared"
        assert onboarding.workspace_id
        assert onboarding.setup_tasks

    def test_marketing_strategy_agent_produces_structured_brief(self):
        lead = next(item for item in fetch_new_leads() if item["label"] == "ambiguous_competitor")
        state = run_pipeline(lead)
        brief = state["marketing_brief"]
        assert brief is not None
        assert brief.competitor_analysis
        assert brief.content_strategy
        assert brief.visual_strategy
        assert brief.communication_strategy
        assert brief.historical_models_used
