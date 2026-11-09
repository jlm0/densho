<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Mutation testing

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

From [Mutation testing](mutation-testing.md):

- Compute the mutation score as the killed mutants divided by the mutants that are not equivalent. ^compute-mutation-score
- Exclude each equivalent mutant from the mutation score. ^exclude-equivalent-mutants
- Add a test for each surviving mutant that is productive. ^kill-productive-mutants
- Show each surviving mutant in the code review of the change. ^mutants-in-code-review
- Generate mutants only for the changed lines of a change that the tests cover. ^mutate-changed-covered-lines
- Use mutation testing to check whether the tests assert on the code that coverage marks as covered. ^mutation-after-coverage
- Make each mutant with `1` small syntactic change to the program. ^one-change-per-mutant
- Generate at most `1` mutant for each line. ^one-mutant-per-line
- Report the surviving mutants of each change, not a mutation score of the whole code base. ^report-change-mutants
- Use only the ABS, AOR, LCR, ROR, and UOI mutation operators. ^selective-mutation-operators
- Do not generate mutants in logging code, test code, or code that controls only non-functional properties, such as memory reservation. ^skip-arid-code
- Do not add a test that kills a mutant through an assertion on an implementation detail, not on the specification. ^skip-unproductive-mutants
- Use the feedback of the developers on each shown mutant to suppress the kinds that they mark as not useful. ^suppress-by-feedback
- Before you run the mutants, check that each test passes on the original program. ^tests-pass-before-mutation

## Definition

A fault-based technique that measures how well a test set detects faults. Jia and Harman describe the process: small syntactic changes seed faults into the program, and each changed copy is a mutant. A test set kills a mutant when a test gives a different result on the mutant than on the original program. The mutation score is the ratio of killed mutants to the mutants that are not equivalent to the original. Petrović and colleagues at Google separate mutation analysis, which measures a test suite, from mutation testing, which uses each surviving mutant as the goal of a new test.

## Notes

Mutation testing rests on 2 hypotheses that Jia and Harman describe. The competent programmer hypothesis states that programmers write code close to the correct version, so real faults are small. The coupling effect states that a test set that detects each simple fault also detects most complex faults. In the studies that they cite, tests that killed each first-order mutant also killed over `99%` of the second-order and third-order mutants.

The process has 4 steps: generate the mutants with mutation operators, run the tests on the original program, run the tests on each mutant, and add tests for the mutants that survive. An equivalent mutant changes the code but not its behavior, so no test can kill it. The detection of equivalent mutants is undecidable in general, and it costs human effort.

A full mutation analysis is costly in machines and in human attention. Selective mutation uses a few operators: the 5 key operators of Offutt and colleagues kept a mutation score of `99.5%`. Google implements AOR, LCR, ROR, SBR, and UOI. It leaves out ABS, because ABS acted on values that are never negative in its code, and it states that this reason does not apply in general. Google makes the technique practical at scale with 3 limits:

- It mutates only the changed lines that the tests cover, during code review.
- It generates at most 1 mutant for each line.
- It skips arid code, where each mutant would be unproductive.

An unproductive mutant is equivalent to the original, or a test that kills it does not improve the suite. Such a test asserts on an implementation detail, such as the initial capacity of a collection, and not on the specification. At Google, developers first marked `85%` of the shown mutants as unproductive. Suppression based on their feedback raised the share of productive mutants from `15%` to `89%`.

Code coverage shows which lines the tests execute. Mutation testing shows whether the tests detect a change in those lines.
