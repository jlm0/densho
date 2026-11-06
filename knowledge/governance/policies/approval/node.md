---
id: approval
kind: ka:Concept
title: Approval
status: proposed
origin: template
knowledge_type: domain
broader:
  - governance
governs:
  - root
  - approval
---

## Definition

The step that takes knowledge from a proposal to a rule. An agent can propose a concept, a directive, or an exception. A person approves it or rejects it.

## Directives

- Do not set `status` to `accepted` unless a person approves the change. ^person-accepts
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not set `status` to `deprecated` unless a person approves the change. ^person-deprecates
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not set `status` to `rejected` unless a person rejects the proposal. ^person-rejects
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Run `uv run ka governance --pending` to list each proposal. ^list-the-proposals
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Read the reason of each exception before you accept it. ^read-the-reason
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Run `uv run ka directives --at` on the node before you accept a directive. ^read-what-applies
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
