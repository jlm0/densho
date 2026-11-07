<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Integration testing

## Directives

No directive is in force at this node.

## Definition

A test that checks whether parts that are developed separately work correctly when they are connected. The ISTQB Foundation Level syllabus names 2 levels: component integration testing checks the interfaces and the interactions between components, and system integration testing checks the interfaces between the system and other systems or external services. Martin Fowler separates 2 kinds. A narrow integration test runs only the code that talks to a separate service, with a test double of that service. A broad integration test needs live versions of each service.

## Notes

The name integration test has more than one meaning, so a team states which one it uses. Martin Fowler lists 3 uses:

- A narrow integration test runs the code of one service that talks to a database, a file system, a queue, or another service. It uses a test double of the other service, and it often runs in the same test framework as the unit tests.
- A broad integration test runs live versions of each service and exercises code paths through each of them. Martin Fowler prefers the name system test or end-to-end test for it.
- Some writers use the name for a sociable unit test.

Software Engineering at Google calls a test of the interactions between a small number of components a medium-scoped test. A medium test can start several processes and use the network, but only on one machine.

SWEBOK v4 and the ISTQB syllabus name the integration strategies: top-down, bottom-up, mixed or sandwich, and big bang. SWEBOK describes integration as incremental and systematic, by functional thread or by architecture.

A narrow integration test is only as good as its test double. Contract testing checks that each double still behaves like the real service.
