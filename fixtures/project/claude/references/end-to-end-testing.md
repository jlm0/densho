<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# End-to-end testing

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

From [End-to-end testing](end-to-end-testing.md):

- Make each timeout and delay of the production code configurable for the large tests. ^configurable-timeouts
- Run each large test hermetically, unless it is a prober or a backend has no runnable copy. ^hermetic-large-tests
- If a backend has no runnable copy, limit the shared parts of the system under test to that backend. ^hybrid-system-under-test
- Give each large test a failure message that names the test, the expected result, and the actual result. ^large-test-failure-message
- Add a large test for each risk that small tests miss, such as configuration, load, or an unfaithful double. ^large-test-for-each-gap
- Build each large test from a system under test, its seeded data, the actions, and the verification. ^large-test-structure
- Before a deployment to production, run the large tests that address the risks of the system. ^large-tests-before-deploy
- Give each large test a documented owner who reviews its changes and supports its failures. ^own-each-large-test
- Run each prober against production with deterministic read-only actions. ^probers-against-production
- Run each usability test on the complete system in a representative test environment. ^representative-system-test-environment
- If a large test is slow, split it into smaller tests that run in parallel. ^split-slow-large-tests
- If a broad test does not check the user interface, run it through the API below the user interface. ^subcutaneous-broad-tests
- Test the deployment configuration of each service with a large test. ^test-deployment-configuration
- Make each large test produce an artifact that locates the cause of a failure, such as a request trace. ^trace-large-test-requests

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
