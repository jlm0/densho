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
