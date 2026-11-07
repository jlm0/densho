---
id: service-level-objective
kind: densho:Concept
title: Service level objective
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://sre.google/sre-book/service-level-objectives/
  - https://sre.google/workbook/implementing-slos/
broader:
  - software-reliability
---

## Definition

A target value or range for a service level indicator (SLI). An SLI is a measure of one aspect of the service that users get, such as latency, the error rate, or availability. A service level agreement (SLA) is a contract that adds a consequence, such as a refund, when the service misses its SLO. A target with no consequence is an SLO, not an SLA.

## Directives

- Define each SLI as the ratio of good events to all events. ^sli-as-ratio
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/workbook/implementing-slos/
- Choose each SLI from what users experience, not from what is easy to measure. ^user-centered-sli
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/service-level-objectives/
- Measure latency at a percentile, not as a mean. ^latency-percentiles
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/service-level-objectives/
- Do not set an SLO target of `100%`. ^no-perfect-slo
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/embracing-risk/
  - sources: https://sre.google/sre-book/service-level-objectives/
- Set the internal SLO of a service tighter than its published SLO. ^internal-slo-margin
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/service-level-objectives/
- Prefer a rolling window of `4` weeks for an SLO. ^four-week-window
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/workbook/implementing-slos/

## Notes

A mean hides the slow tail of a latency distribution. The `99th` percentile shows a likely worst case, and the `50th` percentile shows the typical case. Start with a loose target and tighten it over time, not with a strict target that you relax later.
