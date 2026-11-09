<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software testing

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Software testing](software-testing.md):

- If no time or budget remains, end the testing early only with the risk acceptance of the stakeholders. ^accepted-risk-for-early-exit
- After test completion, add a backlog item for each unresolved defect. ^backlog-item-for-open-defects
- During test analysis, check the testability of the test basis and the test object. ^check-testability
- Choose the inputs of each test with a test technique. ^choose-inputs-with-a-technique
- Choose the level of each new test with the test pyramid. ^choose-level-with-the-pyramid
- Combine the black-box test techniques with code coverage. ^combine-functional-and-structural
- Commit the automated tests with the source code that they test. ^commit-tests-with-code
- Use the interface contract and the UI contract of each part as the test basis of its tests. ^contracts-as-test-basis
- Use the observed defect clusters as an input to the product risk analysis. ^defect-clusters-into-risk
- Record the test object, steps, expected and actual results, and severity of each test failure in its defect report. ^defect-report-contents
- Define the entry criteria and the exit criteria of each test level in the test plan. ^entry-and-exit-criteria
- In Agile development, use the exit criteria of the tests as the Definition of Done of each releasable item. ^exit-criteria-as-definition-of-done
- Define the expected result of each test before you run it. ^expected-result-for-each-test
- If the oracle gives no verdict, record the result as inconclusive, not as a pass. ^inconclusive-results
- Before you end a test level, measure its coverage of the product risks, the requirements, and the acceptance criteria. ^measure-exit-coverage
- Select the tests with test techniques, priorities, and risks, not with exhaustive testing. ^no-exhaustive-testing
- Do not put a conditional or a loop in an example-based test, unless the loop polls for an asynchronous result. ^no-logic-in-tests
- Do not treat an automatic rerun of a flaky test as a fix of its cause. ^no-rerun-for-flaky-test
- Do not treat a passing test suite as proof that the code has no defects. ^passing-tests-are-not-proof
- Set the test levels, the test techniques, and the coverage targets from the product risk analysis. ^product-risk-sets-scope
- If the existing tests stop finding new defects, add new tests. ^refresh-worn-out-tests
- Write a defect report for each anomaly of a test run after you analyze its cause. ^report-each-defect
- Write a defect report for each defect that test analysis finds in the test basis, unless you fix it directly. ^report-test-basis-defects
- Review the specification for ambiguities, gaps, and contradictions before you write its tests. ^review-the-test-basis
- Split each test into its setup, its action, and its verification. ^setup-action-verification
- Do not write a test for code without conditional logic, such as a plain getter or setter. ^skip-trivial-code
- Run static analysis of the source code before the dynamic tests. ^static-analysis-first
- Include a test that reproduces the bug in each bug fix. ^test-before-bug-fix
- Test each unit through its public interface, unless a property checks the invariant of its representation. ^test-public-interface
- Write the tests of each behavior before construction writes its code. ^tests-before-code
- Run the automated component tests and the automated regression tests on each commit in continuous integration. ^tests-in-continuous-integration
- Link each test case to each element of the test basis that it covers. ^trace-tests-to-the-basis

From [Accessibility](accessibility.md):

- Run each single-pointer action on the up event, not on the down event. ^act-on-pointer-up
- Give the user a way to disable, change, or extend each time limit, unless the limit exceeds `20` hours. ^adjustable-time-limits
- Do not block paste or password autofill in a login field. ^allow-paste-in-login
- Keep each text visible when a user raises its line, paragraph, letter, or word spacing. ^allow-text-spacing
- Give each prerecorded silent video a text alternative or an audio track, unless it is a labeled alternative for text. ^alternative-for-silent-video
- Give a way to bypass each block of content that repeats across pages. ^bypass-repeated-blocks
- Give captions to each live video with sound. ^caption-live-video
- Give captions to each prerecorded video with sound, unless the video is a labeled alternative for text. ^caption-prerecorded-video
- Give each single-character keyboard shortcut a setting to disable it or change its key, unless it works only on focus. ^character-key-shortcuts
- Keep each repeated help mechanism, such as contact details or a chat, in the same relative order on each page. ^consistent-help-order
- Give components with the same function the same label and the same glyph on each page. ^consistent-identification
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components
- Declare the purpose of each field that collects data about the user, such as with `autocomplete`. ^declare-input-purpose
- Declare the main language of each page in the code. ^declare-page-language
- Declare the language of each passage in another language, unless it is a name or a technical term. ^declare-passage-language
- When a check finds an input error, describe the error and its field in text. ^describe-input-error
- Give each prerecorded video an audio description of the visual content that its soundtrack does not state. ^describe-prerecorded-video
- Make each heading and label state the topic or the purpose of its content. ^descriptive-headings-and-labels
- Give each page a title that states its topic or purpose. ^descriptive-page-title
- Make content that appears on hover or focus dismissible without moving the pointer or the focus. ^dismissible-hover-content
- Give each drag action a single-pointer alternative that needs no drag, unless dragging is essential. ^drag-alternative
- Expose each status message to assistive technology without moving the focus to it. ^expose-status-messages
- Do not hide the focused control completely behind a sticky header, a banner, or another element. ^focus-not-obscured
- Hide each decorative image from assistive technology. ^hide-decoration
- Keep content that appears on hover visible while the pointer moves over that content. ^hoverable-content
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
- Give each input field a label or an instruction. ^label-each-field
- Include the visible label text of each control in its accessible name. ^label-in-name
- State the purpose of each link in its text or in the sentence that holds it. ^link-purpose
- Set a focus order that keeps the meaning and the operation of the content. ^logical-focus-order
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
- Give each action that a device motion starts an on-screen control and a setting that disables the motion. ^motion-alternative
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
- Expose the name, the role, and the state of each custom control to assistive technology. ^name-role-value
- Do not change the context when a control receives focus. ^no-change-on-focus
- Do not change the context when a user changes a setting, unless the control warns of it first. ^no-change-on-input
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Do not show content that flashes more than `3` times in any `1` second. ^no-flashing-content
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap
- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock
- Do not require a puzzle or a memory test for authentication, unless another method needs neither. ^no-puzzle-login
- Do not ask a user to type again a value that they entered earlier in the same process. ^no-redundant-entry
- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions
- Give a control to pause or hide each automatic update that runs in parallel with other content. ^pause-auto-updates
- Give a pause control to each audio that plays automatically for more than `3` seconds. ^pause-autoplay-audio
- Give a pause control to each moving or blinking content that starts automatically and lasts over `5` seconds. ^pause-moving-content
- Keep hover and focus content visible until the hover or the focus ends, or the user dismisses it. ^persistent-hover-content
- Keep the order of the content in the code the same as its visual reading order. ^reading-order-in-code
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Give a review step before each payment, each legal agreement, and each deletion of user data, unless it is reversible. ^review-before-commitment
- Give each action that a multipoint or path-based gesture does a single-pointer alternative, unless the gesture is essential. ^single-pointer-alternative
- Use the element or role that matches the visual structure of each heading, list, table, and form label. ^structure-in-code
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Give each meaningful image a text alternative. ^text-alternative
- Give each prerecorded audio-only clip a transcript, unless the clip is a labeled alternative for text. ^transcript-for-audio-only
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page

## Definition

The dynamic validation that a system under test gives the expected behavior on a finite set of test cases, selected from a domain of executions that is usually infinite. SWEBOK v4 gives this definition. The ISTQB Foundation Level syllabus adds static testing, and splits the test process into planning, monitoring and control, analysis, design, implementation, execution, and completion. Here, testing turns the contracts of software design into automated tests, and construction writes the code that passes them.

## Notes

The ISTQB syllabus states 7 principles of testing:

- Testing shows the presence of defects, not their absence.
- Exhaustive testing is impossible, except in trivial cases.
- Early testing saves time and money.
- Defects usually cluster in a small number of components.
- Tests wear out: the same tests find fewer new defects each time.
- Testing depends on its context.
- A system without known defects can still fail the needs of its users.

An error of a person produces a defect, and a defect that runs can cause a failure. A test oracle decides whether a test passes or fails. When the oracle cannot decide, the result is inconclusive.

The testing quadrants of Brian Marick group the tests in 2 dimensions. A test faces the business or the technology, and it supports the team or critiques the product. Unit and component integration tests support the team from the technology side, and they run in continuous integration. Functional tests and examples support the team from the business side. Exploratory, usability, and acceptance tests critique the product from the business side. Performance tests and other non-functional tests critique the product from the technology side. In the whole team approach, each member of the team shares the responsibility for quality.

A flaky test passes and fails on the same code. Software Engineering at Google reports that as a suite approaches a flaky rate of `1%`, its tests begin to lose value.

The coverage of this practice area follows 2 anchors: the ISTQB Certified Tester Foundation Level syllabus `v4.0.1` and chapter 5 of SWEBOK `v4`.

- The directives of this practice area cover the principles, the test activities, traceability, shift left, product risk, the oracle, the defect report, and the exit gate.
- The concepts cover the test levels, the test mix, test-driven development, test doubles, contract testing, black-box test techniques, property-based testing, model-based testing, code coverage, mutation testing, regression testing and flaky tests, performance testing, and AI evaluations.
- Other practice areas hold acceptance testing, exploratory testing, code review, and the definition of done (software quality). They also hold security and privacy testing (software security), usability testing (user research), requirements traceability and specification by example (software requirements), and configuration management.
- Test management stays out: planning, estimation, monitoring, roles, and staffing. The tree holds no node for it.
- Experience-based techniques, such as error guessing and checklists, stay with exploratory testing in software quality.
- The non-functional types other than performance stay out. The sources give no rules that an agent can apply alone.
- Syntax testing, cause-effect graphing, domain-specific testing, and test tools stay out. SWEBOK names cause-effect graphing as a technique related to decision tables.

## Comes from

The output of each node in this list is an input of this node.

- [Software design](software-design.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software construction](software-construction.md)

## References

- You test the output of an AI model or an AI feature. Read [AI evaluations](ai-evaluations.md).
- You choose the test inputs for a behavior from its specification. Read [Black-box test techniques](black-box-test-techniques.md).
- You measure the code coverage of a test suite. Read [Code coverage](code-coverage.md).
- A test uses a test double for another service. Read [Contract testing](contract-testing.md).
- A test runs the whole deployed system through its user interface or its public API. Read [End-to-end testing](end-to-end-testing.md).
- A test connects the code to a database, a file system, a queue, or another service. Read [Integration testing](integration-testing.md).
- You generate tests from a model of the system under test. Read [Model-based testing](model-based-testing.md).
- You check whether the tests detect a change in the covered code. Read [Mutation testing](mutation-testing.md).
- You test the response time, the throughput, or the capacity of a system under load. Read [Performance testing](performance-testing.md).
- You write a test that generates its own input values. Read [Property-based testing](property-based-testing.md).
- You run the existing tests again after a change to the code. Read [Regression testing](regression-testing.md).
- A test replaces a dependency with a stub, a mock, or a fake. Read [Test doubles](test-doubles.md).
- You write the code for a new behavior. Read [Test-driven development](test-driven-development.md).
- You choose the level of a new test. Read [Test pyramid](test-pyramid.md).
- You write a test for one function, one class, or one module. Read [Unit testing](unit-testing.md).
