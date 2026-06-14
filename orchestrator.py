"""Orchestrator for the Sircles debate-first lead pipeline.

Resolution rule:
1. If both agents agree, accept consensus and record both positions.
2. If agents disagree, the higher-confidence recommendation wins.
3. If the confidence gap is below 0.12, escalate for human review.
4. If the highest confidence is below 0.45, escalate for human review.
"""

from datetime import datetime

from agents.crm_hygiene_agent import crm_hygiene_agent
from agents.devil_advocate_agent import devil_advocate_agent
from agents.lead_intelligence_agent import lead_intelligence_agent
from agents.marketing_strategy_agent import marketing_strategy_agent
from agents.onboarding_agent import onboarding_agent
from agents.sdr_outreach_agent import sdr_outreach_agent
from state import DebateRecord, SirclesState


ESCALATION_THRESHOLD = 0.12
MIN_CONFIDENCE = 0.45


def run_pipeline(raw_lead: dict) -> SirclesState:
    state: SirclesState = {
        "raw_lead": raw_lead,
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

    state["trace"].append(
        f"[{_ts()}] ORCHESTRATOR START: lead={raw_lead['email']} "
        f"source={raw_lead.get('source', 'unknown')}"
    )

    state["trace"].append(f"[{_ts()}] Handoff: Lead Intelligence Agent")
    state = lead_intelligence_agent(state)

    state["trace"].append(f"[{_ts()}] Handoff: Devil's Advocate Agent")
    state = devil_advocate_agent(state)

    state["trace"].append(f"[{_ts()}] Handoff: Orchestrator debate resolution")
    state = _resolve_debate(state)

    disposition = state["final_disposition"]
    state["trace"].append(f"[{_ts()}] Route selected: disposition={disposition}")

    if disposition == "pursue":
        state["trace"].append(f"[{_ts()}] Handoff: SDR Outreach Agent")
        state = sdr_outreach_agent(state)
    else:
        state = sdr_outreach_agent(state)

    state["trace"].append(f"[{_ts()}] Handoff: CRM Hygiene Agent")
    state = crm_hygiene_agent(state)

    state["trace"].append(f"[{_ts()}] Handoff: Onboarding Agent")
    state = onboarding_agent(state)

    state["trace"].append(f"[{_ts()}] Handoff: Marketing Strategy Agent")
    state = marketing_strategy_agent(state)

    state["trace"].append(
        f"[{_ts()}] ORCHESTRATOR COMPLETE: disposition={disposition} "
        f"human_review={state['needs_human_review']}"
    )
    return state


def _resolve_debate(state: SirclesState) -> SirclesState:
    trace = state["trace"].copy()
    li = state["lead_intelligence_position"]
    da = state["devil_advocate_position"]

    trace.append("[{}] Debate resolution: applying documented rule".format(_ts()))
    trace.append(
        f"[{_ts()}] Position A: {li.agent_name} recommends "
        f"{li.recommendation.upper()} confidence={li.confidence:.2f}; evidence={li.evidence}"
    )
    trace.append(
        f"[{_ts()}] Position B: {da.agent_name} recommends "
        f"{da.recommendation.upper()} confidence={da.confidence:.2f}; evidence={da.evidence}"
    )

    if li.recommendation == da.recommendation:
        avg_confidence = round((li.confidence + da.confidence) / 2, 3)
        resolution_rule = (
            f"CONSENSUS: both agents recommended {li.recommendation.upper()}; "
            f"average confidence {avg_confidence:.2f}."
        )
        debate_record = DebateRecord(
            winner=li,
            loser=da,
            resolution_rule=resolution_rule,
            outcome=li.recommendation,
            escalated=False,
        )
        trace.append(
            f"[{_ts()}] Winner: consensus on {li.recommendation.upper()}; "
            f"no dissenting loser because recommendations matched"
        )
        return {
            **state,
            "debate_record": debate_record,
            "final_disposition": li.recommendation,
            "trace": trace,
        }

    conf_gap = abs(li.confidence - da.confidence)
    max_conf = max(li.confidence, da.confidence)
    trace.append(f"[{_ts()}] Disagreement: confidence_gap={conf_gap:.2f}")

    if conf_gap < ESCALATION_THRESHOLD:
        reason = (
            f"Confidence gap {conf_gap:.2f} is below threshold "
            f"{ESCALATION_THRESHOLD:.2f}; cannot choose reliably."
        )
        return _escalate(state, li, da, reason, trace)

    if max_conf < MIN_CONFIDENCE:
        reason = (
            f"Highest confidence {max_conf:.2f} is below minimum "
            f"{MIN_CONFIDENCE:.2f}; neither agent is certain enough."
        )
        return _escalate(state, li, da, reason, trace)

    winner, loser = (li, da) if li.confidence >= da.confidence else (da, li)
    resolution_rule = (
        f"CONFIDENCE-WEIGHTED VOTE: {winner.agent_name} wins "
        f"{winner.confidence:.2f} to {loser.confidence:.2f}; "
        f"gap {conf_gap:.2f} is above threshold {ESCALATION_THRESHOLD:.2f}. "
        f"{loser.agent_name}'s {loser.recommendation.upper()} is recorded as dissent."
    )
    debate_record = DebateRecord(
        winner=winner,
        loser=loser,
        resolution_rule=resolution_rule,
        outcome=winner.recommendation,
        escalated=False,
    )

    trace.append(f"[{_ts()}] Winner: {winner.agent_name} -> {winner.recommendation.upper()}")
    trace.append(f"[{_ts()}] Loser: {loser.agent_name} -> {loser.recommendation.upper()}")
    trace.append(f"[{_ts()}] Recorded dissent: {loser.reasoning}")

    return {
        **state,
        "debate_record": debate_record,
        "final_disposition": winner.recommendation,
        "trace": trace,
    }


def _escalate(state, li, da, reason, trace) -> SirclesState:
    resolution_rule = f"ESCALATED: {reason}"
    debate_record = DebateRecord(
        winner=li,
        loser=da,
        resolution_rule=resolution_rule,
        outcome="escalate",
        escalated=True,
        escalation_reason=reason,
    )
    trace.append(f"[{_ts()}] Escalation triggered: {reason}")
    trace.append(
        f"[{_ts()}] Winner: none; unresolved positions preserved for human review"
    )
    trace.append(
        f"[{_ts()}] Dissent/unresolved: {li.agent_name}={li.recommendation.upper()} "
        f"vs {da.agent_name}={da.recommendation.upper()}"
    )
    return {
        **state,
        "debate_record": debate_record,
        "final_disposition": "escalate",
        "needs_human_review": True,
        "human_review_reason": reason,
        "trace": trace,
    }


def print_trace(state: SirclesState):
    print("\n" + "=" * 70)
    print(f"TRACE - {state['raw_lead']['email']}")
    print("=" * 70)
    for line in state["trace"]:
        print(line)
    print("=" * 70)


def print_artifacts(state: SirclesState):
    print("\n" + "-" * 70)
    print("OUTPUT ARTIFACTS")
    print("-" * 70)
    print(f"Lead:         {state['raw_lead']['email']}")
    print(f"ICP Score:    {state.get('icp_score', 0):.2f}")
    print(f"Disposition:  {state.get('final_disposition', 'N/A').upper()}")
    print(f"Human Review: {state.get('needs_human_review', False)}")

    debate = state.get("debate_record")
    if debate:
        print("\nDebate:")

    if debate.escalated:
        print(
            f"  Position A: {debate.winner.agent_name} -> "
            f"{debate.winner.recommendation.upper()} ({debate.winner.confidence:.2f})"
        )
        print(
            f"  Position B: {debate.loser.agent_name} -> "
            f"{debate.loser.recommendation.upper()} ({debate.loser.confidence:.2f})"
        )
        print(f"  Rule: {debate.resolution_rule}")
        print(f"  Escalated: {debate.escalation_reason}")

    else:
        print(
            f"  Winner: {debate.winner.agent_name} -> "
            f"{debate.winner.recommendation.upper()} ({debate.winner.confidence:.2f})"
        )
        print(
            f"  Loser:  {debate.loser.agent_name} -> "
            f"{debate.loser.recommendation.upper()} ({debate.loser.confidence:.2f})"
        )
        print(f"  Rule: {debate.resolution_rule}")

    outreach = state.get("outreach_draft")
    if outreach:
        print("\nOutreach:")
        print(f"  Subject:  {outreach.email_subject}")
        print(f"  LinkedIn: {outreach.linkedin_note}")

    crm = state.get("crm_record")
    if crm:
        print("\nCRM Record:")
        print(f"  Contact ID: {crm.contact_id}")
        print(f"  Deal Stage: {crm.deal_stage}")
        print(f"  Flags:      {crm.flags or 'none'}")

    onboarding = state.get("onboarding_record")
    if onboarding:
        print("\nOnboarding:")
        print(f"  Status:       {onboarding.status}")
        print(f"  Workspace ID: {onboarding.workspace_id or 'none'}")
        print(f"  Owner:        {onboarding.owner}")
        print(f"  Next Step:    {onboarding.next_step}")

    marketing = state.get("marketing_brief")
    if marketing:
        print("\nMarketing Brief:")
        print(f"  Segment: {marketing.audience_segment}")
        print(f"  Track:   {marketing.recommended_track}")
        print(f"  Models:  {marketing.historical_models_used}")

    if state.get("needs_human_review"):
        print(f"\nHuman review required: {state['human_review_reason']}")

    print("-" * 70 + "\n")


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
