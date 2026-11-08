<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# End-to-end testing

## Directives

No directive is in force at this node.

## Definition

A test that checks the whole system, with each of its parts integrated, through the interface that its users use. The ISTQB Foundation Level syllabus calls this level system testing: it checks the overall behavior and capabilities of the whole system, often with functional tests of end-to-end tasks. The Practical Test Pyramid also calls it a broad stack test. Software Engineering at Google calls these tests large-scoped tests: they validate the interaction of distinct parts of the system, or emergent behavior that no single class or method shows.

## Notes

Software Engineering at Google names the gaps that unit tests leave, and each gap is a reason for a large test:

- A test double that does not behave like the real dependency.
- A configuration file, a flag, or a deployment setting that the code reads at run time.
- A behavior that appears only under load.
- An input or a behavior that the author of the unit tests did not expect.
- An emergent behavior of the whole system.

A large test has 4 parts: the system under test, the seeded data, the actions, and the verification. A hermetic system under test runs in isolation from production and from a shared staging environment, so other users do not change its results. A hybrid system under test runs the tested part and shares each backend that has no runnable copy. A prober is a large test that runs against production as a form of monitoring. It uses deterministic read-only actions, so its assertions hold while the production data changes. A system under test with fewer parts is faster and less flaky. A test that drives both the user interface and the backend is costly to keep. Software Engineering at Google splits such a test at the boundary between the user interface and the public API.

End-to-end tests are slow, and they fail for reasons outside the code, such as timing and browser quirks. The test pyramid limits them to the core user journeys. Performance testing and acceptance testing also run against the whole system. Performance testing holds the rules for load. Regression testing holds the rules for waits and for flaky tests. Acceptance testing in software quality holds the rules that check the requirements of the users.
