---
id: test-pyramid
kind: ka:Concept
title: Test pyramid
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/TestPyramid.html
  - https://martinfowler.com/articles/practical-test-pyramid.html
  - https://abseil.io/resources/swe-book/html/ch11.html
broader:
  - software-testing
---

## Definition

A model for the mix of automated tests in a suite. Unit tests form the wide base. Service tests, which act through an API or a service layer, form the middle. Tests through the user interface form the narrow top. A test higher in the pyramid covers more of the system, runs slower, and breaks more often for reasons that are not a fault.

## Directives

- Write most automated tests as unit tests. ^mostly-unit-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Test each behavior at the lowest level of the pyramid that detects its failure. ^test-at-lowest-level
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html
- If a broad test fails and no unit test fails, add a unit test for the fault. ^add-missing-unit-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Add a contract test for each interface between two services. ^contract-test-each-service-interface
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html

## Notes

Software Engineering at Google gives a rough mix of `80%` unit tests, `15%` integration tests, and `5%` end-to-end tests, by count. The mix of each team varies.
