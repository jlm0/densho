---
id: software-requirements
kind: densho:PracticeArea
title: Software requirements
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
  - https://www.iso.org/standard/72089.html
broader:
  - software-engineering
informs:
  - software-architecture
pointers:
  - kind: densho:TextPointer
    target: spike
    trigger: A technical question blocks the specification of a change.
  - kind: densho:TextPointer
    target: specification-by-example
    trigger: You write the acceptance scenarios of a change.
  - kind: densho:TextPointer
    target: requirements-traceability
    trigger: You map each requirement of a change to its tests.
---

## Definition

The discovery, the specification, and the validation of what a system must do, before the team builds it. SWEBOK `v4` makes software requirements its first knowledge area. ISO/IEC/IEEE 29148 is the standard for requirements engineering in the life cycle of systems and software.

## Notes

In specification by example, each requirement becomes a set of examples, and each example becomes a test.
