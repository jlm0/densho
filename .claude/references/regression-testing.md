<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Regression testing

## Directives

No directive is in force at this node.

## Definition

Testing that confirms that a change causes no adverse effect on the parts of the system that worked before. The ISTQB Foundation Level syllabus gives this definition, and pairs it with confirmation testing, which confirms that a fix removed the original defect. SWEBOK v4 calls regression testing the selective retesting of the system under test after a change, and adds the selection, the minimization, and the prioritization of the tests. Martin Fowler warns that a non-deterministic test can ruin the whole regression suite. Luo and colleagues call a test with a non-deterministic outcome a flaky test.

## Notes

Confirmation testing and regression testing answer 2 questions after a change. Confirmation testing asks whether the fix removed the defect. Regression testing asks whether the change broke anything else, in the same component, in other components, or in connected systems. Maintenance testing applies both to a system in operation, after a modification, a migration, or a retirement.

The ISTQB syllabus names 3 ways to order the tests:

- Risk-based: the tests of the highest risks run first.
- Coverage-based: the tests with the highest coverage, or the highest additional coverage, run first.
- Requirements-based: the tests of the most important requirements run first.

A flaky test passes and fails on the same code. Martin Fowler calls such tests useless and infectious: once a team ignores their failures, it ignores real failures too. At Google in 2016, about `1.5%` of test runs were flaky, almost `16%` of tests showed some flakiness, and about `84%` of the observed pass-to-fail transitions involved a flaky test. Luo and colleagues found 3 top causes in open-source projects: asynchronous waits (`45%`), concurrency (`20%`), and test order dependency (`12%`). `78%` of the flaky tests were flaky when they were first written, and `24%` of the fixes changed the code under test, most of them to fix a real bug.

Quarantine keeps the healthy suite trustworthy while the flaky tests wait for a fix. Fowler keeps the quarantine suite out of the main pipeline for most teams. The Google blog warns that quarantine can hide a real race condition. An automatic rerun hides the same problem, and the practice area holds that rule. The test doubles concept holds the rules for the clock and for remote services, which are 2 more causes of non-determinism.
