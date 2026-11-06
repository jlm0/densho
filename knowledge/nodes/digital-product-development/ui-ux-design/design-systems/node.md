---
id: design-systems
kind: ka:PracticeArea
title: Design systems
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://atomicdesign.bradfrost.com/chapter-2/
  - https://www.designtokens.org/glossary/
broader:
  - ui-ux-design
informs:
  - software-engineering
pointers:
  - kind: ka:TextPointer
    target: design-tokens
    trigger: You name, store, or reference a color, a size, a space, or a type style.
  - kind: ka:TextPointer
    target: atomic-design
    trigger: You build, combine, or test the components of a design system.
---

## Definition

A shared set of design decisions, components, and patterns, with the rules for their use, that the people who design and build a product draw on. Design tokens store the decisions, such as colors and sizes. Components combine into larger components, layouts, and screens.

## Directives

- Use a design token, not a raw value, for each color, size, and space in a component. ^use-tokens-not-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/glossary/
