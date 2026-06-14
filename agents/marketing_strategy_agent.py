"""Marketing Strategy Agent: produce a mock campaign and positioning brief."""

from datetime import datetime

from state import MarketingBrief, SirclesState
from tools.mock_tools import fetch_sircles_marketing_playbook


def marketing_strategy_agent(state: SirclesState) -> SirclesState:
    trace = state["trace"].copy()
    company = state["enriched_company"]["data"]
    contact = state["enriched_contact"]["data"]
    disposition = state["final_disposition"]
    playbook = fetch_sircles_marketing_playbook()

    segment = company.get("industry") or "default"
    segment_playbook = playbook["segments"].get(segment, playbook["segments"]["default"])
    competitor_analysis = _competitor_analysis(company, disposition)
    communication_strategy = _communication_strategy(contact, company, disposition)

    brief = MarketingBrief(
        audience_segment=segment,
        competitor_analysis=competitor_analysis,
        content_strategy=segment_playbook["content"],
        visual_strategy=segment_playbook["visuals"],
        communication_strategy=communication_strategy,
        historical_models_used=playbook["models"],
        recommended_track=segment_playbook["track"],
    )

    trace.append(
        f"[{_ts()}] Marketing Strategy Agent: brief ready; "
        f"track='{brief.recommended_track}'; models={brief.historical_models_used}"
    )
    return {**state, "marketing_brief": brief, "trace": trace}


def _competitor_analysis(company: dict, disposition: str) -> list[str]:
    if company.get("is_competitor"):
        return [
            "Direct competitor flag: avoid revealing pricing, playbooks, or sales motion",
            "Use suppression or executive-only review instead of automated nurture",
            "Positioning risk outweighs short-term relationship upside",
        ]

    analysis = [
        f"Industry context: {company.get('industry', 'unknown')}",
        f"Company scale: {company.get('headcount_range', company.get('headcount', 'unknown'))}",
    ]
    if disposition == "pursue":
        analysis.append("No competitor block; messaging can reference growth and community ROI")
    elif disposition == "escalate":
        analysis.append("Hold campaign activation until human review resolves the debate")
    else:
        analysis.append("Use low-touch or suppression strategy based on final disposition")
    return analysis


def _communication_strategy(contact: dict, company: dict, disposition: str) -> list[str]:
    if disposition == "pursue":
        return [
            f"Lead with {company['name']}'s growth stage and hiring momentum",
            f"Tailor proof points to {contact['title']} responsibilities",
            "Keep CTA to a specific 20-minute fit conversation",
        ]
    if disposition == "nurture":
        return [
            "Use educational content instead of direct sales asks",
            "Re-score if new funding, hiring, or community signals appear",
        ]
    if disposition == "escalate":
        return [
            "Pause automated outreach",
            "Give reviewer both debate positions and the competitor/fit evidence",
        ]
    return [
        "Suppress from SDR outreach",
        "Retain structured disqualification reason for future scoring calibration",
    ]


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
