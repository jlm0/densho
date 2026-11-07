---
id: root
kind: ka:Root
title: Knowledge architecture
status: proposed
origin: template
pointers:
  - kind: ka:TextPointer
    target: digital-product-development
    trigger: You plan, design, or build a digital product.
  - kind: ka:PathPointer
    target: governance
    trigger: You change a node file.
    paths:
      - knowledge/**/*
---

## Directives

- When a person corrects your work, propose the change with `propose-knowledge`. ^propose-corrections
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template

## Architecture

- A pointer or an edge carries meaning. A folder path only helps navigation, so a file can move and keep its meaning.
- Domain knowledge is universal. Workspace knowledge belongs to one project. One schema, one set of checks, and one workflow cover both.
- An agent can propose a node, a directive, or an exception. Only a person accepts one.
- The governance rules are nodes too. They follow their own rules, and the same checks read them.
- A project owns its copy of this graph, and its copy can differ from the template.
