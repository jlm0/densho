---
id: change-rules
kind: ka:Concept
title: Change rules
status: proposed
origin: template
knowledge_type: domain
broader:
  - governance
governs:
  - root
  - change-rules
---

## Definition

The rules that say which changes reopen a review. A change to what an agent is told, or to what a node means, reopens it. A change to a route or to supporting text does not.

## Directives

- Set `status` to `proposed` when you change the text, the scope, or the attachments of an `accepted` directive. ^reopen-a-directive
  - scope: node
  - status: proposed
  - origin: template
- Set `status` to `proposed` when you change the definition, the kind, or an edge of an `accepted` node. ^reopen-a-node
  - scope: node
  - status: proposed
  - origin: template
- Set `status` to `proposed` when you change the reason of an `accepted` exception. ^reopen-an-exception
  - scope: node
  - status: proposed
  - origin: template
- Keep `status` when you change only a title, a body, a pointer, or a source. ^routes-need-no-review
  - scope: node
  - status: proposed
  - origin: template
- Change only `status` on an entity in the commit that accepts it. ^accept-in-its-own-commit
  - scope: node
  - status: proposed
  - origin: template
