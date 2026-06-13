# OFFICINA — MASTER SPECIFICATION

## Propósito

Este documento define el mapa arquitectónico y operacional maestro de Officina.

Su objetivo es:

- preservar coherencia sistémica;
- evitar drift arquitectónico;
- distinguir núcleo operacional de exploración futura;
- permitir evolución incremental disciplinada;
- y mantener continuidad conceptual sin inflar complejidad prematuramente.

Este documento NO representa:

- roadmap de implementación;
- prioridades temporales;
- estado real de implementación;
- ni secuencia evolutiva.

Representa:

- alcance conceptual;
- arquitectura canónica;
- estado de madurez;
- clasificación operacional;
- y dirección arquitectónica.

---

# Clasificación de Estados

| Estado | Significado |
|---|---|
| Canonizado | Definido oficialmente como parte de Officina |
| Definido | Existe especificación suficientemente clara |
| Parcial | Existe parcialmente |
| Exploratorio | Idea válida aún no estabilizada o no apta para Seed |
| Pendiente | Reconocido pero no diseñado |
| Post-Seed | Intencionalmente diferido para etapas posteriores |

---

# Regla de Canonización

Un componente no puede pasar a Canonizado sin:

- uso operacional validado;
- beneficio operacional observable;
- compatibilidad con KISS estructural;
- y coherencia con governance.

---

# 1. Filosofía y Governance

| Componente | Estado |
|---|---|
| PostgreSQL como source of truth | Canonizado |
| Query before RAG | Canonizado |
| Governance outside the LLM | Canonizado |
| Persistencia fuera del chat | Canonizado |
| Chat como orchestration layer | Canonizado |
| Operational state first | Canonizado |
| Incrementalismo | Canonizado |
| Anti-premature abstraction | Canonizado |
| Local-first philosophy | Definido |
| Model replaceability | Canonizado |
| Trazabilidad operacional | Definido |
| Artifact persistence | Definido |
| Reversibilidad operacional | Definido |
| Continuidad operacional | Definido |
| Anti-complexity governance | Definido |

---

# 2. Núcleo Arquitectónico

| Componente | Estado |
|---|---|
| Operational Database | Canonizado |
| Operational Graph | Definido |
| Execution Layer | Definido |
| Governance Layer | Definido |
| Workflow Engine | Parcial |
| Capability System | Parcial |
| Artifact Registry | Parcial |
| Operational State Management | Parcial |
| Semantic Graph | Exploratorio |
| Event Model | Exploratorio |
| Runtime Coordination Layer | Exploratorio |
| Distributed Runtime | Post-Seed |

---

# 3. Canonical Entities

| Entidad | Estado |
|---|---|
| Projects | Definido |
| Tasks | Definido |
| Documents | Definido |
| Sources | Definido |
| Workflows | Parcial |
| Executions | Parcial |
| Conversations | Parcial |
| Decisions / ADRs | Definido |
| Artifacts | Parcial |
| Operational Relationships | Parcial |
| Capabilities | Parcial |
| Knowledge Objects | Exploratorio |
| Agents | Exploratorio |
| Ontology Objects | Exploratorio |

---

# 4. Retrieval Architecture

| Componente | Estado |
|---|---|
| SQL-first retrieval | Canonizado |
| Relationship traversal | Definido |
| Hybrid retrieval | Definido |
| Semantic retrieval | Definido |
| Deep source retrieval | Parcial |
| WWW augmentation | Definido |
| Specialized APIs | Definido |
| Retrieval orchestration pipeline | Parcial |
| Context assembly | Pendiente |
| Provenance tracking | Parcial |
| Freshness policy | Pendiente |
| Ranking strategy | Pendiente |
| Semantic expansion policy | Exploratorio |
| Ontology-assisted retrieval | Exploratorio |

---

# 5. Execution System

| Componente | Estado |
|---|---|
| Workflow execution | Parcial |
| Capability execution | Parcial |
| Execution persistence | Parcial |
| Execution logging | Definido |
| Artifact generation | Parcial |
| Retry model | Exploratorio |
| Scheduling | Exploratorio |
| Approval model | Exploratorio |
| Async execution | Exploratorio |
| Self-modifying workflows | Exploratorio |
| Autonomous execution agents | Exploratorio |
| Generalized planning system | Exploratorio |

---

# 6. Datasource Layer

| Componente | Estado |
|---|---|
| Datasource adapters | Definido |
| Unified adapter contract | Pendiente |
| PostgreSQL adapter | Parcial |
| Filesystem adapter | Parcial |
| Git adapter | Pendiente |
| Gmail adapter | Exploratorio |
| Drive adapter | Exploratorio |
| API adapters | Exploratorio |
| Sync model | Pendiente |
| Watchers | Exploratorio |
| Change tracking | Exploratorio |
| Cross-source linking | Exploratorio |

---

# 7. Knowledge & Semantic Layer

| Componente | Estado |
|---|---|
| pgvector integration | Definido |
| Embedding storage | Parcial |
| Semantic indexing | Parcial |
| Hybrid search | Definido |
| Semantic graph | Exploratorio |
| Taxonomy layer | Exploratorio |
| Dictionary system | Exploratorio |
| Concept registry | Exploratorio |
| Ontology system | Exploratorio |
| Semantic reasoning | Exploratorio |

---

# 8. Interfaces

| Componente | Estado |
|---|---|
| Open WebUI operational shell | Definido |
| Conversational orchestration | Definido |
| FastAPI backend | Parcial |
| CLI interface | Exploratorio |
| Operational dashboard | Exploratorio |
| Admin UI | Exploratorio |
| Multi-user interface | Post-Seed |
| Mobile interface | Post-Seed |

Open WebUI constituye el shell operacional inicial de Officina.

Su responsabilidad es:

- interacción conversacional;
- contexto operativo humano-modelo;
- runtime multi-modelo;
- y UX operacional.

La continuidad operacional, governance, retrieval y persistence permanecen desacopladas en Officina y PostgreSQL.

---

# 9. Persistence & Governance

| Componente | Estado |
|---|---|
| Markdown persistence | Definido |
| Git integration | Parcial |
| ADR system | Definido |
| Schema versioning | Pendiente |
| Operational lineage | Exploratorio |
| Auditability | Parcial |
| Permission model | Exploratorio |
| Backup strategy | Pendiente |
| Multi-user governance | Post-Seed |
| Policy engine | Exploratorio |

---

# 10. Infrastructure

| Componente | Estado |
|---|---|
| PostgreSQL | Definido |
| pgvector | Definido |
| FastAPI | Definido |
| Ollama | Definido |
| Open WebUI | Definido |
| n8n | Definido |
| Dockerization | Pendiente |
| Observability | Exploratorio |
| Deployment topology | Exploratorio |
| Distributed infrastructure | Post-Seed |

---

# 11. AI Runtime

| Componente | Estado |
|---|---|
| Local inference | Definido |
| Model abstraction | Canonizado |
| Provider abstraction | Canonizado |
| Hybrid cognition | Definido |
| Context orchestration | Parcial |
| Cognitive routing layer | Exploratorio |
| Prompt governance | Exploratorio |
| Long-context strategies | Exploratorio |
| Planner layer | Exploratorio |
| Autonomous agents | Exploratorio |
| Distributed cognition | Exploratorio |

---

# 12. Operational Policies

| Componente | Estado |
|---|---|
| Before create → search | Canonizado |
| Before automate → model | Canonizado |
| Before abstract → simplify | Canonizado |
| Structured persistence | Canonizado |
| Traceable execution | Canonizado |
| Workflow association | Canonizado |
| Project association | Canonizado |
| Artifact persistence policy | Definido |
| Reversible operations preference | Definido |
| Source-of-truth discipline | Canonizado |

---

# 13. Officina Seed

## Objetivo

Construir el núcleo operacional persistente mínimo funcional de Officina.

El Seed NO busca:

- AGI;
- autonomía general;
- swarm systems;
- orchestration universal;
- ni cognición distribuida.

El Seed busca:

- continuidad operacional;
- memoria persistente;
- retrieval híbrido disciplinado;
- workflows básicos;
- execution logging;
- capacidades ejecutables acotadas;
- y organización operacional real.

---

## Seed — Componentes Esperados

| Componente | Estado |
|---|---|
| Persistent projects | Definido |
| Persistent tasks | Definido |
| Persistent documents | Definido |
| Sources registry | Parcial |
| Hybrid retrieval | Parcial |
| Workflow continuity | Parcial |
| Execution logging | Definido |
| Markdown persistence | Definido |
| PostgreSQL persistence | Definido |
| Local execution | Parcial |
| Bounded capabilities | Parcial |
| Conversational orchestration | Definido |

---

# 14. Componentes Fuera del Núcleo Seed

Estos componentes NO se consideran necesarios para validar el núcleo operacional inicial.

Pueden evolucionar posteriormente de forma controlada.

| Componente | Estado |
|---|---|
| Ontology system | Exploratorio |
| Autonomous agents | Exploratorio |
| Generalized planning | Exploratorio |
| Complex graph runtime | Exploratorio |
| Distributed cognition | Exploratorio |
| Advanced orchestration | Exploratorio |
| Multi-user governance | Post-Seed |
| Self-modifying workflows | Exploratorio |

---

# 15. Principio de Disciplina Arquitectónica

Officina NO busca:

- convertirse en framework universal de agentes;
- modelar toda cognición humana;
- reemplazar sistemas operacionales existentes;
- ni abstraer prematuramente toda operación.

Officina busca:

- organizar realidad operacional;
- mantener continuidad;
- estructurar conocimiento operativo;
- ejecutar capacidades gobernadas;
- y permitir evolución incremental disciplinada.

---

# 16. Insight Central

La IA no organiza el sistema.

El sistema organiza la IA.

El LLM:

- razona;
- interpreta;
- propone;
- y ejecuta capacidades.

Pero:

- el estado;
- la memoria;
- la estructura;
- las relaciones;
- los workflows;
- y la gobernanza;

viven fuera del modelo IA.
