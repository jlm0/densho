---
id: product-measurement
kind: densho:PracticeArea
title: Product measurement
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://research.google.com/pubs/archive/36299.pdf
  - https://www.svpg.com/the-alternative-to-roadmaps/
broader:
  - product-strategy
informs:
  - product-discovery
pointers:
  - kind: densho:TextPointer
    target: north-star-metric
    trigger: You choose the one metric that a product team works to move.
  - kind: densho:TextPointer
    target: objectives-and-key-results
    trigger: You write objectives and key results for a team or a company.
  - kind: densho:TextPointer
    target: heart-framework
    trigger: You measure the user experience of a product or a feature.
---

## Definition

Choosing the goals, the metrics, and the targets that show whether a product or a feature succeeds. A metric helps only when it tracks progress toward a goal. Product teams measure outcomes, the change in what users do or feel, rather than output, the amount of work that the team ships.

## Directives

- Link each metric to the goal that it tracks. ^metric-tracks-a-goal
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.google.com/pubs/archive/36299.pdf#page=3
- Normalize each raw count to a ratio, a percentage, or an average for each user, unless it counts new users. ^normalize-raw-counts
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.google.com/pubs/archive/36299.pdf#page=4

## Notes

A raw count grows with the user base, so it can rise while each user does less. Rodden and her colleagues also note that a rise in page views can mean that a feature is popular, or that a confusing interface makes users click around to escape. Metrics add to user research and do not replace early research.
