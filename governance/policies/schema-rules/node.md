---
id: schema-rules
kind: ka:Concept
title: Schema rules
status: proposed
origin: template
knowledge_type: domain
sources:
  - governance/schema/metamodel.yaml
broader:
  - governance
governs:
  - root
  - schema-rules
---

## Definition

The rules for the metamodel, which defines what a node is. The metamodel file stays outside the graph, so this node names it as a source.

## Directives

- Change a node kind, a field, or an edge only in `governance/schema/metamodel.yaml`. ^change-the-schema-file
  - scope: node
  - status: proposed
  - origin: template
- Do not edit a file in `engine/knowledge_architecture/generated/` by hand. ^keep-the-generated-files
  - scope: node
  - status: proposed
  - origin: template
