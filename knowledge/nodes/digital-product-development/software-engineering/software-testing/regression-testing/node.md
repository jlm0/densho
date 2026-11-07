---
id: regression-testing
kind: densho:Concept
title: Regression testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=30
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=124
  - https://mir.cs.illinois.edu/lamyaa/publications/fse14.pdf
  - https://martinfowler.com/articles/nonDeterminism.html
  - https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
broader:
  - software-testing
---

## Definition

Testing that confirms that a change causes no adverse effect on the parts of the system that worked before. The ISTQB Foundation Level syllabus gives this definition, and pairs it with confirmation testing, which confirms that a fix removed the original defect. SWEBOK v4 calls regression testing the selective retesting of the system under test after a change, and adds the selection, the minimization, and the prioritization of the tests. A regression suite works only when its tests are deterministic. Luo and colleagues call a test with a non-deterministic outcome a flaky test.

## Directives

- After a defect fix, confirm that the steps that reproduced its failure no longer fail. ^confirm-the-fix
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=30
- If the risk of a defect fix is high, add tests for each change that the fix needed. ^test-the-changes-of-a-fix
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=30
- After the confirmation tests pass, run the regression tests on the changed system. ^regression-after-confirmation
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=30
- Before regression testing, run an impact analysis to find the parts of the system that the change affects. ^impact-analysis-first
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=31
- Set the scope of maintenance testing by the risk, the size of the system, and the size of the change. ^maintenance-test-scope
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=31
- When the system moves to a new operational environment, test the changed system in that environment. ^test-environment-migrations
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=31
- Run the regression tests at each test level where a change or a fix happens. ^regression-at-each-level
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=31
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=124
- Write automated regression tests from the start of the project. ^automate-regression-early
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=31
- If the team uses continuous integration, run the automated regression tests in it. ^regression-in-continuous-integration
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=31
- Order the regression tests by risk, by coverage, or by the priority of their requirements. ^order-tests-by-priority
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=50
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=124
- If a high-priority test depends on a lower-priority test, run the lower-priority test first. ^dependencies-before-priority
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=50
- Check each new test for flakiness before you add it to the regression suite. ^check-new-tests-for-flakiness
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://mir.cs.illinois.edu/lamyaa/publications/fse14.pdf#page=2
- Prefer a rebuild of the starting state of each test over a clean-up after each test. ^isolated-test-state
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html
- If a rebuild of the starting state is too slow, reset each shared state after each test. ^clean-shared-state
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html
  - sources: https://mir.cs.illinois.edu/lamyaa/publications/fse14.pdf#page=2
- Wait for an asynchronous result with a callback or a polling loop with a timeout, not with a fixed sleep. ^wait-by-polling
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html
  - sources: https://mir.cs.illinois.edu/lamyaa/publications/fse14.pdf#page=2
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#driving_out_flakiness
- Set each wait limit of a test from `1` shared setting, not as a literal value. ^shared-wait-limits
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html
- Raise a distinct timeout error when a test reaches its wait limit. ^distinct-timeout-error
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html
- If you suspect a resource leak, limit each pool to `1` resource, with an error for an empty pool. ^expose-resource-leaks
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html
- Track the flaky results of each test over time. ^track-flakiness
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
- Move each flaky test from the main suite into a quarantine suite. ^quarantine-flaky-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html#Quarantine
  - sources: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
- Open a task to fix each test that goes into quarantine. ^task-for-each-quarantined-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
  - sources: https://martinfowler.com/articles/nonDeterminism.html#Quarantine
- Limit the quarantine by a count of tests or by a time, such as `1` week for each test. ^limit-the-quarantine
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/nonDeterminism.html#Quarantine
- Do not delete a flaky test before you check the code under test for a bug. ^check-code-before-deleting-flaky-tests
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://mir.cs.illinois.edu/lamyaa/publications/fse14.pdf#page=2
- Run the regression suite after integration testing and before each deployment to production. ^regression-before-deployment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=124

## Notes

Confirmation testing and regression testing answer 2 questions after a change. Confirmation testing asks whether the fix removed the defect. Regression testing asks whether the change broke anything else, in the same component, in other components, or in connected systems. Maintenance testing applies both to a system in operation, after a modification, a migration, or a retirement.

The ISTQB syllabus names 3 ways to order the tests:

- Risk-based: the tests of the highest risks run first.
- Coverage-based: the tests with the highest coverage, or the highest additional coverage, run first.
- Requirements-based: the tests of the most important requirements run first.

A flaky test passes and fails on the same code. Martin Fowler calls such tests useless and infectious: once a team ignores their failures, it ignores real failures too. At Google in 2016, about `1.5%` of test runs were flaky, almost `16%` of tests showed some flakiness, and about `84%` of the observed pass-to-fail transitions involved a flaky test. Luo and colleagues found 3 top causes in open-source projects: asynchronous waits (`45%`), concurrency (`20%`), and test order dependency (`12%`). `78%` of the flaky tests were flaky when they were first written, and `24%` of the fixes changed the code under test, most of them to fix a real bug.

Quarantine keeps the healthy suite trustworthy while the flaky tests wait for a fix. Fowler keeps the quarantine suite out of the main pipeline for most teams. The Google blog warns that quarantine can hide a real race condition. An automatic rerun hides the same problem, and the practice area holds that rule. The test doubles concept holds the rules for the clock and for remote services, which are 2 more causes of non-determinism.
