<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Code coverage

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

From [Code coverage](code-coverage.md):

- Make the coverage of the changed lines of each commit meet its per-commit coverage goal. ^cover-changing-code
- Block a change when it drops the coverage below the gate that the team chose. ^coverage-gate
- Show the coverage of each changed line in the code review of the change. ^coverage-in-code-review
- Do not treat a high coverage percent as proof that the tests check the behavior. ^coverage-is-not-quality
- Do not treat full code coverage as proof that the code implements each requirement. ^coverage-misses-omissions
- Exclude each infeasible path from the target of path coverage. ^exclude-infeasible-paths
- Use the coverage report to find the code that no test executes. ^find-untested-code
- Measure branch coverage, not only statement coverage. ^measure-branch-coverage
- Measure the coverage automatically for each change in code review and for each project. ^measure-coverage-automatically
- Do not add a copied test or a test without an assertion only to reach a coverage target. ^no-tests-for-the-number
- If the team sets a coverage goal for each commit, set its lower threshold at `90%` or more. ^per-commit-coverage-floor
- When you change a file with coverage below the target of its code base, raise its coverage. ^raise-coverage-on-change
- In a code review, review the risk of each changed line that no test executes. ^review-uncovered-lines
- In safety-critical or mission-critical code, use a coverage criterion more rigorous than branch coverage. ^stronger-criteria-for-critical-code
- Set the coverage target of a code base at `90%` or less, by its business impact, change rate, and lifetime. ^target-by-impact-and-change
- Treat a coverage target as a floor, not as a ceiling. ^target-is-a-floor

## Definition

A measure of the degree to which a test suite exercises the code of a system. Ivanković and colleagues give this definition in "Code Coverage at Google". The ISTQB Foundation Level syllabus treats it as the target of the white-box test techniques: statement coverage is the share of the executable statements that the tests exercise, and branch coverage is the share of the branches. SWEBOK v4 names further criteria, such as condition, MC/DC, path, and data flow coverage.

## Notes

Branch coverage subsumes statement coverage: a test set with `100%` branch coverage also has `100%` statement coverage, but not the other way round. SWEBOK v4 also names condition, decision, and MC/DC coverage, and calls path coverage the strongest control flow criterion. Loops make full path coverage infeasible, so the less stringent criteria limit the loop iterations. Data flow criteria follow each variable from its definition to its use.

Coverage shows which code ran, not whether a test checked its result. A test can execute a line without an assertion on it. A statement with a data-dependent defect, such as a division by zero, can run without a failure. Code that does not implement a requirement has no line to cover, so white-box testing can miss defects of omission. Mutation testing checks whether the tests detect a change in the covered code.

The Google Testing Blog gives rough guidelines: `60%` is acceptable, `75%` is commendable, and `90%` is exemplary. It states that a project-wide target above `90%` is most likely not worth the cost, while a target of `99%` for each commit is reasonable. Software Engineering at Google warns that a fixed target such as `80%` turns into a ceiling. The 2 Google sources differ on the scope of the measure. The book measures coverage only from small tests, to avoid inflation. The blog adds the coverage of the integration and end-to-end tests, and warns that part of it is incidental.
