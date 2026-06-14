"""Shared state for the Sircles multi-agent lead pipeline."""

from dataclasses import dataclass
from typing import Literal, Optional, TypedDict


Disposition = Literal["pursue", "nurture", "skip", "escalate"]


@dataclass
class AgentPosition:
    agent_name: str
    recommendation: Disposition
    confidence: float
    evidence: list[str]
    reasoning: str


@dataclass
class DebateRecord:
    winner: AgentPosition
    loser: AgentPosition
    resolution_rule: str
    outcome: Disposition
    escalated: bool = False
    escalation_reason: str = ""


@dataclass
class CRMRecord:
    contact_id: str
    company_id: str
    deal_stage: str
    disposition: Disposition
    enriched_data: dict
    flags: list[str]
    created_at: str


@dataclass
class OutreachDraft:
    email_subject: str
    email_body: str
    linkedin_note: str
    personalisation_signals: list[str]


@dataclass
class OnboardingRecord:
    status: str
    workspace_id: Optional[str]
    systems_to_configure: list[str]
    setup_tasks: list[str]
    owner: str
    blockers: list[str]
    next_step: str


@dataclass
class MarketingBrief:
    audience_segment: str
    competitor_analysis: list[str]
    content_strategy: list[str]
    visual_strategy: list[str]
    communication_strategy: list[str]
    historical_models_used: list[str]
    recommended_track: str


class SirclesState(TypedDict):
    raw_lead: dict
    enriched_contact: Optional[dict]
    enriched_company: Optional[dict]
    icp_score: Optional[float]
    lead_intelligence_position: Optional[AgentPosition]
    devil_advocate_position: Optional[AgentPosition]
    debate_record: Optional[DebateRecord]
    final_disposition: Optional[Disposition]
    outreach_draft: Optional[OutreachDraft]
    crm_record: Optional[CRMRecord]
    onboarding_record: Optional[OnboardingRecord]
    marketing_brief: Optional[MarketingBrief]
    trace: list[str]
    needs_human_review: bool
    human_review_reason: str
