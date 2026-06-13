# OFFICINA Repository Map

This document maps the current OFFICINA repository structure and explains how the existing components relate to the long-term runtime architecture.

## Current Repository Structure

OFFICINA is currently organized around several technical areas:

- `db/` — database-related artifacts and PostgreSQL work.
- `fastapi/` — backend API experiments and service layer.
- `react/` — frontend interface work.
- `agents/` — agent-related concepts and workflows.
- `mcp/` — Model Context Protocol oriented integrations.
- `scripts/` — utility scripts and operational tooling.
- `cognition/` — operational cognition, ledger, continuity, and project state.
- `docs/` — architecture, application brief, roadmap, and project documentation.

## Runtime Relationship

The long-term OFFICINA runtime will coordinate these components through a cost-aware model execution layer.

The intended runtime responsibilities include:

- selecting models by role, capability, cost, and risk;
- coordinating coding, reasoning, summarization, and validation workflows;
- orchestrating tools and external integrations;
- preserving operational continuity through the ledger;
- reconstructing relevant context without sending unnecessary full-history payloads;
- escalating to premium models only when operational consequence requires it.

## Existing Code and Artifacts

The current repository already contains early implementation and planning artifacts across backend, frontend, database, agent, MCP, and cognition areas.

The next development step is not to invent a separate artificial package, but to progressively connect the existing components into a coherent runtime.

## Near-Term Integration Priorities

1. Identify the minimal backend service boundary.
2. Define the first model routing configuration.
3. Connect operational ledger read/write helpers.
4. Define the first tool-use evaluation workflow.
5. Establish a small coding workflow that can be tested with Codex.
6. Document which tasks require premium models and which can use local or low-cost alternatives.

## Relationship to `officina`

A clean runtime-core component is being prepared separately at:

https://github.com/officina-systems/officina

That repository is intended to become a reusable extraction of the runtime concepts developed inside the broader OFFICINA framework.
