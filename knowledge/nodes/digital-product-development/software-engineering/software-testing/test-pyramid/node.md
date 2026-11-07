---
id: test-pyramid
kind: densho:Concept
title: Test pyramid
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/TestPyramid.html
  - https://martinfowler.com/articles/practical-test-pyramid.html
  - https://martinfowler.com/bliki/IntegrationTest.html
  - https://abseil.io/resources/swe-book/html/ch11.html
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=50
broader:
  - software-testing
---

## Definition

A model for the mix of automated tests in a suite, by the level of each test. Mike Cohn's original pyramid has 3 layers: unit tests at the wide base, service tests in the middle, and tests through the user interface at the narrow top. The ISTQB Foundation Level syllabus states the model in general terms: the higher the layer, the lower the granularity and the isolation of its tests, and the longer they run. So a suite holds many small, fast tests at the base and few broad tests at the top.

## Directives

- Write most automated tests as unit tests. ^mostly-unit-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Add a contract test for each interface between two services. ^contract-test-each-service-interface
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#ContractTests
- Limit end-to-end tests to the key steps of the user journeys that give the product its core value. ^end-to-end-core-journeys
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#End-to-endTests
- Test user interface behavior with unit tests of the frontend code and a test double of the backend. ^unit-test-ui-behavior
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#UiTests
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Define in the team the name and the scope of each kind of test. ^agree-on-test-names
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#TheConfusionAboutTestingTerminology
- Test each behavior at the lowest level of the pyramid that detects its failure. ^test-at-lowest-level
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#AvoidTestDuplication
- Write each test at the smallest size that checks its behavior, by its use of processes and machines. ^smallest-test-size
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#test_size
- Run the fastest tests in the earliest stage of the deployment pipeline. ^fast-tests-first
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#PuttingTestsIntoYourDeploymentPipeline
- Limit each higher-level test to the part that the lower-level tests do not cover. ^higher-test-covers-the-gap
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#AvoidTestDuplication
- If a broad test fails and no unit test fails, add a unit test for the fault. ^add-missing-unit-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#AvoidTestDuplication
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- If lower-level tests cover each condition of a higher-level test, delete the higher-level test. ^delete-duplicate-high-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#AvoidTestDuplication
- If the high-level tests of a behavior are fast, reliable, and cheap to change, skip its lower-level tests. ^skip-low-tests-for-cheap-high-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Do not keep a recorded test as recorded, unless you edit it as code. ^no-record-playback-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Do not use large tests as the main way to find bugs. ^large-tests-are-not-the-net
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#test_scope
- If a suite holds more end-to-end tests than unit tests, move its checks down the pyramid. ^fix-ice-cream-cone
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#test_scope
- If a suite holds unit tests and end-to-end tests but few integration tests, add integration tests. ^fix-test-hourglass
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#test_scope
- Check that each layer of the suite holds fewer tests than the layer below it. ^check-pyramid-shape
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#TheTestPyramid
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=50

## Notes

The layers of the pyramid are the test levels, and each level has its own concept with the rules to write its tests:

- Unit testing checks one unit in isolation. ISTQB calls it component testing.
- Integration testing checks the interfaces between parts. A narrow integration test checks one integration point with test doubles for the rest.
- Contract testing checks that a test double still behaves like the real service.
- End-to-end testing checks the whole system through its user interface or through the API just below it.

The names differ from source to source, so a team states its own. A UI test is not the same as an end-to-end test: a test of the user interface can be a unit test with the backend replaced. This concept holds only the rules for the mix of tests across the levels.

Software Engineering at Google adds a second dimension. The size of a test is the resource that it uses: a small test runs in one process, a medium test on one machine, and a large test across machines. The scope of a test is the amount of code that it validates. Narrow scope and small size go together often, but not always. Google gives a rough mix of `80%` unit tests, `15%` integration tests, and `5%` end-to-end tests, by count. The mix of each team varies.

2 shapes show a suite that drifts from the pyramid. An ice cream cone holds many end-to-end tests and few unit tests. An hourglass holds many unit tests and many end-to-end tests, with few integration tests between them.

Test-driven development writes most of the unit tests. Performance testing is one kind of large test.
