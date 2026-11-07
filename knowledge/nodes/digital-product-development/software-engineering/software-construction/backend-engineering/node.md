---
id: backend-engineering
kind: densho:PracticeArea
title: Backend engineering
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf
  - https://martinfowler.com/bliki/ParallelChange.html
broader:
  - software-construction
pointers:
  - kind: densho:TextPointer
    target: data-modeling
    trigger: You define the entities and the relationships of a data store.
  - kind: densho:TextPointer
    target: expand-and-contract
    trigger: You make a breaking change to a schema or an interface.
---

## Definition

The services, the business logic, and the data stores behind a product. Here, the backend lane models the data of each service and changes a schema or an interface without downtime.
