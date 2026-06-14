"""Mock tools and fixtures. No live APIs are called."""

from datetime import datetime
import random
import string


CONTACT_FIXTURES = {
    "alex.chen@growthsaas.io": {
        "first_name": "Alex",
        "last_name": "Chen",
        "title": "Head of Revenue Operations",
        "email": "alex.chen@growthsaas.io",
        "linkedin": "linkedin.com/in/alexchen",
        "seniority": "director",
        "phone_verified": True,
        "employment_history": ["Salesforce (3yr)", "HubSpot (2yr)"],
        "skills": ["CRM", "Sales Enablement", "RevOps", "HubSpot"],
    },
    "sara.malik@solofrelancer.dev": {
        "first_name": "Sara",
        "last_name": "Malik",
        "title": "Freelance Web Developer",
        "email": "sara.malik@solofrelancer.dev",
        "linkedin": "linkedin.com/in/saradev",
        "seniority": "individual_contributor",
        "phone_verified": False,
        "employment_history": ["Self-employed (5yr)"],
        "skills": ["React", "Node.js"],
    },
    "james.obi@nexusagency.co": {
        "first_name": "James",
        "last_name": "Obi",
        "title": "Growth Marketing Director",
        "email": "james.obi@nexusagency.co",
        "linkedin": "linkedin.com/in/jamesobi",
        "seniority": "director",
        "phone_verified": True,
        "employment_history": ["Nexus Agency (4yr)", "Ogilvy (2yr)"],
        "skills": ["Digital Marketing", "SEO", "Paid Media", "Client Strategy"],
    },
    "priya.nair@ambiguouscorp.com": {
        "first_name": "Priya",
        "last_name": "Nair",
        "title": "VP of Marketing",
        "email": "priya.nair@ambiguouscorp.com",
        "linkedin": "linkedin.com/in/priyanair",
        "seniority": "vp",
        "phone_verified": True,
        "employment_history": ["AmbiguousCorp (2yr)", "Unilever (3yr)"],
        "skills": ["Brand Strategy", "Community Marketing", "CRM"],
    },
}


COMPANY_FIXTURES = {
    "growthsaas.io": {
        "name": "GrowthSaaS",
        "domain": "growthsaas.io",
        "industry": "B2B SaaS",
        "headcount": 85,
        "headcount_range": "51-200",
        "funding_stage": "Series B",
        "funding_amount_usd": 18_000_000,
        "founded_year": 2019,
        "hiring_signals": ["SDR", "Account Executive", "Marketing Manager"],
        "tech_stack": ["HubSpot", "Salesforce", "Intercom", "Segment"],
        "revenue_range": "$5M-$20M",
        "is_competitor": False,
        "notes": "Strong ICP match. Active hiring in sales.",
    },
    "solofrelancer.dev": {
        "name": "Sara Malik (Freelancer)",
        "domain": "solofrelancer.dev",
        "industry": "Freelance / Consulting",
        "headcount": 1,
        "headcount_range": "1",
        "funding_stage": "Bootstrapped",
        "funding_amount_usd": 0,
        "founded_year": 2018,
        "hiring_signals": [],
        "tech_stack": ["WordPress", "Figma"],
        "revenue_range": "<$100K",
        "is_competitor": False,
        "notes": "Solo operator, no budget signals, wrong profile entirely.",
    },
    "nexusagency.co": {
        "name": "Nexus Agency",
        "domain": "nexusagency.co",
        "industry": "B2B SaaS",
        "headcount": 62,
        "headcount_range": "51-200",
        "funding_stage": "Series A",
        "funding_amount_usd": 4_500_000,
        "founded_year": 2016,
        "hiring_signals": ["SDR", "Head of Marketing", "Content Strategist"],
        "tech_stack": ["HubSpot", "Salesforce", "Segment"],
        "revenue_range": "$2M-$8M",
        "is_competitor": True,
        "notes": "Strong fit signals, but a direct competing agency.",
    },
    "ambiguouscorp.com": {
        "name": "AmbiguousCorp",
        "domain": "ambiguouscorp.com",
        "industry": "Consumer Goods",
        "headcount": 120,
        "headcount_range": "51-200",
        "funding_stage": "Series A",
        "funding_amount_usd": 7_000_000,
        "founded_year": 2020,
        "hiring_signals": ["Marketing Coordinator"],
        "tech_stack": ["Mailchimp", "Shopify"],
        "revenue_range": "$1M-$5M",
        "is_competitor": False,
        "notes": "Some fit signals but weak tech stack and limited hiring momentum.",
    },
}


ICP_CRITERIA = {
    "ideal_industries": ["B2B SaaS", "Tech Startup", "MarTech", "Community Platform"],
    "ideal_headcount_min": 20,
    "ideal_headcount_max": 500,
    "ideal_funding_stages": ["Seed", "Series A", "Series B", "Series C"],
    "ideal_seniority": ["manager", "director", "vp", "c_suite"],
    "positive_signals": ["HubSpot", "Salesforce", "hiring SDR", "hiring marketing"],
}


MARKETING_PLAYBOOK = {
    "models": [
        "ICP-to-message fit matrix",
        "community-led growth adoption curve",
        "competitor-risk positioning checklist",
    ],
    "segments": {
        "B2B SaaS": {
            "track": "RevOps community growth",
            "content": [
                "benchmark post on community-sourced pipeline",
                "case-study email on scaling engagement after Series A/B",
                "webinar invite for RevOps and marketing leaders",
            ],
            "visuals": [
                "pipeline velocity chart",
                "community engagement flywheel",
                "CRM-to-community workflow diagram",
            ],
        },
        "Consumer Goods": {
            "track": "brand community nurture",
            "content": [
                "brand loyalty teardown",
                "retention-focused community checklist",
                "email sequence around customer advocacy",
            ],
            "visuals": [
                "customer lifecycle map",
                "advocacy funnel",
                "campaign moodboard using product/community moments",
            ],
        },
        "default": {
            "track": "low-touch education",
            "content": [
                "introductory thought-leadership email",
                "lightweight community maturity checklist",
            ],
            "visuals": ["simple maturity scorecard"],
        },
    },
}


def fetch_new_leads() -> list[dict]:
    """Mock lead scanner."""
    return [
        {
            "email": "alex.chen@growthsaas.io",
            "domain": "growthsaas.io",
            "source": "website_form",
            "label": "clear_pursue",
        },
        {
            "email": "sara.malik@solofrelancer.dev",
            "domain": "solofrelancer.dev",
            "source": "cold_outbound",
            "label": "clear_skip",
        },
        {
            "email": "james.obi@nexusagency.co",
            "domain": "nexusagency.co",
            "source": "linkedin",
            "label": "ambiguous_competitor",
        },
        {
            "email": "priya.nair@ambiguouscorp.com",
            "domain": "ambiguouscorp.com",
            "source": "referral",
            "label": "escalation_case",
        },
    ]


def enrich_contact(email: str) -> dict:
    """Mock Apollo/Clay contact enrichment."""
    result = CONTACT_FIXTURES.get(
        email,
        {
            "first_name": "Unknown",
            "last_name": "Contact",
            "title": "Unknown",
            "email": email,
            "seniority": "unknown",
            "phone_verified": False,
            "employment_history": [],
            "skills": [],
        },
    )
    return {"source": "apollo_mock", "data": result, "enriched_at": datetime.now().isoformat()}


def enrich_company(domain: str) -> dict:
    """Mock Apollo/Clay company enrichment."""
    result = COMPANY_FIXTURES.get(
        domain,
        {
            "name": "Unknown Company",
            "domain": domain,
            "industry": "Unknown",
            "headcount": 0,
            "funding_stage": "Unknown",
            "is_competitor": False,
            "hiring_signals": [],
            "tech_stack": [],
        },
    )
    return {"source": "clay_mock", "data": result, "enriched_at": datetime.now().isoformat()}


def upsert_crm_record(record: dict) -> dict:
    """Mock HubSpot CRM upsert."""
    deal_id = "DEAL-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return {
        "success": True,
        "deal_id": deal_id,
        "contact_id": "CT-" + record.get("email", "unknown").split("@")[0].upper(),
        "message": f"Record upserted successfully. Deal ID: {deal_id}",
        "timestamp": datetime.now().isoformat(),
    }


def provision_onboarding_workspace(contact: dict, company: dict) -> dict:
    """Mock Sircles system provisioning."""
    workspace_id = "WS-" + company.get("domain", "unknown").replace(".", "-").upper()
    return {
        "workspace_id": workspace_id,
        "systems": ["Sircles workspace", "HubSpot lifecycle list", "CSM handoff board"],
        "provisioned_at": datetime.now().isoformat(),
    }


def fetch_sircles_marketing_playbook() -> dict:
    """Mock retrieval of Sircles historical campaign models."""
    return MARKETING_PLAYBOOK


def score_icp(contact_data: dict, company_data: dict) -> dict:
    """Score a lead against the ICP and return the evidence breakdown."""
    score = 0.0
    signals = []
    penalties = []

    contact = contact_data.get("data", {})
    company = company_data.get("data", {})

    if company.get("industry") in ICP_CRITERIA["ideal_industries"]:
        score += 0.25
        signals.append(f"Industry match: {company.get('industry')}")
    else:
        penalties.append(f"Industry mismatch: {company.get('industry')}")

    headcount = company.get("headcount", 0)
    if ICP_CRITERIA["ideal_headcount_min"] <= headcount <= ICP_CRITERIA["ideal_headcount_max"]:
        score += 0.15
        signals.append(f"Headcount in range: {headcount}")
    else:
        penalties.append(f"Headcount out of range: {headcount}")

    if company.get("funding_stage") in ICP_CRITERIA["ideal_funding_stages"]:
        score += 0.20
        signals.append(f"Funding stage: {company.get('funding_stage')}")
    else:
        penalties.append(f"Funding stage not ideal: {company.get('funding_stage')}")

    if contact.get("seniority") in ICP_CRITERIA["ideal_seniority"]:
        score += 0.20
        signals.append(f"Seniority: {contact.get('seniority')}")
    else:
        penalties.append(f"Seniority too low: {contact.get('seniority')}")

    tech_overlap = [
        tech for tech in company.get("tech_stack", []) if tech in ICP_CRITERIA["positive_signals"]
    ]
    if tech_overlap:
        score += 0.10
        signals.append(f"Tech stack overlap: {', '.join(tech_overlap)}")

    hiring = company.get("hiring_signals", [])
    if hiring:
        score += 0.10
        signals.append(f"Hiring signals: {', '.join(hiring[:2])}")

    if company.get("is_competitor"):
        score -= 0.30
        penalties.append("COMPETITOR FLAG: company is a direct competitor")

    if headcount < 10:
        score -= 0.20
        penalties.append("Too small: headcount < 10")

    return {
        "icp_score": round(max(0.0, min(1.0, score)), 3),
        "positive_signals": signals,
        "penalties": penalties,
        "is_competitor": company.get("is_competitor", False),
    }
