"""Onboarding Agent: prepare client setup on Sircles systems."""

from datetime import datetime

from state import OnboardingRecord, SirclesState
from tools.mock_tools import provision_onboarding_workspace


def onboarding_agent(state: SirclesState) -> SirclesState:
    trace = state["trace"].copy()
    contact = state["enriched_contact"]["data"]
    company = state["enriched_company"]["data"]
    disposition = state["final_disposition"]

    if disposition != "pursue":
        blockers = [f"Disposition is {disposition}; onboarding waits until a qualified lead advances"]
        if state.get("needs_human_review"):
            blockers.append(state.get("human_review_reason", "Human review required"))
        record = OnboardingRecord(
            status="not_applicable",
            workspace_id=None,
            systems_to_configure=[],
            setup_tasks=[],
            owner="unassigned",
            blockers=blockers,
            next_step="No client-system setup until the lead is accepted for pursuit.",
        )
        trace.append(f"[{_ts()}] Onboarding Agent: no setup created; blockers={blockers}")
        return {**state, "onboarding_record": record, "trace": trace}

    provisioned = provision_onboarding_workspace(contact, company)
    tasks = [
        f"Create Sircles workspace for {company['name']}",
        "Add contact and company to HubSpot lifecycle onboarding list",
        "Create CSM handoff task with enrichment and debate summary",
        "Prepare kickoff checklist for post-demo conversion",
    ]
    owner = "CSM Team - Growth"
    record = OnboardingRecord(
        status="prepared",
        workspace_id=provisioned["workspace_id"],
        systems_to_configure=provisioned["systems"],
        setup_tasks=tasks,
        owner=owner,
        blockers=[],
        next_step="Activate onboarding if the first-touch sequence converts to a qualified meeting.",
    )

    trace.append(
        f"[{_ts()}] Onboarding Agent: prepared workspace={record.workspace_id}; "
        f"owner={owner}; tasks={len(tasks)}"
    )
    return {**state, "onboarding_record": record, "trace": trace}


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")
