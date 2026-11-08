<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test-driven development

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

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

From [Test-driven development](test-driven-development.md):

- If a duplication has `3` or more copies, extract it into an abstraction in the refactor step. ^abstract-at-three-copies
- When you find a new case during a step, add it to the test list. ^add-new-cases-to-the-list
- Write production code only to make a failing test pass, unless you refactor the code after a test passes. ^code-only-for-a-failing-test
- Do not extract a duplication into an abstraction in the refactor step, unless it has `3` or more copies. ^duplication-is-a-hint
- Do not refactor while you make a failing test pass. ^green-before-refactor
- Keep each test of the cycle as an automated regression test. ^keep-tdd-tests
- Do not delete an assertion to make a test pass. ^keep-the-assertions
- Do not refactor beyond the current test list. ^limit-the-refactor
- List each variant of the new behavior and each existing behavior that the change puts at risk. ^list-variants-and-risks
- Change the code until the new test and each earlier test pass. ^make-all-tests-pass
- Mark each item of the test list as done when its test passes. ^mark-passing-items
- Do not copy a value that the code computes into the expected value of its test. ^no-copied-expected-values
- Do not put an implementation design decision in the test list. ^no-design-in-test-list
- Do not write tests for the whole test list before the first test passes. ^no-speculative-tests
- Do not write a test without an assertion. ^no-test-without-assertion
- Write exactly `1` item of the test list as a runnable test before you change the code. ^one-test-at-a-time
- After each test passes, refactor the new code and the old code to keep a clean structure. ^refactor-after-green
- Repeat the cycle from the second step until the test list is empty. ^repeat-until-the-list-is-empty
- If a new case invalidates the earlier work, start over with a different test order. ^restart-in-a-new-order
- Before you change the code, confirm that each new test fails. ^see-the-test-fail
- Write the first test of a behavior from its interface, before you decide its implementation. ^test-the-interface-first
- Before you change a behavior, write a list of the test scenarios that the change needs. ^write-the-test-list

## Definition

A way to write code in which a test comes before the code that makes it pass. Kent Beck states the canon in 5 steps: write a list of the test scenarios, turn exactly one item on the list into a concrete and runnable test, change the code to make that test and all earlier tests pass, optionally refactor, and go back to the second step until the list is empty. Martin Fowler sums up the core as red, green, refactor.

## Notes

The cycle has 5 steps, and each step has its own failure mode that Kent Beck names:

1. The test list holds the behavior variants of the change. The mistake is to mix in implementation decisions.
2. One test becomes concrete, with its setup, its invocation, and its assertions. The mistakes are a test without assertions, and a test for each item of the list at once.
3. The code changes until each test passes. The mistakes are a deleted assertion, an expected value copied from the code, and a refactor mixed into this step.
4. An optional refactor improves the implementation design. The mistakes are a refactor beyond the session and an abstraction that comes too soon.
5. The cycle repeats until the list is empty.

Kent Beck calls the choice of the next test a skill that comes only with experience, so this concept holds no rule for the order of the tests. This concept counts an abstraction as too soon while the duplication has fewer than `3` copies.

Red, green, refactor names steps 2 to 4: the new test fails, the code makes it pass, and the refactor cleans the code. Martin Fowler names 2 benefits: self-testing code, and a focus on the interface before the implementation. He names the skipped refactor as the most common way to fail at the practice.

The ISTQB Foundation Level syllabus puts test-driven development next to acceptance test-driven development and behavior-driven development. All 3 write the tests before the code. Acceptance test-driven development derives its tests from the acceptance criteria, and acceptance testing in software quality holds its rules. Specification by example in software requirements holds the Given, When, Then form of behavior-driven development.

The test pyramid sets the level of each test in the list. Test doubles replace the dependencies that a unit test of the cycle does not run.
