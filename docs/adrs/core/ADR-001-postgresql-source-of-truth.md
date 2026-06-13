# ADR-001 — PostgreSQL as Source of Truth

## Status

Accepted

---

## Context

Officina requires:

- persistent operational continuity;
- structured retrieval;
- governance outside the LLM;
- durable operational memory;
- and reproducible state management.

Conversational context alone is insufficient as operational memory because:

- chat context is ephemeral;
- provider-dependent;
- non-structured;
- and non-authoritative.

A persistent external operational state is required.

---

## Decision

PostgreSQL is adopted as the canonical operational source of truth for Officina.

PostgreSQL will persist:

- projects;
- tasks;
- documents;
- workflows;
- execution records;
- operational relationships;
- metadata;
- and future semantic references.

The LLM is NOT considered authoritative storage.

The conversational layer acts only as:

- orchestration interface;
- reasoning layer;
- and execution copilot.

Operational state lives outside the model.

---

## Consequences

### Positive

- durable operational memory;
- structured retrieval;
- relational governance;
- transactional consistency;
- local-first persistence;
- provider independence;
- and future extensibility.

### Negative

- schema governance becomes necessary;
- migrations become operational concerns;
- persistence discipline is required;
- and operational modeling complexity increases over time.

---

## Strategic Impact

This decision operationalizes the principle:

> The AI does not organize the system.
> The system organizes the AI.

It also establishes the foundation for:

- conversational independence;
- operational continuity;
- hybrid retrieval;
- execution persistence;
- and governance outside the LLM.

---