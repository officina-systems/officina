# OFFICINA

OFFICINA is an AI-native operational runtime for small business systems.

It is designed to help small teams build, operate, and evolve business software using a practical combination of:

- multi-model AI routing;
- tool-aware workflows;
- PostgreSQL-backed operational memory;
- FastAPI services;
- React interfaces;
- MCP-compatible integration surfaces;
- local and cloud model providers;
- explicit operational continuity.

OFFICINA is not a single chatbot. It is a framework for building business-facing AI systems where models, tools, data, workflows, and human decisions remain operationally traceable.

## Current Scope

This repository contains the public framework snapshot of OFFICINA.

It includes:

- fastapi/ — backend runtime services, routers, provider abstraction, chat and document flows;
- react/ — frontend interface for AI-native operational work;
- db/ — PostgreSQL schema foundations;
- mcp/ — MCP/PostgreSQL integration work;
- docs/ — architecture notes, application brief, roadmap and design records;
- scripts/ — public-safe local operation helpers;
- agents/ — early agent components;
- opencode/ — development environment integration.

## Design Direction

OFFICINA is built around the idea that small businesses need systems that can:

- preserve operational context;
- route work across different AI models;
- connect tools safely;
- maintain continuity across sessions;
- expose auditable workflows;
- support open-source and cost-aware model alternatives;
- avoid vendor lock-in where possible.

## Framework Concepts

OFFICINA uses a graph-oriented operational model:

- nodes represent operational entities, documents, tasks, sessions, tools, models, users or business objects;
- edges represent relationships, dependencies, decisions, transitions or workflow movement;
- the runtime retrieves and updates only the context needed for the current operation.

This avoids treating the whole company as one large undifferentiated knowledge base.

## Status

OFFICINA is under active development.

This public repository is intended to provide:

- technical evidence of the framework direction;
- a public foundation for funding and startup program applications;
- a clean open-source surface for future collaboration.

Private runtime data, secrets, credentials, local state, and internal operational cognition are intentionally excluded.

## Public Links

Website: https://officina.ioblu.com
Repository: https://github.com/officina-systems/officina
Contact: officina@ioblu.com
