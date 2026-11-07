---
id: expand-and-contract
kind: densho:Concept
title: Expand and contract
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/ParallelChange.html
broader:
  - backend-engineering
---

## Definition

A way to make a breaking change to an interface in 3 phases. Martin Fowler also calls it parallel change. In the expand phase, the interface supports both the old and the new version. In the migrate phase, each client moves to the new version. In the contract phase, the old version is removed. Many database refactorings follow the same pattern.
