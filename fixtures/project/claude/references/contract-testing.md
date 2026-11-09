<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Contract testing

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

From [Contract testing](contract-testing.md):

- Assert only on the fields that affect the consumer when they change. ^assert-consumer-fields-only
- Send each call from a consumer to a provider through a client that the contract tests cover. ^calls-through-the-tested-client
- Before a consumer or a provider deploys, check that its version passed verification with each version in the target environment. ^can-i-deploy
- If the consumers of an API are unknown, do not use consumer-driven contracts. ^cdc-needs-known-consumers
- If a stub holds a snapshot, check field formats, not field content, unless the consumer depends on that content. ^check-format-not-data
- In a consumer contract, state only the parts of the provider contract that the consumer uses. ^consumer-states-what-it-uses
- Write the consumer side of a contract as unit tests of the API client of the consumer. ^consumer-tests-the-client
- Write each HTTP contract as interactions, each with an expected request and the response parts that the consumer uses. ^contract-as-interactions
- Do not use a contract test to test the functions of the provider. ^contract-not-functional
- Check with contract tests that each test double gives the results of the real service, unless it holds a snapshot. ^double-matches-the-service
- If the consumer depends on the content of a response field, match the content exactly. ^exact-match-for-used-content
- In a write interaction, require the updated resource in the response, unless the provider does not return it. ^expect-written-values-back
- Run the contract tests of an external service against its test instance, unless it has no test instance. ^external-contract-test-instance
- Run the contract tests of an external service once a day. ^external-contract-test-pace
- If a contract test of an external service fails, open a task to bring the test doubles back in line. ^fix-doubles-on-contract-failure
- Match each response field that the consumer uses by its type, unless the consumer depends on its content. ^loose-response-matching
- Do not use contract tests to test the user interface of a consumer. ^no-contract-tests-through-ui
- Do not treat a shared OpenAPI description as a contract test, unless a tool checks each side against it. ^openapi-is-not-a-contract-test
- If an external service has no test instance, tell its owners about each contract test against its production instance. ^production-contract-tests-with-owners
- Build the contract of a provider from each consumer expectation inside its business function, unless its consumers are unknown. ^provider-contract-from-consumers
- Describe each precondition of an interaction as a provider state, not as an earlier interaction. ^provider-states
- Record the version and the environment of each deployment of a consumer or a provider. ^record-each-deployment
- Reject a consumer expectation that falls outside the business function of the provider. ^reject-out-of-mandate-expectations
- Include a scenario only if its absence hides a consumer bug or a misunderstanding of the provider response. ^scenario-must-catch-something
- If the provider returns no updated resource, use a shared fixture for the write request and the read response. ^shared-fixture-for-writes
- In a provider verification, limit the stubs to code that runs after the provider parses and validates the request. ^stub-below-request-parsing
- In the broader tests of the consumer, use the generated contract as the stubs of the provider. ^stub-from-the-contract
- Tell the owners of an external service when a change to its contract breaks a contract test. ^tell-the-service-owners
- In the build of the provider, verify each contract against a local instance of the provider, not a deployed instance. ^verify-against-local-provider
- Run the verification of the consumer contracts in the build of the provider. ^verify-in-provider-build

## Definition

A test that checks that a test double still behaves like the external service that it stands for. Martin Fowler describes contract tests as checks that each call against a test double returns the same results as a call to the external service. Ian Robinson's consumer-driven contracts invert the direction: each consumer states what it expects of a provider, and the contract of the provider is the union of these expectations. The Pact docs define contract testing as a check of each application in isolation against a shared contract for the messages between them.

## Notes

A contract test has 2 sides. The consumer side runs the API client of the consumer against a mock provider and records each interaction. The provider side replays each recorded interaction against the real provider and checks the response. Each interaction is independent, and a provider state sets up the data that it needs.

Ian Robinson names 3 kinds of contract:

- A provider contract is closed, complete, and authoritative. It lists each function that the provider offers.
- A consumer contract is open and incomplete. It lists only what one consumer uses, and there is one for each consumer.
- A consumer-driven contract is the union of the consumer contracts. It is complete for the current consumers, but not authoritative.

Robinson states the limits of the pattern: it works inside one company or a closed group of known services, it does not always reduce the coupling, and it shows the coupling that was hidden.

Martin Fowler describes contract tests for an external service that a different team maintains. Those tests run on the schedule of the external service, and a failure starts a task and need not break the build. The Pact docs use the same name for tests between 2 services that communicate, and these run in the build of each side.

The interface contract of software design describes the whole API, such as an OpenAPI description. A consumer contract checks the part that a consumer uses, by example. Test doubles are what a contract test keeps faithful. The test pyramid places contract tests next to the narrow integration tests that use those doubles.
