<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Regression testing

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Accessibility](accessibility.md):

- Run each single-pointer action on the up event, not on the down event. ^act-on-pointer-up
- Keep each text visible when a user raises its line, paragraph, letter, or word spacing. ^allow-text-spacing
- Give a way to bypass each block of content that repeats across pages. ^bypass-repeated-blocks
- Give components with the same function the same label and the same glyph on each page. ^consistent-identification
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components
- Declare the purpose of each field that collects data about the user, such as with `autocomplete`. ^declare-input-purpose
- Declare the main language of each page in the code. ^declare-page-language
- When a check finds an input error, describe the error and its field in text. ^describe-input-error
- Make each heading and label state the topic or the purpose of its content. ^descriptive-headings-and-labels
- Give each page a title that states its topic or purpose. ^descriptive-page-title
- Expose each status message to assistive technology without moving the focus to it. ^expose-status-messages
- Do not hide the focused control completely behind a sticky header, a banner, or another element. ^focus-not-obscured
- Hide each decorative image from assistive technology. ^hide-decoration
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
- Give each input field a label or an instruction. ^label-each-field
- Include the visible label text of each control in its accessible name. ^label-in-name
- State the purpose of each link in its text or in the sentence that holds it. ^link-purpose
- Set a focus order that keeps the meaning and the operation of the content. ^logical-focus-order
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
- Expose the name, the role, and the state of each custom control to assistive technology. ^name-role-value
- Do not change the context when a control receives focus. ^no-change-on-focus
- Do not change the context when a user changes a setting, unless the control warns of it first. ^no-change-on-input
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap
- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock
- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions
- Keep the order of the content in the code the same as its visual reading order. ^reading-order-in-code
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Use the element or role that matches the visual structure of each heading, list, table, and form label. ^structure-in-code
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Give each meaningful image a text alternative. ^text-alternative
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page

From [Software testing](software-testing.md):

- Do not put a conditional or a loop in an example-based test, unless the loop polls for an asynchronous result. ^no-logic-in-tests
- Do not treat an automatic rerun of a flaky test as a fix of its cause. ^no-rerun-for-flaky-test
- Split each test into its setup, its action, and its verification. ^setup-action-verification
- Do not write a test for code without conditional logic, such as a plain getter or setter. ^skip-trivial-code
- Include a test that reproduces the bug in each bug fix. ^test-before-bug-fix
- Test each unit through its public interface, unless a property checks the invariant of its representation. ^test-public-interface

From [Regression testing](regression-testing.md):

- Write automated regression tests from the start of the project. ^automate-regression-early
- Do not delete a flaky test before you check the code under test for a bug. ^check-code-before-deleting-flaky-tests
- Check each new test for flakiness before you add it to the regression suite. ^check-new-tests-for-flakiness
- If the starting state needs a database with preloaded data, reset each shared state after each test. ^clean-shared-state
- After a defect fix, confirm that the steps that reproduced its failure no longer fail. ^confirm-the-fix
- If a high-priority test depends on a lower-priority test, run the lower-priority test first. ^dependencies-before-priority
- Raise a distinct timeout error when a test reaches its wait limit. ^distinct-timeout-error
- If different tests fail at random, limit each resource pool to `1` resource, with an error for an empty pool. ^expose-resource-leaks
- Before regression testing, run an impact analysis to find the parts of the system that the change affects. ^impact-analysis-first
- Build the starting state of each test from scratch, unless the state needs a database with preloaded data. ^isolated-test-state
- Limit the time of each test in quarantine to `1` week. ^limit-the-quarantine
- Set the scope of maintenance testing by the risk, the size of the system, and the size of the change. ^maintenance-test-scope
- Order the regression tests by the product risks that they cover. ^order-tests-by-priority
- Move each flaky test from the main suite into a quarantine suite. ^quarantine-flaky-tests
- After the confirmation tests pass, run the regression tests on the changed system. ^regression-after-confirmation
- Run the regression tests at each test level where a change or a fix happens. ^regression-at-each-level
- Run the regression suite after integration testing and before each deployment to production. ^regression-before-deployment
- Set each wait limit of a test from `1` shared setting, not as a literal value. ^shared-wait-limits
- Open a task to fix each test that goes into quarantine. ^task-for-each-quarantined-test
- When the system moves to a new operational environment, test the changed system in that environment. ^test-environment-migrations
- Add tests for each change that a defect fix needed, unless no time or budget remains. ^test-the-changes-of-a-fix
- Track the flaky results of each test over time. ^track-flakiness
- Wait for an asynchronous result with a callback, unless the service has no callback. ^wait-by-callback
- If an asynchronous service has no callback, wait for its result in a polling loop with a wait limit. ^wait-by-polling

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
