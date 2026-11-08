<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Unit testing

## Directives

No directive is in force at this node.

## Definition

A test that checks one unit of the code in isolation from the rest of the system. The ISTQB Foundation Level syllabus calls this level component testing, and states that developers normally run these tests in their development environments. SWEBOK v4 defines the unit as an element of the system under test that is separately testable, such as a subprogram, a component, or a subsystem. Software Engineering at Google calls unit tests narrow-scoped tests: each one validates the logic of a small, focused part of the code, such as one class or one method.

## Notes

The Practical Test Pyramid names 2 kinds of unit test. A solitary unit test replaces each collaborator of the unit with a test double. A sociable unit test keeps the real collaborators. The default tree prefers real collaborators, and the test doubles concept holds that rule.

Software Engineering at Google separates the size of a test from its scope. A small test runs in one process, and most unit tests are small. The rules for clear unit tests follow from one goal: a test that never changes unless the requirements change. A pure refactor, a new feature, and a bug fix leave the existing tests as they are. Only a change of the required behavior changes a test. If a pure refactor breaks a test, the test does not use the public API, and the fix changes the test to use it.

Each test has a given part, a when part, and a then part. The practice area holds the rule for this structure, the rule to test through the public interface, and the rule against logic in tests, so that each test level applies them. Test-driven development writes unit tests one at a time.
