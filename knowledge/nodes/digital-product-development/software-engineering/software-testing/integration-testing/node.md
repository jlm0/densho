---
id: integration-testing
kind: densho:Concept
title: Integration testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/IntegrationTest.html
  - https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
  - https://abseil.io/resources/swe-book/html/ch11.html#medium_tests
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=123
broader:
  - software-testing
related:
  - contract-testing
---

## Definition

A test that checks whether parts that are developed separately work correctly when they are connected. The ISTQB Foundation Level syllabus names 2 levels: component integration testing checks the interfaces and the interactions between components, and system integration testing checks the interfaces between the system and other systems or external services. Martin Fowler separates 2 kinds. A narrow integration test runs only the code that talks to a separate service, with a test double of that service. A broad integration test needs live versions of each service.

## Directives

- Write an integration test for each part of the code that serializes or deserializes data at a boundary. ^integration-test-each-boundary
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
- In a narrow integration test, test only the code that calls another service, against a test double of it. ^one-integration-point-per-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/IntegrationTest.html
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
- Add errors and latency to the calls between components in the integration tests. ^integration-test-failures
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#testing_for_failure
- Choose the integration strategy: top-down, bottom-up, sandwich, or big bang. ^choose-integration-strategy
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=123
- In a database integration test, check the written data by reading it back from the database. ^read-back-written-data
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
- In a narrow integration test, run each external dependency locally, unless it is a third-party service with no local version. ^local-integration-dependencies
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
- If a third-party service has no local version, run the integration tests against its dedicated test instance. ^third-party-test-instance
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
- In a narrow integration test, limit the network calls to localhost, unless a third-party service has no local version. ^one-machine-integration-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#medium_tests
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
- If a suite holds only broad integration tests, add narrow integration tests. ^add-narrow-integration-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/IntegrationTest.html
- Run the system integration tests in an environment similar to the operational environment. ^system-integration-environment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=29
- Do not run an integration test against production, unless a contract test has no test instance to target. ^no-tests-against-production
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#IntegrationTests
  - sources: https://martinfowler.com/bliki/ContractTest.html
- Add a contract test for each test double of a service that a narrow integration test uses. ^pair-narrow-test-with-contract
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/IntegrationTest.html

## Notes

The name integration test has more than one meaning, so Martin Fowler looks for the context of each use. Martin Fowler lists 3 uses:

- A narrow integration test runs the code of one service that talks to a database, a file system, a queue, or another service. It uses a test double of the other service, and it often runs in the same test framework as the unit tests.
- A broad integration test runs live versions of each service and exercises code paths through each of them. Martin Fowler prefers the name system test or end-to-end test for it.
- Some writers use the name for a sociable unit test.

Software Engineering at Google calls a test of the interactions between a small number of components a medium-scoped test. A medium test can start several processes and use the network, but only on one machine.

SWEBOK v4 and the ISTQB syllabus name the integration strategies: top-down, bottom-up, mixed or sandwich, and big bang. SWEBOK describes integration as incremental and systematic, by functional thread or by architecture.

A narrow integration test is only as good as its test double. Contract testing checks that each double still behaves like the real service.
