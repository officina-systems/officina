# ADR-003 — Conversational Shell Architecture

## Status

Accepted

---

## Context

Traditional conversational AI systems frequently couple:

- interface;
- cognition;
- memory;
- orchestration;
- and operational state

inside a single chat-centric runtime.

This creates several limitations:

- provider dependency;
- ephemeral continuity;
- weak operational persistence;
- limited governance;
- and fragile context reconstruction.

Officina instead separates:

- operational persistence;
- governance;
- cognitive providers;
- execution capabilities;
- and conversational interfaces.

---

## Decision

Officina adopts a conversational shell architecture.

The conversational layer is treated as:

- an operational interface;
- orchestration surface;
- and cognitive interaction shell.

The conversational interface itself is NOT considered:

- the operational memory;
- the system identity;
- nor the authoritative runtime state.

Operational continuity must instead be reconstructed from persistent artifacts and operational storage.

---

## Architectural Implications

Conversational interfaces become interchangeable.

Potential interfaces may include:

- Open WebUI;
- terminal environments;
- IDE integrations;
- desktop applications;
- APIs;
- messaging platforms;
- voice interfaces;
- and automation runtimes.

The underlying operational system remains independent from any specific interface.

---

## Cognitive Provider Model

LLMs are treated as cognitive providers rather than sovereign system entities.

Cognitive capabilities may eventually be orchestrated across:

- local runtimes;
- external providers;
- specialized reasoning models;
- coding models;
- retrieval-aware systems;
- and execution-capable runtimes.

---

## Explicit Non-Goals

This architecture does NOT imply:

- AGI;
- unrestricted autonomy;
- swarm intelligence;
- generalized self-awareness;
- or unconstrained autonomous agents.

Officina remains a governed cognitive-operational system.

---

## Strategic Impact

This decision reinforces:

> Persistence outside the chat.

> Governance outside the LLM.

> The system organizes the AI.

The conversational interface becomes an operational shell rather than the system itself.

---

## Open WebUI

Open WebUI constituye la implementación operacional inicial del conversational shell de Officina.

Su rol es:

- interfaz conversacional;
- shell operacional;
- capa UX;
- entorno contextual de interacción humano-modelo;
- y runtime multi-modelo desacoplado.

Open WebUI NO constituye:

- source of truth;
- governance authority;
- workflow authority;
- ni persistence layer principal.

La continuidad operacional, governance, retrieval estructurado y estado operacional permanecen en Officina y PostgreSQL.
