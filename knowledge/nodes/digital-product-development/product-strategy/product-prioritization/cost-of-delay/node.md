---
id: cost-of-delay
kind: ka:Concept
title: Cost of delay
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://blackswanfarming.com/cost-of-delay/
  - https://blackswanfarming.com/cost-of-delay-divided-by-duration/
  - https://blackswanfarming.com/urgency-profiles/
broader:
  - product-prioritization
---

## Definition

The value that a team loses for each unit of time that it delivers an item late. Joshua Arnold, after Donald Reinertsen, defines it as the rate at which the total expected value changes with time, so it combines value and urgency. CD3, cost of delay divided by duration, orders the work of a team with limited capacity so that the total cost of delay stays as low as possible. CD3 is one form of weighted shortest job first. The urgency profile of an item describes how its value rises and falls over time, and whether a late delivery lowers its peak.

## Directives

- State the cost of delay of each item as an amount of money for each unit of time. ^cost-per-unit-of-time
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://blackswanfarming.com/cost-of-delay/
- When the time of one team limits the work, order the items by cost of delay divided by duration. ^order-by-cd3
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://blackswanfarming.com/cost-of-delay-divided-by-duration/
- Name the urgency profile of each item. ^name-urgency-profile
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://blackswanfarming.com/urgency-profiles/
- For an item with an external deadline, set its start date to the deadline minus its duration. ^start-before-deadline
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://blackswanfarming.com/urgency-profiles/

## Notes

The urgency profiles are a short life cycle with a peak that falls when the item is late, a long life cycle with a peak that falls when the item is late, a long life cycle with a peak that does not fall, and an external deadline. Before an external deadline, the cost of delay is zero.

In Arnold's example, an order by CD3 cuts the total cost of delay of three features by 61% against the order in which they arrived. A rough estimate of duration is enough. The cost of delay matters more.
