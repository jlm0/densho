<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test pyramid

## Directives

No directive is in force at this node.

## Definition

A model for the mix of automated tests in a suite, by the level of each test. Mike Cohn's original pyramid has 3 layers: unit tests at the wide base, service tests in the middle, and tests through the user interface at the narrow top. The ISTQB Foundation Level syllabus states the model in general terms: the higher the layer, the lower the granularity and the isolation of its tests, and the longer they run. So a suite holds many small, fast tests at the base and few broad tests at the top.

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
