---
id: end-to-end-testing
kind: densho:Concept
title: End-to-end testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/articles/practical-test-pyramid.html#End-to-endTests
  - https://abseil.io/resources/swe-book/html/ch14.html
  - https://abseil.io/resources/swe-book/html/ch11.html#test_scope
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=123
broader:
  - software-testing
---

## Definition

A test that checks the whole system, with each of its parts integrated, through the interface that its users use. The ISTQB Foundation Level syllabus calls this level system testing: it checks the overall behavior and capabilities of the whole system, often with functional tests of end-to-end tasks. Martin Fowler also calls it a broad stack test. Software Engineering at Google calls these tests large-scoped tests: they validate the interaction of distinct parts of the system, or emergent behavior that no single class or method shows.

## Directives

- Build each large test from a system under test, its seeded data, the actions, and the verification. ^large-test-structure
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#structure_of_a_large_test
- Add a large test for each risk that small tests miss, such as configuration, load, or an unfaithful double. ^large-test-for-each-gap
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#common_gaps_in_unit_tests
- Test the deployment configuration of each service with a large test. ^test-deployment-configuration
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#configuration_issues
- Prefer a hermetic system under test over a shared staging environment for a large test. ^hermetic-large-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#the_benefits_of_hermetic_suts
- Run the system tests in a test environment that represents the production environment. ^representative-system-test-environment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29
- If a broad test does not check the user interface, run it through the API below the user interface. ^subcutaneous-broad-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestPyramid.html
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#RestApiEnd-to-endTest
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#reducing_the_size_of_your_sut_at_proble
- In a large test, wait for each state change with a polling loop and a timeout, not a sleep. ^wait-by-polling
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#speeding_up_tests
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#driving_out_flakiness
- Make each timeout and delay of the production code configurable for the large tests. ^configurable-timeouts
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#speeding_up_tests
- If a large test is slow, replace it with smaller tests that run in parallel. ^split-slow-large-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#speeding_up_tests
- Give each large test a failure message that names the test, the expected result, and the actual result. ^large-test-failure-message
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#making_tests_understandable
- Record a trace of each request across the processes of a large test. ^trace-large-test-requests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#making_tests_understandable
- Give each large test a documented owner who reviews its changes and supports its failures. ^own-each-large-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#owning_large_tests
- Run the large tests of a service before each deployment to production. ^large-tests-before-deploy
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#conclusion-id00018

## Notes

Software Engineering at Google names the gaps that unit tests leave, and each gap is a reason for a large test:

- A test double that does not behave like the real dependency.
- A configuration file, a flag, or a deployment setting that the code reads at run time.
- A behavior that appears only under load.
- An input or a behavior that the author of the unit tests did not expect.
- An emergent behavior of the whole system.

A large test has 4 parts: the system under test, the seeded data, the actions, and the verification. A hermetic system under test runs in isolation from production and from a shared staging environment, so other users do not change its results. A system under test with fewer parts is faster and less flaky. A test that drives both the user interface and the backend is costly to keep. Software Engineering at Google splits such a test at the boundary between the user interface and the public API.

End-to-end tests are slow, and they fail for reasons outside the code, such as timing and browser quirks. The test pyramid limits them to the core user journeys. Performance testing and acceptance testing also run against the whole system. Performance testing holds the rules for load. Acceptance testing in software quality holds the rules that check the requirements of the users.
