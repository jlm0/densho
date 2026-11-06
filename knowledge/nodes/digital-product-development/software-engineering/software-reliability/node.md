---
id: software-reliability
kind: ka:PracticeArea
title: Reliability
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://sre.google/sre-book/monitoring-distributed-systems/
broader:
  - software-engineering
pointers:
  - kind: ka:TextPointer
    target: service-level-objective
    trigger: You set a reliability target for a service.
  - kind: ka:TextPointer
    target: error-budget
    trigger: You plan a release of a service that has an SLO.
  - kind: ka:TextPointer
    target: postmortem
    trigger: You write the record of an incident.
---

## Definition

The ability of a service to do what its users expect, at the level that they expect, over time. Site reliability engineering, from Google, measures reliability against a target and uses the gap between the target and perfection to decide how fast the service changes.

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
- Prefer an alert on a symptom that users see over an alert on its cause. ^alert-on-symptoms
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
