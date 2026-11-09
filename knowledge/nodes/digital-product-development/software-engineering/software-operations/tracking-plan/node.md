---
id: tracking-plan
kind: densho:Concept
title: Tracking plan
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://amplitude.com/docs/data/create-tracking-plan
  - https://docs.mixpanel.com/docs/tracking-best-practices/tracking-plan
broader:
  - software-operations
informs:
  - product-measurement
---

## Definition

A document that defines each product event and each property that a product collects, why it collects each one, and which source emits it. Amplitude advises a team to build it before it instruments the code, so that analysts, product managers, and engineers work from one schema. Mixpanel builds it from the key metrics, maps them to user flows, and turns the flows into events and properties.
