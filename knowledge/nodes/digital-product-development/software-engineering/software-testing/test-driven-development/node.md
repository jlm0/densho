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
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=26
broader:
  - software-testing
---

## Definition

A way to write code in which a test comes before the code that makes it pass. Kent Beck states the canon in 5 steps: write a list of the test scenarios, turn exactly one item on the list into a concrete and runnable test, change the code to make that test and all earlier tests pass, optionally refactor, and go back to the second step until the list is empty. Martin Fowler sums up the core as red, green, refactor.

## Directives

- Before you change a behavior, write a list of the test scenarios that the change needs. ^write-the-test-list
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- List each variant of the new behavior and each existing behavior that the change puts at risk. ^list-variants-and-risks
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Do not put an implementation design decision in the test list. ^no-design-in-test-list
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Write exactly `1` item of the test list as a runnable test before you change the code. ^one-test-at-a-time
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Do not write tests for the whole test list before the first test passes. ^no-speculative-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Write the first test of a behavior from its interface, before you decide its implementation. ^test-the-interface-first
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Do not write a test without an assertion. ^no-test-without-assertion
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Before you change the code, confirm that each new test fails. ^see-the-test-fail
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Write production code only to make a failing test pass. ^code-only-for-a-failing-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Change the code until the new test and each earlier test pass. ^make-all-tests-pass
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Do not delete an assertion to make a test pass. ^keep-the-assertions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Do not copy a value that the code computes into the expected value of its test. ^no-copied-expected-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Do not refactor while you make a failing test pass. ^green-before-refactor
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- When you find a new case during a step, add it to the test list. ^add-new-cases-to-the-list
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- If a new case invalidates the earlier work, start over with a different test order. ^restart-in-a-new-order
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Mark each item of the test list as done when its test passes. ^mark-passing-items
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- After each test passes, refactor the new code and the old code to keep a clean structure. ^refactor-after-green
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Do not refactor beyond the needs of the current test list. ^limit-the-refactor
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Treat a duplication as a hint to abstract, not as a command. ^duplication-is-a-hint
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Choose as the next test the one that leads fastest to a key point of the design. ^choose-the-next-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestDrivenDevelopment.html
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Repeat the cycle from the second step until the test list is empty. ^repeat-until-the-list-is-empty
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://tidyfirst.substack.com/p/canon-tdd
- Keep each test of the cycle as an automated regression test. ^keep-tdd-tests
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=26

## Notes

The cycle has 5 steps, and each step has its own failure mode that Kent Beck names:

1. The test list holds the behavior variants of the change. The mistake is to mix in implementation decisions.
2. One test becomes concrete, with its setup, its invocation, and its assertions. The mistakes are a test without assertions, and a test for each item of the list at once.
3. The code changes until each test passes. The mistakes are a deleted assertion, an expected value copied from the code, and a refactor mixed into this step.
4. An optional refactor improves the implementation design. The mistakes are a refactor beyond the session and an abstraction that comes too soon.
5. The cycle repeats until the list is empty.

Red, green, refactor names steps 2 to 4: the new test fails, the code makes it pass, and the refactor cleans the code. Martin Fowler names 2 benefits: self-testing code, and a focus on the interface before the implementation. He names the skipped refactor as the most common way to fail at the practice.

The ISTQB Foundation Level syllabus puts test-driven development next to acceptance test-driven development and behavior-driven development. All 3 write the tests before the code. Acceptance test-driven development derives its tests from the acceptance criteria, and acceptance testing in software quality holds its rules. Specification by example in software requirements holds the Given, When, Then form of behavior-driven development.

The test pyramid sets the level of each test in the list. Test doubles replace the dependencies that a unit test of the cycle does not run.
