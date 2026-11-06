---
id: schema-rules
kind: ka:Concept
title: Schema rules
status: proposed
origin: template
knowledge_type: domain
sources:
  - knowledge/governance/schema/metamodel.yaml
broader:
  - governance
governs:
  - root
  - schema-rules
---

## Definition

The rules for the metamodel, which defines what a node is. The metamodel file stays outside the graph, so this node names it as a source.

## Directives

- Change a node kind, a field, or an edge only in `knowledge/governance/schema/metamodel.yaml` of the template. ^change-the-schema-file
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not edit a file in `engine/generated/` by hand. ^keep-the-generated-files
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
