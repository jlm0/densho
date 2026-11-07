<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test-driven development

## Directives

No directive is in force at this node.

## Definition

A way to write code in which a test comes before the code that makes it pass. Kent Beck states the canon in 5 steps: write a list of the test scenarios, turn exactly one item on the list into a concrete and runnable test, change the code to make that test and all earlier tests pass, optionally refactor, and go back to the second step until the list is empty. Martin Fowler sums up the core as red, green, refactor.

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
