---
id: lifecycle
kind: ka:Concept
title: Lifecycle
status: proposed
origin: template
knowledge_type: domain
broader:
  - governance
governs:
  - root
  - lifecycle
---

## Definition

The states of a node, a directive, or an exception. `proposed` means that an author recommends it and no reviewer approved it. `accepted` means that a reviewer approved this content. `deprecated` means that it stays only for reference.

## Directives

- Set `status` to `proposed` on each new node, directive, and exception. ^start-as-proposed
  - scope: node
  - status: proposed
  - origin: template
- Treat a `proposed` directive as a draft, not as a rule. ^proposed-is-a-draft
  - scope: node
  - status: proposed
  - origin: template
- Follow a directive while its exception stays `proposed`. ^proposed-exception-stops-nothing
  - scope: node
  - status: proposed
  - origin: template
- Do not apply a `deprecated` node or directive to new work. ^deprecated-is-for-reference
  - scope: node
  - status: proposed
  - origin: template
- Before you deprecate a node, move the nodes under it. ^move-before-deprecating
  - scope: node
  - status: proposed
  - origin: template
- Before you remove an `accepted` node or directive, set its `status` to `deprecated`. ^deprecate-before-removing
  - scope: node
  - status: proposed
  - origin: template
- Keep the `id` of a node or a directive when you move its file. ^keep-the-id
  - scope: node
  - status: proposed
  - origin: template
- Do not change the `origin` of a node or a directive. ^keep-the-origin
  - scope: node
  - status: proposed
  - origin: template
- Set `origin` to `project` on each entity in workspace knowledge. ^workspace-is-project
  - scope: node
  - status: proposed
  - origin: template
