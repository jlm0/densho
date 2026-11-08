<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Black-box test techniques

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

From [Black-box test techniques](black-box-test-techniques.md):

- In mission-critical or safety-critical software, test each valid transition and each invalid transition of the state table. ^all-transitions-for-critical-software
- In mission-critical software, raise the interaction strength above `2` until the `t`-way tests detect no failure. ^beyond-pairs-for-critical-software
- Use boundary value analysis only for ordered partitions. ^boundaries-of-ordered-partitions
- If the test budget covers only part of a decision table, test the minimized table in order of risk. ^choose-columns-by-risk
- Define each invalid combination of values as a constraint of the covering array. ^constraints-for-invalid-combinations
- Write each combination of conditions as a column of the decision table, with its actions. ^decision-table-columns
- If a requirement maps combinations of conditions to different outcomes, write a decision table for it. ^decision-table-for-combinations
- Write each condition and each action of the system as a row of the decision table. ^decision-table-rows
- Define the equivalence partitions of each input, output, and configuration value of the test object. ^define-equivalence-partitions
- When you simplify a decision table, delete each column that holds an infeasible combination of conditions. ^delete-infeasible-columns
- If a test object has more than `1` input, test each partition of each input in at least `1` test. ^each-choice-coverage
- Do not delete a test with an invalid combination from a covering array, unless other tests cover its valid combinations. ^keep-covering-array-tests
- Keep each black-box test when the implementation changes and the required behavior stays the same. ^keep-tests-across-implementations
- Limit each parameter of a combinatorial test to `10` values, unless the values for its partitions and boundaries exceed `10`. ^limit-values-per-parameter
- Test at most `1` invalid transition in each test case. ^one-invalid-transition-per-test
- In a combinatorial test, test at least each pair of parameter values with a covering array. ^pairwise-covering-array
- Define the partitions of a value range from the specification, not from evenly spaced points of the range. ^partitions-from-the-specification
- Make the partitions of each data element non-empty and without overlap. ^partitions-without-overlap
- For each boundary, test the boundary value and both of its neighbors. ^prefer-three-value-boundaries
- Record each gap and each contradiction in the requirements that the decision table shows. ^record-requirement-gaps
- Measure the coverage of each technique as the percent of its coverage items that the tests exercise. ^record-technique-coverage
- If events move the test object between states, write a state table of its states and transitions. ^state-table-for-history
- Test each boundary value of an ordered partition and its closest neighbor in the next partition. ^test-each-boundary
- Test each feasible column of the decision table, unless the test budget covers only part of the table. ^test-each-column
- Test at least `1` value from each equivalence partition, including each invalid partition. ^test-each-partition
- When you test the robustness of a program, include values outside its input domain in the boundary tests. ^test-outside-the-domain
- Build each black-box test from the specified behavior of the test object, not from its code. ^test-the-specified-behavior
- Test each valid transition of the state table at least once. ^valid-transitions-coverage

## Definition

Techniques that select test cases from the specified behavior of the test object, without reference to its internal structure. The ISTQB Foundation Level syllabus names 4: equivalence partitioning, boundary value analysis, decision table testing, and state transition testing. SWEBOK v4 calls them specification-based techniques, and adds combinatorial testing, such as pairwise testing. Each technique defines its coverage items, and its coverage is the share of those items that the tests exercise.

## Notes

Each technique has its own coverage items:

| Technique                 | Coverage items                                                              |
| ------------------------- | --------------------------------------------------------------------------- |
| Equivalence partitioning  | The partitions, valid and invalid                                           |
| 2-value boundary analysis | Each boundary value and its closest neighbor in the next partition          |
| 3-value boundary analysis | Each boundary value and both of its neighbors                               |
| Decision table testing    | The feasible columns                                                        |
| State transition testing  | All states, the valid transitions, or all transitions with invalid ones     |
| Combinatorial testing     | Each combination of `t` parameter values, such as each pair when `t` is `2` |

The ISTQB syllabus ranks the state transition criteria. Valid transitions coverage is the most widely used, and it implies all states coverage. All transitions coverage implies both, and the syllabus sets it as the minimum for mission-critical and safety-critical software. 3-value boundary analysis can find defects that 2-value analysis misses, such as `x = 10` in place of `x <= 10`.

NIST SP 800-142 states the interaction rule from fault studies: most failures come from 1 parameter or the interaction of 2, and fewer come from 3 or more. In the studies, tests of all 4-way to 6-way combinations found each fault. Pairwise testing can miss `10%` to `40%` or more of the faults of a system. A covering array holds each `t`-way combination in few tests. A constraint keeps an invalid combination out of the array. The tool still covers each valid combination that a deletion of tests would lose.

Black-box tests do not depend on the code, so they stay useful when the implementation changes and the required behavior stays the same. White-box tests check the structure, and code coverage holds their rules. The 2 kinds find different defects. Property-based testing generates the input values at random, and model-based testing generates the tests from a model, such as a state machine.
