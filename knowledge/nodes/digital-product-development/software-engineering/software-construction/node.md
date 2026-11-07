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

The detailed creation of working software through code and its verification. SWEBOK `v4` makes software construction a knowledge area. Here, construction builds to the contracts of software design, in 4 lanes that can run in parallel: infrastructure, backend, frontend, and native.
