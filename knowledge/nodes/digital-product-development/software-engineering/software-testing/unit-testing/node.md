---
id: unit-testing
kind: densho:Concept
title: Unit testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://abseil.io/resources/swe-book/html/ch12.html
  - https://martinfowler.com/articles/practical-test-pyramid.html#UnitTests
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=122
broader:
  - software-testing
---

## Definition

A test that checks one unit of the code in isolation from the rest of the system. The ISTQB Foundation Level syllabus calls this level component testing, and states that developers normally run these tests in their development environments. SWEBOK v4 defines the unit as an element of the system under test that is separately testable, such as a subprogram, a component, or a subsystem. Software Engineering at Google calls unit tests narrow-scoped tests: each one validates the logic of a small, focused part of the code, such as one class or one method.

## Directives

- In a unit test, replace each dependency that uses a network, a disk, or another process with a test double. ^unit-test-in-one-process
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#small_tests
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#MockingAndStubbing
- Write a separate test for each behavior of a unit, not `1` test for each method. ^test-each-behavior
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#test_behaviorscomma_not_methods
- Limit each unit test to `1` behavior. ^one-behavior-per-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#structure_tests_to_emphasize_behaviors
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#WritingCleanTestCode
- Test each non-trivial code path of a unit, including the happy path and each edge case. ^unit-test-each-code-path
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#WhatToTest
- Test the response of a unit to the common errors that its dependencies return. ^unit-test-each-error
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#testing_for_failure
- Name each unit test after the action that it takes and the outcome that it requires. ^name-after-the-behavior
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#name_tests_after_the_behavior_being_tes
- Put each fact that explains the result of a test in the body of the test. ^complete-test-body
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#make_your_tests_complete_and_concise
- Move each construction detail that does not affect the result into a helper. ^concise-test-body
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#make_your_tests_complete_and_concise
- Build each test value with a helper that takes only the fields that the test depends on. ^test-value-helpers
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#shared_values
- Use a setup method to build the object under test and its collaborators with default values. ^setup-for-defaults
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#shared_setup
- If a test depends on a value from the setup method, set that value in the test body. ^state-setup-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#shared_setup
- Limit each validation helper to `1` conceptual fact about its inputs. ^one-fact-per-validation-helper
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#shared_helpers_and_validation
- Write each failure message with the expected outcome, the actual outcome, and the inputs that produced them. ^clear-failure-messages
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#write_clear_failure_messages
- Do not move a step of a test into shared code that hides what the test does. ^damp-over-dry
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#tests_and_code_sharing_dampcomma_not_dr
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#WritingCleanTestCode
- Change an existing unit test only when the required behavior of the system changes. ^change-tests-only-for-behavior
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#strive_for_unchanging_tests
- If a private method needs its own test, move it into a new class with a public interface. ^extract-private-method
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#private-methods-sidebar
- If a pure refactor breaks a unit test, make the test use the public API. ^refactor-breaks-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#strive_for_unchanging_tests
  - sources: https://testdesiderata.com/
- Make the result of each unit test independent of the order in which the tests run. ^order-independent-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html#LackOfIsolation
  - sources: https://testdesiderata.com/
- Treat shared test infrastructure as a separate product with its own tests. ^test-infrastructure-as-product
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#defining_test_infrastructure
- Run the unit tests in the development environment. ^run-in-development-environment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29

## Notes

The Practical Test Pyramid names 2 kinds of unit test. A solitary unit test replaces each collaborator of the unit with a test double. A sociable unit test keeps the real collaborators. The default tree prefers real collaborators, and the test doubles concept holds that rule.

Software Engineering at Google separates the size of a test from its scope. A small test runs in one process, and most unit tests are small. The rules for clear unit tests follow from one goal: a test that never changes unless the requirements change. A pure refactor, a new feature, and a bug fix leave the existing tests as they are. Only a change of the required behavior changes a test.

Each test has a given part, a when part, and a then part. The practice area holds the rule for this structure, the rule to test through the public interface, and the rule against logic in tests, so that each test level applies them. Test-driven development writes unit tests one at a time.
