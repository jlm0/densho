---
id: test-driven-development
kind: densho:Concept
title: Test-driven development
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://tidyfirst.substack.com/p/canon-tdd
  - https://martinfowler.com/bliki/TestDrivenDevelopment.html
broader:
  - software-testing
---

## Definition

A way to write code in which a test comes before the code that makes it pass. Kent Beck states the canon in 5 steps: write a list of the test scenarios, turn exactly one item on the list into a concrete and runnable test, change the code to make that test and all earlier tests pass, optionally refactor, and go back to the second step until the list is empty. Martin Fowler sums up the core as red, green, refactor.
