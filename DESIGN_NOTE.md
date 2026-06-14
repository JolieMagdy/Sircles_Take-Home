# Design Note

## Architecture decisions

### Why Propose / Challenge / Resolve

I chose a two-position debate instead of a voting panel because the assignment values visible disagreement. Lead Intelligence is intentionally optimistic about fit, while Devil's Advocate is intentionally skeptical about risk. That makes the ambiguous case easy to inspect: the reviewer can see exactly which argument won, lost, or remained unresolved.

The tradeoff is that two agents can deadlock. The confidence-gap threshold handles that by escalating instead of forcing a false decision.

### Why deterministic scoring

The ICP scorer is deterministic Python. It is easier to test, explain, and defend than a simulated LLM score. In production, an LLM could help write richer rationale, but the core scoring criteria should remain auditable.

### Why shared state

Every agent reads and returns the same `SirclesState`. The orchestrator owns that state and is the only component that decides routing. This keeps handoffs explicit and makes the trace a single append-only story.

### Why CRM always runs

Skipped and escalated leads still matter. A CRM record with a clear disqualification or review reason prevents silent drops, supports suppression lists, and gives future scoring work clean training examples.

### Why lightweight onboarding and marketing artifacts

The assignment includes Onboarding and Marketing Strategy agents, but the core slice is inbound lead to first touch. I implemented realistic lightweight artifacts instead of pretending to provision real systems or run a real RAG workflow. Onboarding prepares setup only when the lead is pursued and records blockers otherwise. Marketing uses a mock Sircles playbook to produce competitor, content, visual, and communication strategy.

## What I would do with two more weeks

1. Add structured LLM calls for richer agent reasoning while keeping deterministic scores as grounding evidence.
2. Move the orchestrator to LangGraph for conditional edges, checkpointing, and human-review resume.
3. Replace mock fixtures with adapters around Apollo/Clay, HubSpot, and an internal Sircles playbook store.
4. Add confidence calibration from closed-won, closed-lost, and skipped lead outcomes.
5. Build a small review UI for escalated leads that shows both positions and lets a human approve the next route.

## Where it breaks at scale

- Volume: the pipeline is sequential and should become queue-backed for high-throughput lead intake.
- ICP drift: scoring criteria are hardcoded and should move to configuration owned with Sales/Marketing.
- Debate quality: the skeptical logic is rule-based, so unusual edge cases may need LLM reasoning or additional risk models.
- Escalation operations: human review needs a queue, owner assignment, and SLA tracking.
- Persistence: state is in memory during a run; production needs durable trace storage and replay.
