---
id: software-design
kind: densho:PracticeArea
title: Software design
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
broader:
  - software-engineering
informs:
  - software-testing
pointers:
  - kind: densho:TextPointer
    target: interface-contract
    trigger: You define or change the API or the events of a service.
  - kind: densho:TextPointer
    target: ui-contract
    trigger: You define the states and the inputs of an interface component.
---

## Definition

The definition of the parts of a system and of the interfaces between them, at a level of detail that lets a team build and test each part on its own. SWEBOK `v4` makes software design a knowledge area next to software architecture.

## Notes

The output of this area is a set of contracts: the interface contract of each API and the UI contract of each component. Software testing and software construction take the contracts as their input.
