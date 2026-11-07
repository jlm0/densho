---
id: heart-framework
kind: densho:Concept
title: HEART framework
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/
  - https://research.google.com/pubs/archive/36299.pdf
broader:
  - product-measurement
---

## Definition

Five categories of user-centered metrics from Kerry Rodden, Hilary Hutchinson, and Xin Fu at Google, published at CHI 2010. Happiness covers attitudes such as satisfaction and perceived ease of use. Engagement is the level of involvement, such as visits per user per week. Adoption counts the new users in a period. Retention counts the users of one period who still use the product in a later period. Task success covers efficiency, effectiveness, and the error rate. The Goals-Signals-Metrics process states the goals first, then the signals in behavior or attitude that show success, then the metrics to track. HEART adds to the PULSE metrics of product health: page views, uptime, latency, seven-day active users, and earnings.

## Directives

- State for each HEART category whether the product uses it. ^choose-heart-categories
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.google.com/pubs/archive/36299.pdf
- Write the goal of each HEART category before its signals and its metrics. ^goal-before-metric
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.google.com/pubs/archive/36299.pdf
- Choose signals that change only when the user experience changes. ^specific-signals
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.google.com/pubs/archive/36299.pdf
- Report each engagement metric as an average for each user, not as a total. ^engagement-per-user
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.google.com/pubs/archive/36299.pdf

## Notes

Not every category fits every product. Engagement can mean little in an enterprise tool that people must use for work, while it still matters for one feature. The goals of a feature can differ from the goals of the whole product. Logs and surveys are the usual sources of signals, and failure is sometimes easier to see than success, for example in abandoned tasks or "undo" events.

Gmail measured engagement as the share of active users who visited on five or more days in the last week, and found that it predicted long-term retention.
