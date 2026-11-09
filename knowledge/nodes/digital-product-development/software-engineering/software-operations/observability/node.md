---
id: observability
kind: densho:Concept
title: Observability
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://opentelemetry.io/docs/concepts/observability-primer/
  - https://opentelemetry.io/docs/concepts/signals/
broader:
  - software-operations
informs:
  - tracking-plan
---

## Definition

The ability to understand a system from the outside, by asking questions about it without knowing its inner workings. OpenTelemetry makes a system observable through instrumentation: the code emits signals such as traces, metrics, and logs. A trace is the path of a request through an application, and a metric is a measurement captured at runtime.

## Directives

- Monitor the latency, the traffic, the errors, and the saturation of each user-facing service. ^golden-signals
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/monitoring-distributed-systems/
- Measure the latency of failed requests apart from the latency of successful requests. ^separate-error-latency
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/monitoring-distributed-systems/
- Make each alert detect a symptom that users see, not its cause, unless the cause is definite and imminent. ^alert-on-symptoms
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/monitoring-distributed-systems/
- Send a page only for a problem that needs human judgment at once. ^actionable-pages
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/monitoring-distributed-systems/
