---
id: integration-style
kind: densho:Concept
title: Integration style
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.enterpriseintegrationpatterns.com/patterns/messaging/IntegrationStylesIntro.html
  - https://martinfowler.com/articles/201701-event-driven.html
broader:
  - software-architecture
informs:
  - c4-model
---

## Definition

The way that separate applications work together. Gregor Hohpe and Bobby Woolf name four integration styles: file transfer, a shared database, remote procedure invocation, and messaging. The choice depends on each point of integration, and one system can use several styles. Martin Fowler separates event notification, in which a system tells other systems of a change in its domain and does not care much about the response, from a command, in which the sender expects the receiver to act.
