# OFFICINA Architecture

OFFICINA is an AI-native operational framework for cost-aware, multi-model software development and small-business workflows.

The architecture is designed around a simple principle:

> use the cheapest reliable model for routine work, and escalate to premium models only when operational consequence requires it.

## Architectural Goals

OFFICINA aims to provide:

* model routing by role, capability, cost, and risk;
* operational continuity across sessions;
* safe tool orchestration;
* local/free-first execution where possible;
* premium-model escalation for high-consequence work;
* human confirmation for persistent, destructive, external, or irreversible actions;
* retrieval-based context reconstruction;
* reproducible human-AI software development workflows.

## High-Level Architecture

```text
User / Developer
      ↓
OFFICINA Interface
      ↓
Task Classifier
      ↓
Risk Assessment
      ↓
Capability Router
      ↓
Model Runtime
      ↓
Tool Orchestration
      ↓
Validation Layer
      ↓
Operational Ledger
      ↓
Continuity / Retrieval
```

## Main Components

### 1. OFFICINA Interface

The interface is the human entry point into the system.

It may include:

* chat-based interaction;
* developer console;
* dashboard;
* task view;
* model/runtime status;
* ledger visibility;
* tool confirmation prompts.

The interface should make AI actions visible and understandable to the human operator.

### 2. Task Classifier

The task classifier identifies the type of user request.

Example task types:

* summarization;
* coding;
* research;
* ledger extraction;
* tool invocation;
* architecture decision;
* document processing;
* administrative workflow;
* troubleshooting;
* adversarial review.

The classifier should be lightweight and may use a low-cost or local model.

### 3. Risk Assessment

The risk layer determines the operational consequence of the task.

Example risk levels:

* low: reversible, local, non-persistent;
* medium: modifies generated artifacts or draft state;
* high: affects code, ledger, external systems, credentials, data, or decisions;
* critical: destructive, irreversible, security-sensitive, financial, legal, or production-impacting.

High-risk and critical actions require stronger models and human confirmation.

### 4. Capability Router

The capability router selects the appropriate model based on the task.

It considers:

* reasoning capability;
* coding ability;
* tool-use support;
* structured output reliability;
* context length;
* cost;
* latency;
* availability;
* privacy requirements;
* risk tolerance.

The router should choose a role, not a hardcoded provider.

Example roles:

* director;
* implementer;
* summarizer;
* extractor;
* router;
* validator;
* adversarial reviewer;
* local fallback.

### 5. Model Runtime

The model runtime manages provider and model execution.

Supported model categories may include:

* local models;
* open-source models;
* low-cost API models;
* premium reasoning models;
* premium coding models;
* embedding models;
* rerankers.

The runtime should support fallback behavior when a model fails, exceeds cost limits, lacks a capability, or produces invalid output.

### 6. Tool Orchestration

The tool layer connects models to external capabilities.

Possible tools include:

* GitHub;
* filesystem;
* database;
* browser;
* MCP servers;
* APIs;
* shell commands;
* document processors;
* evaluation tools.

Tools must have capability and risk profiles.

Destructive, persistent, external, or irreversible tool actions require human confirmation.

### 7. Validation Layer

The validation layer checks outputs before they become operationally consequential.

Validation may include:

* schema validation;
* structured output checks;
* tool argument validation;
* diff review;
* test execution;
* ledger admissibility checks;
* adversarial review;
* human approval.

The validation layer helps prevent weak model output from becoming persistent system state.

### 8. Operational Ledger

The operational ledger is the canonical continuity substrate of OFFICINA.

It stores stabilized operational crystallizations, not raw conversation history.

The ledger should preserve:

* decisions;
* constraints;
* current system state;
* validated policies;
* next executable actions;
* important transitions;
* operational consequences.

The ledger should avoid preserving:

* discarded hypotheses;
* raw brainstorming;
* redundant summaries;
* temporary reasoning;
* procedural scaffolding;
* unvalidated assumptions.

### 9. Continuity and Retrieval

OFFICINA should reconstruct context from relevant sources instead of sending all available context to every model call.

Relevant context may come from:

* operational ledger;
* codebase;
* documentation;
* recent task state;
* user-provided files;
* database records;
* prior validated outputs.

The goal is to reduce context cost while preserving reconstructability.

## Model Escalation Strategy

OFFICINA follows a free/local-first strategy.

Routine tasks should use:

* local models;
* open-source models;
* low-cost API models;
* cached outputs;
* retrieval-based context minimization.

Premium models should be reserved for:

* architecture decisions;
* complex coding;
* code validation;
* adversarial review;
* high-risk tool use;
* long-context reasoning;
* ledger-critical updates;
* security-sensitive workflows.

## Human-in-the-Loop Policy

The human operator must remain in control of high-consequence actions.

Human confirmation is required before:

* deleting files;
* modifying canonical ledger state;
* changing production configuration;
* exposing credentials;
* making external API calls with side effects;
* applying irreversible code changes;
* executing financial, legal, or security-sensitive actions.

## Operational Continuity Model

OFFICINA distinguishes between:

* exploration;
* working cognition;
* extraction pressure;
* stabilized operational crystallization.

Only stabilized operational crystallizations should become persistent operational state.

This preserves continuity without polluting memory or inflating context.

## MDI+

OFFICINA follows MDI+:

> maximum operational reconstructability under minimum admissible persistence.

This means the system should preserve only what is operationally necessary while keeping enough structure for future agents, tools, and humans to reconstruct the state of the project.

## Initial Implementation Direction

The initial implementation should prioritize:

1. runtime package skeleton;
2. model capability profiles;
3. simple task classifier;
4. risk assessment rules;
5. routing policy;
6. operational ledger schema;
7. tool-use validation rules;
8. evaluation scenarios;
9. examples and documentation.

## Long-Term Architecture Direction

Over time, OFFICINA may evolve into:

* a runtime core package;
* a developer dashboard;
* a model/provider catalog;
* a tool registry;
* a ledger and retrieval subsystem;
* a coding workflow engine;
* a small-business workflow framework;
* a human-AI operational control layer.
