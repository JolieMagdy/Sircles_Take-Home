"""Devil's Advocate Agent: independent risk review for the debate."""

from datetime import datetime

from state import AgentPosition, Disposition, SirclesState


def devil_advocate_agent(state: SirclesState) -> SirclesState:
    trace = state["trace"].copy()
    contact_data = state["enriched_contact"]["data"]
    company_data = state["enriched_company"]["data"]
    icp_score = state["icp_score"]
    li_position = state["lead_intelligence_position"]

    trace.append("[{}] Devil's Advocate Agent: reviewing counterarguments".format(_ts()))
    trace.append(
        f"[{_ts()}] Lead Intelligence proposed "
        f"{li_position.recommendation.upper()} confidence={li_position.confidence:.2f}"
    )

    recommendation, confidence, evidence, reasoning = _challenge(
        icp_score, contact_data, company_data, li_position
    )
    position = AgentPosition(
        agent_name="Devil's Advocate Agent",
        recommendation=recommendation,
        confidence=confidence,
        evidence=evidence,
        reasoning=reasoning,
    )

    trace.append(
        f"[{_ts()}] Devil's Advocate recommendation: "
        f"{recommendation.upper()} confidence={confidence:.2f}"
    )

    if recommendation == li_position.recommendation:
        trace.append(f"[{_ts()}] Debate converged on {recommendation.upper()}")
    else:
        trace.append(
            f"[{_ts()}] Debate triggered: "
            f"Lead Intelligence={li_position.recommendation.upper()} vs "
            f"Devil's Advocate={recommendation.upper()}"
        )

    return {**state, "devil_advocate_position": position, "trace": trace}


def _challenge(
    icp_score: float,
    contact: dict,
    company: dict,
    li_position: AgentPosition,
) -> tuple[Disposition, float, list[str], str]:
    evidence = []
    is_competitor = company.get("is_competitor", False)
    headcount = company.get("headcount", 0)
    funding_stage = company.get("funding_stage", "Unknown")
    industry = company.get("industry", "Unknown")
    seniority = contact.get("seniority", "unknown")
    hiring_signals = company.get("hiring_signals", [])

    if headcount < 5:
        return (
            "skip",
            0.95,
            ["Micro-company with no realistic procurement cycle", "No verified buying motion"],
            "Single-person or micro-company leads are not worth SDR time for this workflow.",
        )

    if is_competitor:
        evidence = [
            "Direct competitor; IP and sales-intelligence risk",
            "Engagement could expose Sircles positioning and sales motion",
            "Partner framing is speculative for this stage",
            f"Industry overlap confirmed: {industry}",
        ]
        return (
            "skip",
            0.78,
            evidence,
            f"Although the ICP score is {icp_score:.2f}, the direct competitor flag is "
            "more important than fit. Nurture value is uncertain, while intelligence "
            "leakage risk is concrete.",
        )

    if icp_score >= 0.70:
        risks = []
        if not contact.get("phone_verified"):
            risks.append("Phone not verified; outreach reliability reduced")
        if funding_stage not in ["Series A", "Series B", "Series C"]:
            risks.append(f"Funding stage '{funding_stage}' may limit budget")
        if seniority not in ["director", "vp", "c_suite"]:
            risks.append(f"Seniority '{seniority}' may lack buying authority")
        if not hiring_signals:
            risks.append("No active hiring signals")

        if risks:
            return (
                "nurture",
                round(0.50 + len(risks) * 0.05, 2),
                risks + [f"ICP score {icp_score:.2f} is strong but risk remains"],
                f"ICP fit is promising, but {len(risks)} risk signal(s) argue for "
                "qualification before SDR outreach.",
            )

        return (
            "pursue",
            round(icp_score * 0.90, 2),
            [f"ICP score {icp_score:.2f} confirmed", "No material risk factors found"],
            "Independent review found no disqualifying risk. Pursue is justified.",
        )

    if icp_score >= 0.45:
        evidence = [
            f"ICP score {icp_score:.2f} is below a strong engagement threshold",
            "Nurture ROI is weak when fit is marginal",
            f"Industry: {industry}",
        ]
        if not hiring_signals:
            evidence.append("No hiring signals")
        return (
            "skip",
            0.58,
            evidence,
            "The nurture recommendation may spend automation capacity on a weak-fit lead. "
            "Better to keep the pipeline focused on stronger prospects.",
        )

    return (
        "skip",
        0.90,
        [f"ICP score {icp_score:.2f} is well below threshold", "Weak fit confirmed"],
        f"Weak ICP score ({icp_score:.2f}) makes skip the only sensible outcome.",
    )


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
