---
id: contract-testing
kind: densho:Concept
title: Contract testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/ContractTest.html
  - https://martinfowler.com/articles/consumerDrivenContracts.html
broader:
  - software-testing
---

## Definition

A test that checks that a test double still behaves like the external service that it stands for. Martin Fowler describes contract tests as checks that each call against a test double returns the same results as a call to the external service. Ian Robinson's consumer-driven contracts invert the direction: each consumer states what it expects of a provider, and the contract of the provider is the union of these expectations.
