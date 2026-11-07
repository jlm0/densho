---
id: continuous-delivery
kind: densho:Concept
title: Continuous delivery
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/ContinuousDelivery.html
broader:
  - software-operations
informs:
  - observability
---

## Definition

A discipline in which a team builds software so that it can be released to production at any time. Martin Fowler names the signs: the software is deployable throughout its life, the team keeps it deployable before it works on new features, each change gets fast automated feedback on its readiness for production, and a push-button deployment sends any version to any environment. A deployment pipeline carries each change toward production.
