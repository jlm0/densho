---
id: rice-scoring
kind: ka:Concept
title: RICE scoring
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
  - https://www.nngroup.com/articles/prioritization-methods/
broader:
  - product-prioritization
related:
  - cost-of-delay
---

## Definition

A prioritization score from Intercom, described by Sean McBride. Reach is the number of people or events that an item affects in a period. Impact is the effect on each person, on a fixed scale. Confidence is the share of support that the team has for its estimates. Effort is the total work of product, design, and engineering, in person-months. The score is reach times impact times confidence, divided by effort. It measures the total impact for each unit of work.

## Directives

- Measure reach as the number of people or events in one fixed period. ^reach-per-period
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Prefer reach figures from product metrics over estimates. ^reach-from-metrics
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Set impact to `3`, `2`, `1`, `0.5`, or `0.25`. ^impact-scale
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Set confidence to `100%`, `80%`, or `50%`. ^confidence-scale
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- State effort in person-months for the whole team, with `0.5` as the minimum. ^effort-in-person-months
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Compute the RICE score as reach times impact times confidence, divided by effort. ^rice-formula
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/

## Notes

The impact scale reads `3` for massive, `2` for high, `1` for medium, `0.5` for low, and `0.25` for minimal. The confidence scale reads `100%` for high, `80%` for medium, and `50%` for low. Intercom calls anything below `50%` a moonshot. Nielsen Norman Group allows `25%` for a wild guess. This node follows Intercom.

Intercom does not treat the score as a hard rule. A dependency, or a feature that a set of customers requires before they buy, can move an item with a lower score first.
