---
id: software-delivery-metrics
kind: densho:Concept
title: Software delivery metrics
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://dora.dev/guides/dora-metrics/
broader:
  - software-operations
---

## Definition

The five measures of software delivery performance from the DORA research program. Change lead time, deployment frequency, and failed deployment recovery time measure throughput. Change fail rate and deployment rework rate measure instability.

## Directives

- Measure the delivery metrics of one application or service at a time. ^measure-one-service-at-a-time
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://dora.dev/guides/dora-metrics/
- Do not compare the delivery metrics of one team with the metrics of another team. ^no-team-comparison
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://dora.dev/guides/dora-metrics/

## Metrics

| Metric                          | What it measures                                                        |
| ------------------------------- | ----------------------------------------------------------------------- |
| Change lead time                | The time from a commit to the change running in production              |
| Deployment frequency            | How often a team deploys                                                |
| Failed deployment recovery time | The time to recover from a deployment that needs immediate intervention |
| Change fail rate                | The share of deployments that need a rollback or a hotfix               |
| Deployment rework rate          | The share of deployments that are unplanned and that an incident causes |

DORA warns that a metric used as a target invites gaming. A team uses the metrics together to track its own improvement over time.
