<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test doubles

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

From [Test doubles](test-doubles.md):

- If no fake exists for an API, ask its owners to write one. ^ask-owners-for-a-fake
- If a unit test checks only interactions, add a larger test that checks the state against a real implementation. ^back-interactions-with-state
- Do not replace the part of the code that the test verifies with a test double. ^do-not-double-the-subject
- Replace a dependency on an external server with a test double, unless no test double fits the test. ^double-external-servers
- Replace a dependency on the system clock with a test double that returns a fixed time. ^double-the-clock
- Use a dummy only for an argument or an attribute that the code under test never uses. ^dummy-for-unused-arguments
- Write each fake for the API whose real implementation does not fit the tests, not for its callers. ^fake-at-the-root-api
- Make a fake raise an error when a test reaches a path that the fake does not support. ^fake-fails-fast
- Give a fake the same outputs and state changes as the real implementation, for each input that it supports. ^fake-fidelity
- If the real implementation is unavailable, slow, nondeterministic, or hard to construct, use a fake, unless no fake exists. ^fake-for-unusable-real
- If no test double fits a dependency on an external server, use a hermetic server that the test controls. ^hermetic-server-fallback
- Name each test double by its kind: dummy, stub, spy, mock, or fake. ^name-the-double-kind
- In an interaction test, verify only the calls and the arguments that the tested behavior needs. ^no-overspecified-interactions
- Keep at least `1` test that runs the code under test without test doubles. ^one-test-without-doubles
- Assign the fake of an API to the team that owns the real implementation. ^owner-writes-the-fake
- Build the objects of a test with the factory or the dependency injection of the production code. ^production-construction-in-tests
- If no state verification observes an indirect output, verify it with a spy. ^spy-or-mock-for-indirect-outputs
- Use a stub only to feed the indirect inputs that put the code under test into a needed state. ^stub-for-indirect-inputs
- Limit the stubs of a test to the functions that its assertions depend on. ^stub-only-for-assertions
- Give each fake its own tests, such as contract tests that also run against the real implementation. ^test-each-fake
- Use a real implementation in place of a test double, unless it is slow, nondeterministic, or hard to construct. ^use-real-implementations
- Use state testing, unless the behavior is a call count or order, or no real implementation or fake fits. ^use-state-testing
- In an interaction test, verify only the calls to state-changing functions, unless the test verifies a call count or order. ^verify-state-changing-calls
- Limit interaction testing to call counts, call orders, and dependencies with no real implementation or fake that fits the test. ^when-to-test-interactions
- If the API owners write no fake, write a fake of `1` class that wraps each call to the API. ^wrap-and-fake

## Definition

An object that replaces a production object in a test. Gerard Meszaros named the general term after a stunt double, and his xUnit Test Patterns names 5 kinds by their use: a dummy, a stub, a spy, a mock, and a fake. A test double gives the test control over the indirect inputs of the code under test, or a point to observe its indirect outputs, or a faster stand-in for a slow dependency.

## Notes

The 5 kinds differ by what the test does with the double:

- A dummy fills a parameter list and is never used.
- A stub returns canned answers. It is a control point for the indirect inputs of the code under test.
- A spy is a stub that also records how the code called it. The test checks the record after the action.
- A mock holds the expected calls before the action, and fails when a call does not match. It is an observation point for the indirect outputs.
- A fake has a working implementation, usually with a shortcut that makes it unfit for production, such as an in-memory database.

State verification checks the state or the return value after the action. Behavior verification, or interaction testing, checks the calls that the code made to its dependencies. Martin Fowler names 2 styles of test-driven development after this choice: the classical style uses real objects where it can, and the mockist style uses a mock for each object with interesting behavior. The default tree follows the classical style of Software Engineering at Google: a real implementation first, a fake next, and a stub or a mock last. A mock couples the test to the implementation, so a refactor can break the test. A real implementation fits a test when it is fast, deterministic, and simple to construct. A test double fits a test when it supports each call that the test makes.

The fidelity of a double is how closely it follows the real dependency. A double with low fidelity lets a test pass while the real code fails. Contract testing checks the fidelity of a double against the real service. The test pyramid sets where doubles go: each small test replaces the dependencies that leave its process.
