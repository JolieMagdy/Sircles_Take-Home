"""SDR Outreach Agent: draft personalized email and LinkedIn first touch."""

from datetime import datetime

from state import OutreachDraft, SirclesState


def sdr_outreach_agent(state: SirclesState) -> SirclesState:
    trace = state["trace"].copy()
    contact = state["enriched_contact"]["data"]
    company = state["enriched_company"]["data"]
    disposition = state["final_disposition"]

    if disposition != "pursue":
        trace.append(f"[{_ts()}] SDR Outreach Agent: skipped for disposition={disposition}")
        return {**state, "trace": trace}

    trace.append(
        f"[{_ts()}] SDR Outreach Agent: drafting for "
        f"{contact['first_name']} {contact['last_name']} at {company['name']}"
    )
    signals = _extract_signals(contact, company)
    email_subject, email_body = _draft_email(contact, company)
    linkedin_note = _draft_linkedin(contact, company, signals)

    draft = OutreachDraft(
        email_subject=email_subject,
        email_body=email_body,
        linkedin_note=linkedin_note,
        personalisation_signals=signals,
    )

    trace.append(f"[{_ts()}] SDR Outreach Agent: email and LinkedIn note complete")
    return {**state, "outreach_draft": draft, "trace": trace}


def _extract_signals(contact: dict, company: dict) -> list[str]:
    signals = []

    if company.get("funding_stage") in ["Series A", "Series B", "Series C"]:
        signals.append(f"recently raised {company['funding_stage']}")

    hiring = company.get("hiring_signals", [])
    if hiring:
        signals.append(f"actively hiring {', '.join(hiring[:2])}")

    relevant_tech = [
        tech
        for tech in company.get("tech_stack", [])
        if tech in ["HubSpot", "Salesforce", "Segment", "Intercom"]
    ]
    if relevant_tech:
        signals.append(f"using {', '.join(relevant_tech)}")

    if contact.get("seniority") in ["director", "vp", "c_suite"]:
        signals.append(f"{contact['title']} decision-maker level")

    history = contact.get("employment_history", [])
    if history:
        signals.append(f"background at {history[0].split('(')[0].strip()}")

    return signals


def _draft_email(contact: dict, company: dict) -> tuple[str, str]:
    first = contact["first_name"]
    title = contact["title"]
    company_name = company["name"]
    industry = company["industry"]
    funding = company.get("funding_stage", "growth")
    hiring = company.get("hiring_signals", [])

    subject = f"Community-led growth for {company_name}'s {funding} stage"
    hiring_line = ""
    if hiring:
        hiring_line = (
            f"\n\nI also noticed you're hiring {hiring[0]}. That usually means the team "
            "is scaling fast and the pressure to hit pipeline targets rises with it."
        )

    body = f"""Hi {first},

I came across {company_name} and your work as {title} in the {industry} space.{hiring_line}

A lot of {funding}-stage teams we work with are hitting the same wall: demand gen spend is up, but community engagement is not scaling with it.

At Sircles, we help teams like yours build AI-powered community engagement systems that turn your audience into a growth engine, not just a support channel.

Worth a 20-minute call to see if there is a fit? I will keep it specific to {company_name}'s situation.

Best,
[SDR Name]
Sircles
"""
    return subject, body


def _draft_linkedin(contact: dict, company: dict, signals: list[str]) -> str:
    first = contact["first_name"]
    company_name = company["name"]
    funding = company.get("funding_stage", "growth")
    signal = signals[0] if signals else f"your work at {company_name}"
    note = (
        f"Hi {first} - noticed {company_name} {signal}. We help {funding}-stage "
        "teams build community-led growth with AI. Would love to connect."
    )
    return note[:297] + "..." if len(note) > 300 else note


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
