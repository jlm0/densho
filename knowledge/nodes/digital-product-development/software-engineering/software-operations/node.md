---
id: software-operations
kind: densho:PracticeArea
title: Software operations
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
  - https://martinfowler.com/bliki/ContinuousDelivery.html
  - https://sre.google/sre-book/monitoring-distributed-systems/
broader:
  - software-engineering
informs:
  - product-measurement
pointers:
  - kind: densho:TextPointer
    target: continuous-delivery
    trigger: You release or deploy a change.
  - kind: densho:TextPointer
    target: observability
    trigger: You add logs, metrics, or traces to a service.
  - kind: densho:TextPointer
    target: tracking-plan
    trigger: You add or change a product analytics event.
  - kind: densho:TextPointer
    target: service-level-objective
    trigger: You set a reliability target for a service.
  - kind: densho:TextPointer
    target: error-budget
    trigger: You plan a release of a service that has an SLO.
  - kind: densho:TextPointer
    target: postmortem
    trigger: You write the record of an incident.
  - kind: densho:TextPointer
    target: software-delivery-metrics
    trigger: You measure how a team delivers software.
---

## Definition

The release, the monitoring, and the running of software in production. SWEBOK `v4` adds software engineering operations as a knowledge area. Reliability is one of its concerns: the ability of a service to do what its users expect, at the level that they expect, over time. Site reliability engineering, from Google, measures reliability against a target and uses the gap between the target and perfection to decide how fast the service changes.

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

## Notes

The four golden signals measure the time to serve a request, the demand on the service, the rate of failed requests, and how full the most constrained resource is. A problem that needs only a mechanical response gets automation, not a page.
