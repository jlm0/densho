---
id: design-systems
kind: densho:PracticeArea
title: Design systems
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://atomicdesign.bradfrost.com/chapter-2/
  - https://www.designtokens.org/glossary/
  - https://v1.lightningdesignsystem.com/design-tokens/
  - https://atlassian.design/components/eslint-plugin-design-system/ensure-design-token-usage/usage
broader:
  - ui-ux-design
informs:
  - software-design
pointers:
  - kind: densho:TextPointer
    target: design-tokens
    trigger: You name, store, or reference a color, a size, a space, or a type style.
  - kind: densho:TextPointer
    target: atomic-design
    trigger: You build, combine, or test the components of a design system.
---

## Definition

A shared set of design decisions, components, and patterns, with the rules for their use, that the people who design and build a product draw on. Design tokens store the decisions, such as colors and sizes. Components combine into larger components, layouts, and screens.

## Directives

- Use a design token, not a hard-coded value, for each color and each space in a component. ^use-tokens-not-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://v1.lightningdesignsystem.com/design-tokens/
  - sources: https://atlassian.design/components/eslint-plugin-design-system/ensure-design-token-usage/usage
