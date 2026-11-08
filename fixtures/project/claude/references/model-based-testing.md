<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Model-based testing

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

From [Model-based testing](model-based-testing.md):

- Check the syntax, the meaning, and the fit of each model with reviews, tool checks, and model simulation. ^check-model-quality
- If one selection criterion does not cover each aspect of the test objectives, combine criteria. ^combine-selection-criteria
- Write a separate model for each aspect that the test objectives need, not `1` model for the whole system. ^focused-models
- Write the test model apart from the system design model, with a different author. ^independent-test-model
- If only the interface of the test object changes, update only the test adaptation layer, unless no adaptation layer exists. ^interface-change-in-adapter
- If only the interface of the test object changes and no adaptation layer exists, update the model. ^interface-change-without-adapter
- After each increment of the model, run its generated tests again. ^iterate-model-and-tests
- Link each model element to the requirements that it covers. ^link-model-to-requirements
- Keep in each model only the details that its test objectives need. ^model-abstraction-level
- Do not use model-based testing in place of the other test techniques. ^model-based-testing-complements
- Before you change a model work product, check the impact on the model, the selection criteria, and the adaptation layer. ^model-change-impact
- When you build a test model from a requirements model, add elements for unusual scenarios and error situations. ^model-error-situations
- Choose the focus of each model from its test objective, such as a state machine for responses in each state. ^model-from-the-test-objective
- Change the model, not the generated tests. ^model-is-the-master
- Before the team builds models, write the modeling guidelines. ^modeling-guidelines
- If the number of generated tests exceeds the test budget, change the test selection criteria. ^narrow-criteria-against-explosion
- Define measurable objectives for model-based testing before you choose a tool. ^objectives-before-tools
- Record each test selection criterion and the reason for it. ^record-selection-criteria
- If generated test scripts run in a chain, set the precondition of each script before its execution. ^set-script-preconditions

## Definition

A way to test that derives the test cases from a model of the system under test or of its environment. Utting, Pretschner, and Legeard give this definition in their taxonomy of model-based testing approaches. The ISTQB Model-Based Tester syllabus names the parts: the model, the test selection criteria that choose the tests from the model, the generated testware, and the test adaptation layer that connects the abstract tests to the real interfaces. SWEBOK v4 lists the approach as scenario-based testing.

## Notes

The ISTQB syllabus names 3 subjects of a model, and a model often combines them:

- A system model describes the system as it is intended to be, such as a state machine.
- An environment model, or usage model, describes the use of the system, such as a Markov chain.
- A test model describes the test cases and their expected results.

A model has 3 quality characteristics. Syntactic quality means that the model follows the rules of its language. Semantic quality means that its content is correct. Pragmatic quality means that it suits the test objective and the generator. The common mistakes are the wrong level of detail and one model that tries to cover everything.

The test selection criteria choose a subset of the tests that a model can generate. The families are model coverage, such as each state and transition, requirements coverage, data coverage with equivalence partitions and boundary values, random or stochastic walks, scenarios and patterns, and project information such as risk. The model is the master, and the tests are derived work products. A small change of the model can change the whole selection.

A model that the system design reuses without change gives verification tests only, and it copies each error of the design into the tests. The syllabus recommends separate models by different authors. A test adaptation layer turns the abstract tests into executable scripts. A change of the interface alone touches only that layer.

Model-based testing is used mostly at the system, system integration, and acceptance levels. It supports the black-box test techniques and does not replace them. Property-based testing uses a state machine model in a similar way for code with side effects.
