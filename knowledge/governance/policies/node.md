---
id: governance
kind: densho:Domain
title: Governance
status: proposed
origin: template
knowledge_type: domain
governs:
  - root
  - governance
  - lifecycle
  - approval
  - change-rules
  - language-rules
  - schema-rules
pointers:
  - kind: densho:TextPointer
    target: lifecycle
    trigger: You set the `status` of an entity.
  - kind: densho:TextPointer
    target: approval
    trigger: You accept a change.
  - kind: densho:TextPointer
    target: change-rules
    trigger: You change an accepted entity.
  - kind: densho:TextPointer
    target: language-rules
    trigger: You write a directive, a trigger, or a skill description.
  - kind: densho:TextPointer
    target: schema-rules
    trigger: You change a node kind, a field, or an edge.
---

## Definition

The rules that set how knowledge enters the graph and how it changes. They cover domain knowledge and workspace knowledge alike, and they cover themselves.

## Directives

- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Do not use `--no-verify` on a commit. ^keep-the-hook
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
