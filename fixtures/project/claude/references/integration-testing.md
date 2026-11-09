<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Integration testing

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

From [Integration testing](integration-testing.md):

- If a suite holds only broad integration tests, add narrow integration tests. ^add-narrow-integration-tests
- Choose the integration strategy: top-down, bottom-up, sandwich, or big bang. ^choose-integration-strategy
- Write an integration test for each part of the code that serializes or deserializes data at a boundary. ^integration-test-each-boundary
- Add errors and latency to the calls between components in the integration tests. ^integration-test-failures
- In a narrow integration test, run each external dependency locally, unless it is a third-party service with no local version. ^local-integration-dependencies
- Do not run an integration test against production, unless a contract test has no test instance to target. ^no-tests-against-production
- In a narrow integration test, test only the code that calls another service, against a test double of it. ^one-integration-point-per-test
- In a narrow integration test, limit the network calls to localhost, unless a third-party service has no local version. ^one-machine-integration-tests
- Add a contract test for each test double of a service that a narrow integration test uses. ^pair-narrow-test-with-contract
- In a database integration test, check the written data by reading it back from the database. ^read-back-written-data
- Run the system integration tests in an environment similar to the operational environment. ^system-integration-environment
- If a third-party service has no local version, run the integration tests against its dedicated test instance. ^third-party-test-instance

## Definition

A test that checks whether parts that are developed separately work correctly when they are connected. The ISTQB Foundation Level syllabus names 2 levels: component integration testing checks the interfaces and the interactions between components, and system integration testing checks the interfaces between the system and other systems or external services. Martin Fowler separates 2 kinds. A narrow integration test runs only the code that talks to a separate service, with a test double of that service. A broad integration test needs live versions of each service.

## Notes

The name integration test has more than one meaning, so Martin Fowler looks for the context of each use. Martin Fowler lists 3 uses:

- A narrow integration test runs the code of one service that talks to a database, a file system, a queue, or another service. It uses a test double of the other service, and it often runs in the same test framework as the unit tests.
- A broad integration test runs live versions of each service and exercises code paths through each of them. Martin Fowler prefers the name system test or end-to-end test for it.
- Some writers use the name for a sociable unit test.

Software Engineering at Google calls a test of the interactions between a small number of components a medium-scoped test. A medium test can start several processes and use the network, but only on one machine.

SWEBOK v4 and the ISTQB syllabus name the integration strategies: top-down, bottom-up, mixed or sandwich, and big bang. SWEBOK describes integration as incremental and systematic, by functional thread or by architecture.

A narrow integration test is only as good as its test double. Contract testing checks that each double still behaves like the real service.
