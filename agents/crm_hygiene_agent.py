"""CRM Hygiene Agent: write a structured mock HubSpot record."""

from datetime import datetime

from state import CRMRecord, SirclesState
from tools.mock_tools import upsert_crm_record


DEAL_STAGE_MAP = {
    "pursue": "qualified_lead",
    "nurture": "awareness",
    "skip": "disqualified",
    "escalate": "pending_human_review",
}


def crm_hygiene_agent(state: SirclesState) -> SirclesState:
    trace = state["trace"].copy()
    contact = state["enriched_contact"]["data"]
    company = state["enriched_company"]["data"]
    disposition = state["final_disposition"]
    debate = state.get("debate_record")

    trace.append(
        f"[{_ts()}] CRM Hygiene Agent: building record for {contact['email']} "
        f"with disposition={disposition}"
    )

    deal_stage = DEAL_STAGE_MAP.get(disposition, "unknown")
    flags = _identify_flags(state)
    crm_payload = {
        "email": contact["email"],
        "first_name": contact["first_name"],
        "last_name": contact["last_name"],
        "title": contact["title"],
        "company_name": company["name"],
        "company_domain": company.get("domain", ""),
        "industry": company.get("industry", ""),
        "headcount": company.get("headcount", 0),
        "funding_stage": company.get("funding_stage", ""),
        "icp_score": state.get("icp_score", 0),
        "disposition": disposition,
        "deal_stage": deal_stage,
        "is_competitor": company.get("is_competitor", False),
        "lead_source": state["raw_lead"].get("source", "unknown"),
        "debate_outcome": _debate_payload(debate),
        "flags": flags,
        "outreach_drafted": state.get("outreach_draft") is not None,
    }

    crm_response = upsert_crm_record(crm_payload)
    record = CRMRecord(
        contact_id=crm_response["contact_id"],
        company_id=f"CO-{company.get('domain', 'unknown').upper().replace('.', '_')}",
        deal_stage=deal_stage,
        disposition=disposition,
        enriched_data=crm_payload,
        flags=flags,
        created_at=datetime.now().isoformat(),
    )

    trace.append(
        f"[{_ts()}] CRM Hygiene Agent: upserted {record.contact_id}; "
        f"deal_stage={deal_stage}; flags={flags or 'none'}"
    )
    return {**state, "crm_record": record, "trace": trace}


def _debate_payload(debate) -> dict:
    if not debate:
        return {}
    return {
        "winner": debate.winner.agent_name,
        "winner_recommendation": debate.winner.recommendation,
        "winner_confidence": debate.winner.confidence,
        "loser": debate.loser.agent_name,
        "loser_recommendation": debate.loser.recommendation,
        "loser_confidence": debate.loser.confidence,
        "resolution_rule": debate.resolution_rule,
        "escalated": debate.escalated,
        "escalation_reason": debate.escalation_reason,
    }


def _identify_flags(state: SirclesState) -> list[str]:
    flags = []
    company = state["enriched_company"]["data"] if state.get("enriched_company") else {}
    debate = state.get("debate_record")

    if state.get("needs_human_review"):
        flags.append(f"ESCALATED BY DEBATE SYSTEM: {state.get('human_review_reason', '')}")

    if company.get("is_competitor") and state.get("final_disposition") != "skip":
        flags.append("COMPETITOR FLAG: manual review before outreach")

    icp = state.get("icp_score", 0) or 0
    if icp >= 0.70 and state.get("final_disposition") == "skip":
        flags.append(f"HIGH ICP SCORE ({icp:.2f}) but disposition is SKIP")

    if debate and not debate.escalated:
        li = state.get("lead_intelligence_position")
        da = state.get("devil_advocate_position")
        if (
            li
            and da
            and li.recommendation != da.recommendation
            and abs(li.confidence - da.confidence) < 0.15
        ):
            flags.append(f"CLOSE DEBATE: confidence gap {abs(li.confidence - da.confidence):.2f}")

    return flags


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
