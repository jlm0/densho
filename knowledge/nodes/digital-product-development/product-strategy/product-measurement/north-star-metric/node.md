---
id: north-star-metric
kind: densho:Concept
title: North star metric
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://amplitude.com/blog/product-north-star-metric
broader:
  - product-measurement
informs:
  - objectives-and-key-results
---

## Definition

The single metric that best captures the value that customers get from a product, in the North Star Framework of Amplitude. It ties the problems that the product team solves to the revenue that the business aims for. A good north star metric reflects customer value, expresses the product strategy, and leads revenue rather than lags it. A set of three to five input metrics, which the team can influence directly, drives it. Amplitude sorts products into three games: attention, transaction, and productivity. The game decides what the north star measures.

## Directives

- Choose one north star metric for each product. ^one-north-star
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://amplitude.com/blog/product-north-star-metric
- Do not use active users or registered users as the north star metric. ^no-user-count-north-star
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://amplitude.com/blog/product-north-star-metric
- Do not use a lagging measure such as revenue as the north star metric. ^leading-north-star
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://amplitude.com/blog/product-north-star-metric
- Choose `3` to `5` input metrics that drive the north star metric and that the team influences. ^north-star-inputs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://amplitude.com/blog/product-north-star-metric

## Notes

Examples from Amplitude are "number of mobile orders delivered" for a retailer and "trial accounts with more than `3` users active in week `1`" for a self-serve SaaS product. Breadth, depth, frequency, and efficiency give a pattern for the inputs. A company with several divisions, each with its own customers and its own profit and loss, can have one north star for each division.
