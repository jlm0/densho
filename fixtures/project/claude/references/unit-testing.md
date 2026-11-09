<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Unit testing

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

From [Unit testing](unit-testing.md):

- Change an existing unit test only when the required behavior of the system changes, unless a pure refactor breaks it. ^change-tests-only-for-behavior
- Write each failure message with the expected outcome, the actual outcome, and the inputs that produced them. ^clear-failure-messages
- Put each fact that explains the result of a test in the body of the test. ^complete-test-body
- Move each construction detail that does not affect the result into a helper. ^concise-test-body
- Do not move a step of a test into shared code that hides what the test does. ^damp-over-dry
- If a test targets a private method, move the method into a new class with a public interface. ^extract-private-method
- Name each unit test after the action that it takes and the outcome that it requires. ^name-after-the-behavior
- Limit each validation helper to `1` conceptual fact about its inputs. ^one-fact-per-validation-helper
- Make the result of each unit test independent of the order in which the tests run. ^order-independent-tests
- If a pure refactor breaks a unit test, make the test verify state through the public API. ^refactor-breaks-test
- Run the unit tests in the development environment. ^run-in-development-environment
- Use a setup method to build the object under test and its collaborators with default values. ^setup-for-defaults
- If a test depends on a value from the setup method, set that value in the test body. ^state-setup-values
- Write a separate test for each behavior of a unit, not `1` test for each method. ^test-each-behavior
- Treat shared test infrastructure as a separate product with its own tests. ^test-infrastructure-as-product
- Build each test value with a helper that takes only the fields that the test depends on. ^test-value-helpers
- Test each code path of a unit with conditional logic, including the happy path and each edge case. ^unit-test-each-code-path
- Test the response of a unit to each error that the interface of its dependency declares. ^unit-test-each-error
- In a unit test, replace each dependency that uses a network, a disk, or another process with a test double. ^unit-test-in-one-process

## Definition

A test that checks one unit of the code in isolation from the rest of the system. The ISTQB Foundation Level syllabus calls this level component testing, and states that developers normally run these tests in their development environments. SWEBOK v4 defines the unit as an element of the system under test that is separately testable, such as a subprogram, a component, or a subsystem. Software Engineering at Google calls unit tests narrow-scoped tests: each one validates the logic of a small, focused part of the code, such as one class or one method.

## Notes

The Practical Test Pyramid names 2 kinds of unit test. A solitary unit test replaces each collaborator of the unit with a test double. A sociable unit test keeps the real collaborators. The default tree prefers real collaborators, and the test doubles concept holds that rule.

Software Engineering at Google separates the size of a test from its scope. A small test runs in one process, and most unit tests are small. The rules for clear unit tests follow from one goal: a test that never changes unless the requirements change. A pure refactor, a new feature, and a bug fix leave the existing tests as they are. Only a change of the required behavior changes a test. If a pure refactor breaks a test, the test does not use the public API, and the fix changes the test to use it.

Each test has a given part, a when part, and a then part. The practice area holds the rule for this structure, the rule to test through the public interface, and the rule against logic in tests, so that each test level applies them. Test-driven development writes unit tests one at a time.
