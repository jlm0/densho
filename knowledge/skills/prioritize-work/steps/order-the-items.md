---
title: Order the items
pages:
  - target: product-prioritization
    trigger: You set the order of the items in a backlog or a roadmap.
  - target: rice-scoring
    trigger: You score items by reach, impact, confidence, and effort.
directives:
  - state-user-problem
  - reach-per-period
  - reach-from-metrics
  - estimated-reach-confidence
  - impact-scale
  - confidence-scale
  - effort-in-person-months
  - rice-formula
  - order-by-rice-score
  - dependencies-first
missing_rules:
  - No directive of prioritization requires the goal, the timeframe, and the capacity before the order.
  - No directive of prioritization chooses the method for items with deadlines.
---

## Procedure

1. Collect the items to order: features, projects, or requirements.
2. State the goal that the order serves, the timeframe, and the capacity of the team.
3. Collect the reach, the impact, the confidence, and the effort of each item.
4. Mark each value that rests on an estimate and not on data.
5. Compute the RICE score of each item.
6. Sort the items by score.
7. Check the order against dependencies and commitments to customers.
8. Write the reason for each item that leaves its place in the score order.

## Output

The items in their final order, each with its values, its score, and the reason for each move.
