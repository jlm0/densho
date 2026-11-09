---
id: architecture-style
kind: densho:Concept
title: Architecture style
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/MonolithFirst.html
broader:
  - software-architecture
informs:
  - integration-style
---

## Definition

The overall form of a system, such as one deployable monolith or a set of services.

## Notes

Martin Fowler reports that almost every successful microservice system started as a monolith that grew too big and was split. Almost every system that he heard of that started as microservices ended up in serious trouble. Microservices carry a premium, the cost of managing a suite of services, that pays off only for complex systems. A monolith first, with modular boundaries, lets a team find the right boundaries before it splits out a service.
