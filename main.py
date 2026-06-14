"""Run the Sircles agent pipeline.

Usage:
    python main.py
    python main.py --lead 2
    python main.py --lead 2 --trace-only
"""

from datetime import datetime
import os
import sys

from orchestrator import print_artifacts, print_trace, run_pipeline
from tools.mock_tools import fetch_new_leads


def save_trace(state: dict, label: str):
    os.makedirs("traces", exist_ok=True)
    filename = f"traces/{label}_{datetime.now().strftime('%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("SIRCLES AGENT PIPELINE - RUN TRACE\n")
        f.write(f"Lead: {state['raw_lead']['email']}\n")
        f.write(f"Label: {label}\n")
        f.write(f"Run at: {datetime.now().isoformat()}\n")
        f.write("=" * 70 + "\n\n")

        f.write("TRACE LOG:\n")
        for line in state["trace"]:
            f.write(f"{line}\n")

        f.write("\nARTIFACTS SUMMARY:\n")
        f.write(f"ICP Score:    {state.get('icp_score', 'N/A')}\n")
        f.write(f"Disposition:  {state.get('final_disposition', 'N/A').upper()}\n")
        f.write(f"Human Review: {state.get('needs_human_review', False)}\n")

        debate = state.get("debate_record")
        if debate:
            f.write("\nDEBATE:\n")
            f.write(
                f"Winner: {debate.winner.agent_name} -> "
                f"{debate.winner.recommendation.upper()} ({debate.winner.confidence:.2f})\n"
            )
            f.write(
                f"Loser:  {debate.loser.agent_name} -> "
                f"{debate.loser.recommendation.upper()} ({debate.loser.confidence:.2f})\n"
            )
            f.write(f"Rule:   {debate.resolution_rule}\n")
            f.write(f"Winner reasoning: {debate.winner.reasoning}\n")
            f.write(f"Dissent reasoning: {debate.loser.reasoning}\n")
            f.write(f"Winner evidence: {debate.winner.evidence}\n")
            f.write(f"Loser evidence:  {debate.loser.evidence}\n")
            if debate.escalated:
                f.write(f"Escalation: {debate.escalation_reason}\n")

        outreach = state.get("outreach_draft")
        if outreach:
            f.write("\nOUTREACH DRAFT:\n")
            f.write(f"Subject: {outreach.email_subject}\n")
            f.write("Email:\n")
            for line in outreach.email_body.splitlines():
                f.write(f"  {line}\n")
            f.write(f"LinkedIn note: {outreach.linkedin_note}\n")
            f.write(f"Signals used: {outreach.personalisation_signals}\n")

        crm = state.get("crm_record")
        if crm:
            f.write("\nCRM RECORD:\n")
            f.write(f"Contact ID: {crm.contact_id}\n")
            f.write(f"Company ID: {crm.company_id}\n")
            f.write(f"Deal Stage: {crm.deal_stage}\n")
            f.write(f"Flags:      {crm.flags}\n")
            f.write(f"Created at: {crm.created_at}\n")

        onboarding = state.get("onboarding_record")
        if onboarding:
            f.write("\nONBOARDING RECORD:\n")
            f.write(f"Status: {onboarding.status}\n")
            f.write(f"Workspace ID: {onboarding.workspace_id}\n")
            f.write(f"Systems: {onboarding.systems_to_configure}\n")
            f.write(f"Tasks: {onboarding.setup_tasks}\n")
            f.write(f"Owner: {onboarding.owner}\n")
            f.write(f"Blockers: {onboarding.blockers}\n")
            f.write(f"Next step: {onboarding.next_step}\n")

        marketing = state.get("marketing_brief")
        if marketing:
            f.write("\nMARKETING BRIEF:\n")
            f.write(f"Audience segment: {marketing.audience_segment}\n")
            f.write(f"Recommended track: {marketing.recommended_track}\n")
            f.write(f"Competitor analysis: {marketing.competitor_analysis}\n")
            f.write(f"Content strategy: {marketing.content_strategy}\n")
            f.write(f"Visual strategy: {marketing.visual_strategy}\n")
            f.write(f"Communication strategy: {marketing.communication_strategy}\n")
            f.write(f"Historical models used: {marketing.historical_models_used}\n")

        if state.get("needs_human_review"):
            f.write(f"\nHUMAN REVIEW REQUIRED: {state['human_review_reason']}\n")

    print(f"Trace saved to {filename}")
    return filename


def run_lead(lead: dict, label: str, trace_only: bool = False):
    print("\n" + "#" * 70)
    print(f"RUNNING: {label.upper()} - {lead['email']}")
    print("#" * 70)
    state = run_pipeline(lead)
    print_trace(state)
    if not trace_only:
        print_artifacts(state)
    save_trace(state, label)
    return state


def main():
    leads = fetch_new_leads()
    labels = [lead["label"] for lead in leads]
    args = sys.argv[1:]
    trace_only = "--trace-only" in args
    lead_index = None

    if "--lead" in args:
        idx = args.index("--lead")
        lead_index = int(args[idx + 1])

    print("\n" + "#" * 70)
    print("SIRCLES MULTI-AGENT LEAD PIPELINE")
    print("Debate-first architecture with mock tools")
    print("#" * 70)

    if lead_index is not None:
        run_lead(leads[lead_index], labels[lead_index], trace_only)
    else:
        for lead, label in zip(leads, labels):
            run_lead(lead, label, trace_only)

    print("\nAll runs complete. Traces saved to traces/\n")


if __name__ == "__main__":
    main()
