---
id: test-doubles
kind: densho:Concept
title: Test doubles
status: proposed
origin: template
knowledge_type: domain
sources:
  - http://xunitpatterns.com/Test%20Double.html
  - https://martinfowler.com/bliki/TestDouble.html
  - https://martinfowler.com/articles/mocksArentStubs.html
  - https://abseil.io/resources/swe-book/html/ch13.html
broader:
  - software-testing
related:
  - contract-testing
---

## Definition

An object that replaces a production object in a test. Gerard Meszaros named the general term after a stunt double, and his xUnit Test Patterns names 5 kinds by their use: a dummy, a stub, a spy, a mock, and a fake. A test double gives the test control over the indirect inputs of the code under test, or a point to observe its indirect outputs, or a faster stand-in for a slow dependency.

## Directives

- Use a dummy only for an argument or an attribute that the code under test never uses. ^dummy-for-unused-arguments
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: http://xunitpatterns.com/Dummy%20Object.html
  - sources: https://martinfowler.com/bliki/TestDouble.html
- Use a stub only to feed the indirect inputs that put the code under test into a needed state. ^stub-for-indirect-inputs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: http://xunitpatterns.com/Test%20Stub.html
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#when_is_stubbing_appropriatequestion_ma
- If no state verification observes an indirect output, verify it with a spy. ^spy-or-mock-for-indirect-outputs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: http://xunitpatterns.com/Test%20Spy.html
  - sources: http://xunitpatterns.com/Mock%20Object.html
- Use a fake for a slow or unavailable dependency whose needed behavior is too complex for stubs and mocks. ^fake-for-slow-dependencies
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: http://xunitpatterns.com/Fake%20Object.html
- Name each test double by its kind: dummy, stub, spy, mock, or fake. ^name-the-double-kind
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/TestDouble.html
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#MockingAndStubbing
- Use a real implementation in place of a test double, unless it is slow, nondeterministic, or hard to construct. ^prefer-real-implementations
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#prefer_realism_over_isolation
- Use the real implementation of each dependency that is fast, deterministic, and simple to construct, such as a value object. ^real-value-objects
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#how_to_decide_when_to_use_a_real_implem
- If the real implementation is slow, nondeterministic, or hard to construct, use a fake, unless no fake exists. ^prefer-fakes
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#tlsemicolondrs-id00116
- Replace a dependency on the system clock with a test double that returns a fixed time. ^double-the-clock
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#determinism
- Replace a dependency on an external server with a test double, unless no test double fits the test. ^double-external-servers
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#determinism
- If no test double fits a dependency on an external server, use a hermetic server that the test controls. ^hermetic-server-fallback
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#determinism
- Build the objects of a test with the factory or the dependency injection of the production code. ^production-construction-in-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#dependency_construction
- Assign the fake of an API to the team that owns the real implementation. ^owner-writes-the-fake
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#when_should_fakes_be_writtenquestion_ma
- Write each fake for the API that does not fit in tests, not for each class that calls the API. ^fake-at-the-root-api
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#when_should_fakes_be_writtenquestion_ma
- Give a fake the same outputs and state changes as the real implementation, for each input of the API contract. ^fake-fidelity
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#the_fidelity_of_fakes
- Make a fake raise an error when a test reaches a path that the fake does not support. ^fake-fails-fast
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#the_fidelity_of_fakes
- Give each fake its own tests, such as contract tests that also run against the real implementation. ^test-each-fake
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#fakes_should_be_tested
- If no fake exists for an API, ask its owners to write one. ^ask-owners-for-a-fake
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#what_to_do_if_a_fake_is_not_available
- If the API owners write no fake, write a fake of `1` class that wraps each call to the API. ^wrap-and-fake
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#what_to_do_if_a_fake_is_not_available
- Limit the stubs of a test to the functions that its assertions depend on. ^stub-only-for-assertions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#when_is_stubbing_appropriatequestion_ma
- Use state testing, unless the behavior is a call count or order, or no real implementation or fake fits. ^prefer-state-testing
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#prefer_state_testing_over_interaction_t
  - sources: https://martinfowler.com/articles/mocksArentStubs.html#TheDifferenceBetweenMocksAndStubs
- Limit interaction testing to call counts, call orders, and dependencies that have no usable real implementation or fake. ^when-to-test-interactions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#when_is_interaction_testing_appropriate
- In an interaction test, verify only the calls to state-changing functions, unless the test verifies a call count or order. ^verify-state-changing-calls
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#prefer_to_perform_interaction_testing_o
- In an interaction test, verify only the calls and the arguments that the tested behavior needs. ^no-overspecified-interactions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#avoid_overspecification
- If a unit test checks only interactions, add a larger test that checks the state against a real implementation. ^back-interactions-with-state
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch13.html#when_is_interaction_testing_appropriate
- Do not replace the part of the code that the test verifies with a test double. ^do-not-double-the-subject
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: http://xunitpatterns.com/Test%20Double.html
- Keep at least `1` test that runs the code under test without test doubles. ^one-test-without-doubles
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: http://xunitpatterns.com/Test%20Double.html

## Notes

The 5 kinds differ by what the test does with the double:

- A dummy fills a parameter list and is never used.
- A stub returns canned answers. It is a control point for the indirect inputs of the code under test.
- A spy is a stub that also records how the code called it. The test checks the record after the action.
- A mock holds the expected calls before the action, and fails when a call does not match. It is an observation point for the indirect outputs.
- A fake has a working implementation, usually with a shortcut that makes it unfit for production, such as an in-memory database.

State verification checks the state or the return value after the action. Behavior verification, or interaction testing, checks the calls that the code made to its dependencies. Martin Fowler names 2 styles of test-driven development after this choice: the classical style uses real objects where it can, and the mockist style uses a mock for each object with interesting behavior. The default tree follows the classical style of Software Engineering at Google: a real implementation first, a fake next, and a stub or a mock last. A mock couples the test to the implementation, so a refactor can break the test.

The fidelity of a double is how closely it follows the real dependency. A double with low fidelity lets a test pass while the real code fails. Contract testing checks the fidelity of a double against the real service. The test pyramid sets where doubles go: each small test replaces the dependencies that leave its process.
