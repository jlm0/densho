<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Property-based testing

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

From [Property-based testing](property-based-testing.md):

- If a property has a precondition, check the share of trivial cases among the tested cases. ^check-trivial-cases
- Make each generator able to produce each valid test case. ^complete-generators
- If a precondition rejects most generated inputs, write a generator that produces only valid inputs. ^generators-for-preconditions
- Measure the distribution of the generated cases with labels. ^measure-the-distribution
- If the expected result needs a copy of the implementation, write metamorphic properties that relate the results of `2` calls. ^metamorphic-properties
- If the model is costly or resembles the implementation, write metamorphic properties in place of model-based properties. ^metamorphic-when-the-model-is-costly
- Write the model-based and validity properties first, unless the model is costly or resembles the implementation. ^model-based-properties-first
- Do not copy the implementation into a property to compute the expected result. ^no-reimplementation-in-properties
- In a postcondition, check the result of a single call against its arguments. ^postcondition-properties
- Write each property as a statement that holds for each valid input, not for one example. ^properties-not-examples
- Write the properties against the exported API, unless a property checks the invariant of the representation. ^properties-through-the-api
- If most generated cases miss the behavior that a property checks, change the generator. ^rebalance-the-generator
- Use a tool that shrinks each failing case to a minimal counterexample. ^shrink-failing-cases
- If the code under test has side effects, test sequences of operations against a state machine model. ^state-machine-properties
- Test that each generator and each shrinker produce only valid values. ^test-generators-and-shrinkers
- If a data type has an invariant, write a validity property that each operation keeps the invariant. ^validity-properties

## Definition

A way to test code by stating general properties that the code must hold, and by checking them on generated test cases. John Hughes describes it in "How to Specify It!": the tool generates the cases, usually at random, and reports a minimized failing case when a property does not hold. Claessen and Hughes introduced the approach with QuickCheck in 2000, and joined 2 older ideas: specifications as test oracles, and random testing. David MacIver adds that the person designs the property, and the tool only fuzzes it.

## Notes

Hughes names 5 kinds of property, and a pitfall for each:

- A validity property checks that each operation keeps the invariant of a data type. Validity alone is weak: a function that always returns an empty value keeps the invariant.
- A postcondition relates the result of 1 call to its arguments.
- A metamorphic property relates the results of 2 related calls, such as an insert before and after a union. It needs no expected value, so it solves the oracle problem in many cases.
- An inductive property relates a call to calls with smaller arguments. A complete set of inductive properties gives a proof of correctness.
- A model-based property compares the result of 1 call with the result of a simpler abstract operation on a model.

In the comparison of Hughes, model-based properties found each seeded bug with few properties. Metamorphic properties were almost as effective, but they need more properties.

A generator produces the test cases, and a shrinker turns a failing case into a smaller one. Shrinking gives a counterexample in which each part matters to the failure. The QuickCheck paper shows a common failure: a precondition such as "the list is ordered" skews the generated cases toward short lists, so most tests check almost nothing. A label on each case shows the distribution, and a custom generator corrects it.

Property-based testing is not the same as fuzzing. MacIver defines fuzzing as feeding code data from a large corpus to see whether it fails. A property-based test adds the properties that a person writes, so a failure shows a problem that plain fuzzing does not find. Security fuzzing belongs to software security. Black-box test techniques choose the test values by hand, and property-based testing generates them.
