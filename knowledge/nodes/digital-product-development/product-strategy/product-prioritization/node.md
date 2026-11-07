---
id: product-prioritization
kind: densho:PracticeArea
title: Prioritization
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/prioritization-methods/
  - https://www.svpg.com/the-alternative-to-roadmaps/
broader:
  - product-strategy
pointers:
  - kind: densho:TextPointer
    target: rice-scoring
    trigger: You compare a long list of items for one goal.
  - kind: densho:TextPointer
    target: cost-of-delay
    trigger: You weigh the urgency of items against their value and their duration.
  - kind: densho:TextPointer
    target: kano-model
    trigger: You judge how a feature affects the satisfaction of customers.
  - kind: densho:TextPointer
    target: moscow-prioritization
    trigger: You set the scope of a timebox or a release with a fixed date.
---

## Definition

Deciding the order in which a team works on items when it cannot build everything at once. Each method weighs a mix of value to users, value to the business, urgency, confidence, and effort. Nielsen Norman Group finds no method best in general: the choice depends on the context, the culture of the team, and the success criteria. Marty Cagan warns that a roadmap of features tells a team what to build without the problem that each feature solves.

## Directives

- Give each product team business objectives with key results, not a list of features to build. ^objectives-not-feature-lists
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.svpg.com/the-alternative-to-roadmaps/

## Notes

Cagan keeps two needs that a roadmap serves: work on the most valuable items first, and dates that the business needs. Prioritized business objectives for each team meet the first need. A high-integrity commitment meets the second, for the few cases that need a date.
