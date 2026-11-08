<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test pyramid

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

From [Test pyramid](test-pyramid.md):

- If only a broad test finds a fault, add a unit test for it, unless broad tests are cheap. ^add-missing-unit-test
- Define in the team the name and the scope of each kind of test. ^agree-on-test-names
- Check that each layer of the suite holds fewer tests than the layer below it, unless broad tests are cheap. ^check-pyramid-shape
- Add a contract test for each interface between two services. ^contract-test-each-service-interface
- If lower-level tests cover each condition of a higher-level test, delete the higher-level test. ^delete-duplicate-high-test
- Limit end-to-end tests to the user journeys that define the core value of the product, unless broad tests are cheap. ^end-to-end-core-journeys
- Run the fastest tests in the earliest stage of the deployment pipeline. ^fast-tests-first
- If end-to-end tests outnumber unit tests, move their checks down the pyramid, unless broad tests are cheap. ^fix-ice-cream-cone
- If a suite holds fewer integration tests than end-to-end tests, add integration tests, unless broad tests are cheap. ^fix-test-hourglass
- Limit each higher-level test to the part that the lower-level tests do not cover. ^higher-test-covers-the-gap
- Do not use large tests as the main way to find bugs, unless broad tests are cheap. ^large-tests-are-not-the-net
- Write most automated tests as unit tests, unless broad tests are cheap. ^mostly-unit-tests
- Use the output of a record-playback tool only as a script fragment that you edit as code. ^no-record-playback-tests
- If broad tests are cheap, skip the lower-level tests of the behaviors that they cover. ^skip-low-tests-for-cheap-high-tests
- Write each test at the smallest size that checks its behavior, by its use of processes and machines. ^smallest-test-size
- Test each behavior at the lowest level of the pyramid that detects its failure, unless broad tests are cheap. ^test-at-lowest-level
- If a single page application behavior needs the real backend, test the backend part through its API. ^ui-backend-part-through-api
- In a single page application, test each user interface behavior with frontend unit tests, unless broad tests are cheap. ^unit-test-ui-behavior

## Definition

A model for the mix of automated tests in a suite, by the level of each test. Mike Cohn's original pyramid has 3 layers: unit tests at the wide base, service tests in the middle, and tests through the user interface at the narrow top. The ISTQB Foundation Level syllabus states the model in general terms: the higher the layer, the lower the granularity and the isolation of its tests, and the longer they run. So a suite holds many small, fast tests at the base and few broad tests at the top.

## Notes

The layers of the pyramid are the test levels, and each level has its own concept with the rules to write its tests:

- Unit testing checks one unit in isolation. ISTQB calls it component testing.
- Integration testing checks the interfaces between parts. A narrow integration test checks one integration point with test doubles for the rest.
- Contract testing checks that a test double still behaves like the real service.
- End-to-end testing checks the whole system through its user interface or through the API just below it.

The names differ from source to source, so a team states its own. A UI test is not the same as an end-to-end test: a test of the user interface can be a unit test with the backend replaced. This concept holds only the rules for the mix of tests across the levels.

Software Engineering at Google adds a second dimension. The size of a test is the resource that it uses: a small test runs in one process, a medium test on one machine, and a large test across machines. The scope of a test is the amount of code that it validates. Narrow scope and small size go together often, but not always. Google gives a rough mix of `80%` unit tests, `15%` integration tests, and `5%` end-to-end tests, by count. The mix of each team varies.

2 shapes show a suite that drifts from the pyramid. An ice cream cone holds many end-to-end tests and few unit tests. An hourglass holds many unit tests and many end-to-end tests, with few integration tests between them.

A broad test is a test above the unit level. Martin Fowler names 1 exception to the pyramid: if the high-level tests are fast, reliable, and cheap to modify, the lower-level tests are not necessary. The rules of this concept call broad tests cheap when they are as fast, as reliable, and as cheap to change as the unit tests of the same behavior.

This concept sets the level of each test that test-driven development writes. Performance testing is one kind of large test.
