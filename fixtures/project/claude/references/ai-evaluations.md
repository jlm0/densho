<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# AI evaluations

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

From [AI evaluations](ai-evaluations.md):

- Set each success target from a benchmark, a prior experiment, or expert knowledge. ^achievable-success-targets
- Include tasks that require a behavior and tasks that prohibit it in each eval suite. ^balanced-eval-suites
- Make each grader reject a result that exploits a loophole in place of a solution of the task. ^bypass-resistant-graders
- Check the outcome of each trial, not the order of its tool calls. ^check-the-outcome
- Use a code-based grader for each eval result, unless the result has valid variations that no code check matches. ^code-graders-first
- Combine the automated evals with production monitoring and periodic human review. ^combine-evaluation-methods
- Before you use an LLM grader at scale, compare its grades with the grades of human experts. ^compare-llm-graders-with-experts
- Write the evals for a planned capability before the agent performs it. ^evals-before-capabilities
- Run the automated evals on each change of the agent and on each model upgrade. ^evals-on-each-change
- Add the failures that users report to the eval suite as tasks, first those with the highest impact. ^failures-into-eval-tasks
- If a grader rejects a valid solution or `2` domain experts disagree on a task verdict, change the eval. ^fix-unfair-evals
- State in the task description each condition that the grader checks. ^grader-checks-in-the-task
- After the agent launches, move each capability eval that reaches a `100%` pass rate into the regression suite. ^graduate-capability-evals
- Start each trial from a clean environment with no state from other trials. ^isolated-trials
- If an eval result has valid variations that no code check matches, use an LLM grader, not a human grader. ^llm-grader-for-complex-judgment
- Monitor each capability eval for saturation. ^monitor-eval-saturation
- Define success criteria for each dimension of the feature, such as task fidelity, consistency, latency, and price. ^multidimensional-success-criteria
- Run more than `1` trial of each eval task. ^multiple-trials
- Before you deploy a model, test it offline against its required conditions, such as with cross-validation. ^offline-tests-before-deployment
- Use a separate LLM grader for each dimension of a task. ^one-llm-grader-per-dimension
- After you deploy a model, test it online to check how it interacts with the behavior of its users. ^online-tests-after-deployment
- Assign an owner to the infrastructure of the eval suites. ^owner-for-eval-infrastructure
- For a task with more than `1` component, give partial credit for each component. ^partial-credit
- If the product accepts `1` success in `k` attempts, measure `pass@k`. ^pass-at-k-for-one-success
- If the product requires consistent behavior on each attempt, measure `pass^k`, not `pass@k`. ^pass-power-k-for-consistency
- Make the agent in the eval behave like the agent in production. ^production-like-agent
- Read a sample of the transcripts before you accept an eval score. ^read-transcripts
- Make the eval tasks match the real distribution of tasks, including the edge cases. ^real-task-distribution
- Make each LLM grader reason before it gives a score. ^reasoning-before-grades
- Write a reference solution for each eval task that passes each grader. ^reference-solutions
- Treat each decrease in the pass rate of a regression eval as a defect. ^regression-eval-pass-rate
- Give each LLM grader a rubric that states each pass condition, and a fixed scale, such as `correct` or `incorrect`. ^rubrics-for-llm-graders
- Keep the capability evals and the regression evals in separate suites. ^separate-capability-and-regression
- Use a different model for the LLM grader than the model that generated the output. ^separate-grader-model
- Define each success criterion of an AI feature as a named metric, a threshold, and its test set. ^specific-success-criteria
- Start the eval suite with `20` to `50` tasks from manual checks, common user tasks, and failure reports from production. ^tasks-from-real-failures
- In an eval of a coding agent, check correctness with unit tests and code quality with an LLM rubric. ^tests-for-coding-agents
- Make each eval task specific enough that `2` domain experts give it the same verdict. ^unambiguous-eval-tasks
- Give each LLM grader an option to return `Unknown` when it lacks information. ^unknown-option-for-llm-graders
- Choose more test cases with automated grading, not fewer test cases with human grading. ^volume-over-hand-grading
- If a frontier model fails each of `100` trials of a task, check the task and its graders for defects. ^zero-pass-rate-is-a-broken-task

## Definition

A test of an AI system: the test gives the system an input, and applies grading logic to its output to measure success. Anthropic's engineering post on evals for AI agents gives this definition, and names the parts: a task with defined inputs and success criteria, a trial for each attempt, a grader that scores the result, the transcript of each trial, and the outcome in the environment. Anthropic's guide on success criteria starts from criteria that are specific and measurable, and builds evals that mirror the real distribution of tasks. SWEBOK v4 lists the testing of AI and machine learning systems as an emerging area, with offline testing before deployment and online testing after it.

## Notes

Anthropic names 3 types of grader:

- A code-based grader is the fastest and the most reliable, and it scales. It includes string matches, binary tests, static analysis, and checks of the tool calls. It is brittle to valid variations of an answer.
- A model-based grader, or LLM grader, is fast, flexible, and suitable for complex judgment. It needs calibration with human graders.
- A human grader is the most flexible and gives high quality, but it is slow and expensive. Anthropic uses human graders to calibrate LLM graders.

A task can combine graders. Its score can be weighted, binary, or a hybrid of the 2.

Agent behavior varies between runs, so 1 trial gives a noisy result. `pass@k` is the chance of at least 1 success in k trials, and it rises with k. `pass^k` is the chance that each of k trials succeeds, and it falls with k. With a `75%` success rate per trial, `pass^3` is about `42%`. A tool where 1 success is enough uses `pass@k`. A customer-facing agent uses `pass^k`.

A capability eval asks what the agent can do well, and starts at a low pass rate. A regression eval asks whether the agent still handles the tasks that it handled before. A capability eval at `100%` gives no signal for improvement. After the agent launches, a capability eval with a high pass rate can move to the regression suite.

Grading defects can hide a capable agent. Anthropic reports a benchmark where a model first scored `42%`. A researcher found rigid grading, ambiguous tasks, and tasks that no run could reproduce exactly. After the fixes and a less constrained scaffold, the score rose to `95%`. With frontier models, a pass rate of `0%` across many trials is most often a sign of a broken task, not of an incapable agent.

Automated evals are 1 layer among several: production monitoring, A/B tests, user feedback, transcript review, and human studies. Each layer catches failures that the others miss.
