---
id: change-rules
kind: densho:Concept
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

- Set `status` to `proposed` when you change the text, the scope, the basis, or the attachments of an `accepted` directive. ^reopen-a-directive
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Set `status` to `proposed` when you change the definition, the kind, or an edge of an `accepted` node. ^reopen-a-node
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Set `status` to `proposed` when you change the reason of an `accepted` exception. ^reopen-an-exception
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Set `status` to `proposed` when you change the invocation or a script of an `accepted` skill. ^reopen-a-skill
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Keep `status` when you change only a title, a body, a pointer, a source, or a rejection reason. ^routes-need-no-review
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Change only `status` on an entity in the commit that accepts it. ^accept-in-its-own-commit
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
