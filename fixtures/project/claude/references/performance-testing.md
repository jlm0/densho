<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Performance testing

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

From [Performance testing](performance-testing.md):

- Keep each operational profile broad until a test objective requires more detail. ^broad-operational-profiles
- In each performance test script, check the content of each response, not only its status code. ^check-performance-responses
- Choose the type of each performance test from its objective: load, stress, scalability, spike, endurance, concurrency, or capacity. ^choose-performance-test-type
- If a baseline test exists, compare the results of each later performance test with its results. ^compare-with-a-baseline
- After a performance fix, repeat the performance test to confirm the fix. ^confirm-performance-fixes
- If a test objective covers degradation over time, such as from a memory leak, run an endurance test. ^endurance-for-degradation
- Test the error handling of the system at its load limits and above them. ^error-handling-under-load
- Find the root cause of each failed transaction before you use the throughput results. ^failed-transactions-first
- Choose only the performance metrics that support a test objective and that the test tools collect and report consistently. ^limit-performance-metrics
- Build each load profile from the test objective, the operational profiles, and the distribution of the load over time. ^load-profiles
- Record the start, the duration, the scripts, the data, the configuration, and the defects of each test run. ^log-each-performance-run
- Measure the performance in the steady state after the ramp-up, unless the test targets a transient state. ^measure-in-steady-state
- Before a performance test, define the measurements and the metrics that show whether the test meets its objectives. ^metrics-before-performance-tests
- Monitor each load generator during the test. ^monitor-load-generators
- After each delivery, monitor the performance of the system in production. ^monitor-performance-after-delivery
- Do not require `100%` of the transactions to meet a performance objective. ^no-full-compliance-goal
- If users interact with the system, define each operational profile from their roles, tasks, and numbers in each period. ^operational-profiles
- Set each response time goal at the `90th` percentile. ^percentile-response-goals
- In continuous integration, make each performance test raise an alert when its results leave the expected range. ^performance-alerts-in-ci
- Write the performance criteria of each user story with a performance risk into its acceptance criteria. ^performance-in-acceptance-criteria
- If a subset of the performance tests runs at build level, run that subset in continuous integration. ^performance-subset-in-ci
- Define the objectives of each performance test with its stakeholders, as user-based objectives or technical objectives. ^performance-test-objectives
- Start dynamic performance tests in the first iterations, not in the final iterations. ^performance-tests-early
- Make the performance test environment match production in data, hardware, software, and network, unless no match is possible. ^production-like-environment
- If the test environment differs from production, find each difference and its effect on the projection of the results. ^record-environment-differences
- Report the results of each performance test against the objectives in its test plan. ^report-against-objectives
- Require repeated runs of a performance test on an unchanged system to give results within a stated tolerance. ^reproducible-performance-results
- If a performance test changes the system state, restore the original state before the next run. ^restore-state-before-repeat
- Review each operational profile with the stakeholders before you build a load profile from it. ^review-operational-profiles
- Review the requirements, the data schemas, the architecture, and the code for performance risks. ^static-performance-reviews
- Give each virtual user a different set of test data, not the recorded data of `1` user. ^test-data-per-virtual-user
- Test each performance test script with the full range of its input data. ^test-performance-scripts
- Set the think times of each script to match the throughput of its operational profile. ^think-times-from-profiles
- Put a timer around each business transaction in a performance test script. ^time-each-transaction
- Set the clocks of each test tool and each monitoring tool from `1` time source. ^time-source-for-tools
- When you test a transient state, such as a spike, do not monitor only the averages. ^transient-states-without-averages
- Before a performance test, validate the environment and the monitoring with a controlled set of tests. ^validate-the-test-setup
- Before you read the response times, check that each virtual user finished the tasks of its profile. ^virtual-users-first

## Definition

Testing that checks the performance of a system or a component under different volumes of load. The ISTQB Performance Testing syllabus calls it an umbrella term for each kind of test that focuses on responsiveness, and follows ISO 25010 with 3 parts: time behavior, resource utilization, and capacity. SWEBOK v4 lists performance testing as non-functional testing: it checks that the software meets its specified performance requirements, and it measures characteristics such as capacity and response time.

## Notes

The ISTQB syllabus names 7 types of performance test:

- A load test checks the system under increasing levels of realistic load.
- A stress test checks the system at its peak load or beyond it, or with fewer resources.
- A scalability test checks whether the system can grow beyond its current requirements.
- A spike test checks the response to a sudden burst of load, and the return to a steady state.
- An endurance test checks the stability of the system over a long period, and finds leaks of memory, connections, or threads.
- A concurrency test checks what happens when specific actions occur at the same time.
- A capacity test finds how many users or transactions the system supports within its objectives.

An operational profile describes how 1 kind of user or system uses the system under test. A load profile combines the operational profiles with a number of virtual users and a distribution over time, such as a ramp-up, a step, or a daily cycle.

The syllabus names 4 common failure modes. The response is slow at each load level, from causes such as a bad database design. The response is slow under moderate or heavy load, from a saturated resource. The response degrades over time, from a memory leak or data growth. The error handling degrades at high load, from small resource pools, small queues, or short timeouts.

The syllabus warns about 2 traps of recorded scripts. Virtual users that share 1 set of data can hit a cache and give results better than production. They can also wait on the same locks and give results worse than production. Performance is a non-linear function of the environment, so a projection from a small environment to production is less reliable as the gap grows.

The average response time can hide outliers, so the 90th percentile is often used as the goal. A failed transaction takes less time than a successful one, so a failure can inflate the throughput.
