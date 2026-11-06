---
id: software-testing
kind: ka:PracticeArea
title: Testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/articles/practical-test-pyramid.html
  - https://abseil.io/resources/swe-book/html/ch11.html
broader:
  - software-engineering
pointers:
  - kind: ka:TextPointer
    target: test-pyramid
    trigger: You choose the level of a new test.
---

## Definition

The automated checks that show that code does what it claims, and that keep it doing so as the code changes. A test runs the code with known inputs and compares the result with an expected result.

## Directives

- Before you fix a bug, write a test that reproduces the bug. ^test-before-bug-fix
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Test each unit through its public interface, not through its private methods. ^test-public-interface
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html
- Do not put a conditional or a loop in a test. ^no-logic-in-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html
- Do not hide a flaky test behind an automatic rerun. ^no-rerun-for-flaky-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html
- Split each test into its setup, its action, and its verification. ^setup-action-verification
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html
- Do not write a test for code with no logic, such as a plain getter or setter. ^skip-trivial-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html

## Notes

A flaky test passes and fails on the same code. Software Engineering at Google reports that a suite loses the trust of engineers when about `1%` of its runs are flaky.
