---
id: software-construction
kind: densho:PracticeArea
title: Software construction
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
broader:
  - software-engineering
informs:
  - software-configuration-management
pointers:
  - kind: densho:TextPointer
    target: infrastructure-engineering
    trigger: You define where a service runs or how it deploys.
  - kind: densho:TextPointer
    target: backend-engineering
    trigger: You build a service, its logic, or its data store.
  - kind: densho:TextPointer
    target: frontend-engineering
    trigger: You build the web client of a product.
  - kind: densho:TextPointer
    target: native-engineering
    trigger: You build a native mobile app.
---

## Definition

The detailed creation of working software through code and its verification. SWEBOK `v4` makes software construction a knowledge area.

## Directives

- Write each code comment to explain why the code exists, not what it does. ^comments-explain-why
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: code-review
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html

## Notes

Construction takes the contracts of software design as its input. It has 4 lanes: infrastructure, backend, frontend, and native. The lanes can run in parallel.
