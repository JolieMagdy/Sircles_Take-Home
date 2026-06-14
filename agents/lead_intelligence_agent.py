"""Lead Intelligence Agent: enrich, score ICP, and propose a disposition."""

from datetime import datetime

from state import AgentPosition, Disposition, SirclesState
from tools.mock_tools import enrich_company, enrich_contact, score_icp


def lead_intelligence_agent(state: SirclesState) -> SirclesState:
    lead = state["raw_lead"]
    email = lead["email"]
    domain = lead["domain"]
    trace = state["trace"].copy()

    trace.append(f"[{_ts()}] Lead Intelligence Agent: enriching {email}")

    enriched_contact = enrich_contact(email)
    enriched_company = enrich_company(domain)
    contact_data = enriched_contact["data"]
    company_data = enriched_company["data"]

    trace.append(
        f"[{_ts()}] Enrichment: {contact_data['title']} at "
        f"{company_data['name']} ({company_data['industry']})"
    )

    icp_result = score_icp(enriched_contact, enriched_company)
    icp_score = icp_result["icp_score"]
    trace.append(
        f"[{_ts()}] ICP score {icp_score:.2f}; "
        f"signals={icp_result['positive_signals']}; penalties={icp_result['penalties']}"
    )

    recommendation, confidence, evidence, reasoning = _propose(
        icp_score, icp_result, contact_data, company_data
    )
    position = AgentPosition(
        agent_name="Lead Intelligence Agent",
        recommendation=recommendation,
        confidence=confidence,
        evidence=evidence,
        reasoning=reasoning,
    )

    trace.append(
        f"[{_ts()}] Lead Intelligence recommendation: "
        f"{recommendation.upper()} confidence={confidence:.2f}"
    )

    return {
        **state,
        "enriched_contact": enriched_contact,
        "enriched_company": enriched_company,
        "icp_score": icp_score,
        "lead_intelligence_position": position,
        "trace": trace,
    }


def _propose(
    icp_score: float,
    icp_result: dict,
    contact: dict,
    company: dict,
) -> tuple[Disposition, float, list[str], str]:
    evidence = icp_result["positive_signals"].copy()
    is_competitor = icp_result.get("is_competitor", False)

    if company.get("headcount", 0) < 5:
        return (
            "skip",
            0.92,
            ["Headcount < 5; not a viable prospect"] + icp_result["penalties"],
            "Company has fewer than 5 employees, so there is no credible budget or team "
            "scale to justify SDR attention.",
        )

    if is_competitor:
        fit_evidence = [item for item in evidence if "competitor" not in item.lower()]
        fit_evidence.append("Competitor flag noted; relationship value may still exist")
        confidence = round(min(0.72, icp_score + 0.10), 2)
        if icp_score >= 0.45:
            return (
                "nurture",
                confidence,
                fit_evidence,
                f"ICP score {icp_score:.2f} shows strong industry, seniority, and growth "
                "signals. The competitor flag blocks direct pursuit, but a nurture path "
                "preserves optionality for partner, ecosystem, or future career movement.",
            )
        return (
            "skip",
            0.75,
            icp_result["penalties"],
            f"Competitor risk plus weak ICP score ({icp_score:.2f}) leaves no practical "
            "conversion path.",
        )

    if icp_score >= 0.70:
        confidence = min(round(0.60 + (icp_score - 0.70) * 1.5, 2), 0.95)
        return (
            "pursue",
            confidence,
            evidence,
            f"Strong ICP match ({icp_score:.2f}). Contact seniority, funding stage, "
            "hiring signals, and tech stack suggest budget and timing for first-touch "
            "outreach.",
        )

    if icp_score >= 0.45:
        confidence = round(0.45 + (icp_score - 0.45) * 0.8, 2)
        return (
            "nurture",
            confidence,
            evidence + ["Score below pursue threshold of 0.70"],
            f"Moderate ICP fit ({icp_score:.2f}). There are useful signals, but not "
            "enough urgency for immediate SDR pursuit.",
        )

    confidence = min(round(0.70 + (0.45 - icp_score), 2), 0.92)
    return (
        "skip",
        confidence,
        icp_result["penalties"],
        f"Weak ICP match ({icp_score:.2f}) with disqualifying signals. Outreach would "
        "consume SDR capacity with low conversion probability.",
    )


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
