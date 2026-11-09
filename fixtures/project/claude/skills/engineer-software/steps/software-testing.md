<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software testing

This file is step 4 of 8 of the skill `engineer-software`.

## Directives

From [AI evaluations](../../../references/ai-evaluations.md):

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

From [Black-box test techniques](../../../references/black-box-test-techniques.md):

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
- Record each gap and each contradiction in the requirements that the decision table shows. ^record-requirement-gaps
- Measure the coverage of each technique as the percent of its coverage items that the tests exercise. ^record-technique-coverage
- If events move the test object between states, write a state table of its states and transitions. ^state-table-for-history
- Test each boundary value of an ordered partition and its closest neighbor in the next partition. ^test-each-boundary
- Test each feasible column of the decision table, unless the test budget covers only part of the table. ^test-each-column
- Test at least `1` value from each equivalence partition, including each invalid partition. ^test-each-partition
- When you test the robustness of a program, include values outside its input domain in the boundary tests. ^test-outside-the-domain
- Build each black-box test from the specified behavior of the test object, not from its code. ^test-the-specified-behavior
- For each boundary, test the boundary value and both of its neighbors. ^three-value-boundaries
- Test each valid transition of the state table at least once. ^valid-transitions-coverage

From [Code coverage](../../../references/code-coverage.md):

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

From [Contract testing](../../../references/contract-testing.md):

- Assert only on the fields that affect the consumer when they change. ^assert-consumer-fields-only
- Send each call from a consumer to a provider through a client that the contract tests cover. ^calls-through-the-tested-client
- Before a consumer or a provider deploys, check that its version passed verification with each version in the target environment. ^can-i-deploy
- If the consumers of an API are unknown, do not use consumer-driven contracts. ^cdc-needs-known-consumers
- If a stub holds a snapshot, check field formats, not field content, unless the consumer depends on that content. ^check-format-not-data
- In a consumer contract, state only the parts of the provider contract that the consumer uses. ^consumer-states-what-it-uses
- Write the consumer side of a contract as unit tests of the API client of the consumer. ^consumer-tests-the-client
- Write each HTTP contract as interactions, each with an expected request and the response parts that the consumer uses. ^contract-as-interactions
- Do not use a contract test to test the functions of the provider. ^contract-not-functional
- Check with contract tests that each test double gives the results of the real service, unless it holds a snapshot. ^double-matches-the-service
- If the consumer depends on the content of a response field, match the content exactly. ^exact-match-for-used-content
- In a write interaction, require the updated resource in the response, unless the provider does not return it. ^expect-written-values-back
- Run the contract tests of an external service against its test instance, unless it has no test instance. ^external-contract-test-instance
- Run the contract tests of an external service once a day. ^external-contract-test-pace
- If a contract test of an external service fails, open a task to bring the test doubles back in line. ^fix-doubles-on-contract-failure
- Match each response field that the consumer uses by its type, unless the consumer depends on its content. ^loose-response-matching
- Do not use contract tests to test the user interface of a consumer. ^no-contract-tests-through-ui
- Do not treat a shared OpenAPI description as a contract test, unless a tool checks each side against it. ^openapi-is-not-a-contract-test
- If an external service has no test instance, tell its owners about each contract test against its production instance. ^production-contract-tests-with-owners
- Build the contract of a provider from each consumer expectation inside its business function, unless its consumers are unknown. ^provider-contract-from-consumers
- Describe each precondition of an interaction as a provider state, not as an earlier interaction. ^provider-states
- Record the version and the environment of each deployment of a consumer or a provider. ^record-each-deployment
- Reject a consumer expectation that falls outside the business function of the provider. ^reject-out-of-mandate-expectations
- Include a scenario only if its absence hides a consumer bug or a misunderstanding of the provider response. ^scenario-must-catch-something
- If the provider returns no updated resource, use a shared fixture for the write request and the read response. ^shared-fixture-for-writes
- In a provider verification, limit the stubs to code that runs after the provider parses and validates the request. ^stub-below-request-parsing
- In the broader tests of the consumer, use the generated contract as the stubs of the provider. ^stub-from-the-contract
- Tell the owners of an external service when a change to its contract breaks a contract test. ^tell-the-service-owners
- In the build of the provider, verify each contract against a local instance of the provider, not a deployed instance. ^verify-against-local-provider
- Run the verification of the consumer contracts in the build of the provider. ^verify-in-provider-build

From [End-to-end testing](../../../references/end-to-end-testing.md):

- Make each timeout and delay of the production code configurable for the large tests. ^configurable-timeouts
- Run each large test hermetically, unless it is a prober or a backend has no runnable copy. ^hermetic-large-tests
- If a backend has no runnable copy, limit the shared parts of the system under test to that backend. ^hybrid-system-under-test
- Give each large test a failure message that names the test, the expected result, and the actual result. ^large-test-failure-message
- Add a large test for each risk that small tests miss, such as configuration, load, or an unfaithful double. ^large-test-for-each-gap
- Build each large test from a system under test, its seeded data, the actions, and the verification. ^large-test-structure
- Before a deployment to production, run the large tests that address the risks of the system. ^large-tests-before-deploy
- Give each large test a documented owner who reviews its changes and supports its failures. ^own-each-large-test
- Run each prober against production with deterministic read-only actions. ^probers-against-production
- Run each usability test on the complete system in a representative test environment. ^representative-system-test-environment
- If a large test is slow, split it into smaller tests that run in parallel. ^split-slow-large-tests
- If a broad test does not check the user interface, run it through the API below the user interface. ^subcutaneous-broad-tests
- Test the deployment configuration of each service with a large test. ^test-deployment-configuration
- Make each large test produce an artifact that locates the cause of a failure, such as a request trace. ^trace-large-test-requests

From [Integration testing](../../../references/integration-testing.md):

- If a suite holds only broad integration tests, add narrow integration tests. ^add-narrow-integration-tests
- Choose the integration strategy: top-down, bottom-up, sandwich, or big bang. ^choose-integration-strategy
- Write an integration test for each part of the code that serializes or deserializes data at a boundary. ^integration-test-each-boundary
- Add errors and latency to the calls between components in the integration tests. ^integration-test-failures
- In a narrow integration test, run each external dependency locally, unless it is a third-party service with no local version. ^local-integration-dependencies
- Do not run an integration test against production, unless a contract test has no test instance to target. ^no-tests-against-production
- In a narrow integration test, test only the code that calls another service, against a test double of it. ^one-integration-point-per-test
- In a narrow integration test, limit the network calls to localhost, unless a third-party service has no local version. ^one-machine-integration-tests
- Add a contract test for each test double of a service that a narrow integration test uses. ^pair-narrow-test-with-contract
- In a database integration test, check the written data by reading it back from the database. ^read-back-written-data
- Run the system integration tests in an environment similar to the operational environment. ^system-integration-environment
- If a third-party service has no local version, run the integration tests against its dedicated test instance. ^third-party-test-instance

From [Model-based testing](../../../references/model-based-testing.md):

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

From [Mutation testing](../../../references/mutation-testing.md):

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

From [Performance testing](../../../references/performance-testing.md):

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

From [Property-based testing](../../../references/property-based-testing.md):

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

From [Regression testing](../../../references/regression-testing.md):

- Write automated regression tests from the start of the project. ^automate-regression-early
- Do not delete a flaky test before you check the code under test for a bug. ^check-code-before-deleting-flaky-tests
- Check each new test for flakiness before you add it to the regression suite. ^check-new-tests-for-flakiness
- If the starting state needs a database with preloaded data, reset each shared state after each test. ^clean-shared-state
- After a defect fix, confirm that the steps that reproduced its failure no longer fail. ^confirm-the-fix
- If a high-priority test depends on a lower-priority test, run the lower-priority test first. ^dependencies-before-priority
- Raise a distinct timeout error when a test reaches its wait limit. ^distinct-timeout-error
- If different tests fail at random, limit each resource pool to `1` resource, with an error for an empty pool. ^expose-resource-leaks
- Before regression testing, run an impact analysis to find the parts of the system that the change affects. ^impact-analysis-first
- Build the starting state of each test from scratch, unless the state needs a database with preloaded data. ^isolated-test-state
- Limit the time of each test in quarantine to `1` week. ^limit-the-quarantine
- Set the scope of maintenance testing by the risk, the size of the system, and the size of the change. ^maintenance-test-scope
- Order the regression tests by the product risks that they cover. ^order-tests-by-priority
- Move each flaky test from the main suite into a quarantine suite. ^quarantine-flaky-tests
- After the confirmation tests pass, run the regression tests on the changed system. ^regression-after-confirmation
- Run the regression tests at each test level where a change or a fix happens. ^regression-at-each-level
- Run the regression suite after integration testing and before each deployment to production. ^regression-before-deployment
- Set each wait limit of a test from `1` shared setting, not as a literal value. ^shared-wait-limits
- Open a task to fix each test that goes into quarantine. ^task-for-each-quarantined-test
- When the system moves to a new operational environment, test the changed system in that environment. ^test-environment-migrations
- Add tests for each change that a defect fix needed, unless no time or budget remains. ^test-the-changes-of-a-fix
- Track the flaky results of each test over time. ^track-flakiness
- Wait for an asynchronous result with a callback, unless the service has no callback. ^wait-by-callback
- If an asynchronous service has no callback, wait for its result in a polling loop with a wait limit. ^wait-by-polling

From [Test doubles](../../../references/test-doubles.md):

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

From [Test-driven development](../../../references/test-driven-development.md):

- If a duplication has `3` or more copies, extract it into an abstraction in the refactor step. ^abstract-at-three-copies
- When you find a new case during a step, add it to the test list. ^add-new-cases-to-the-list
- Write production code only to make a failing test pass, unless you refactor the code after a test passes. ^code-only-for-a-failing-test
- Do not extract a duplication into an abstraction in the refactor step, unless it has `3` or more copies. ^duplication-is-a-hint
- Do not refactor while you make a failing test pass. ^green-before-refactor
- Keep each test of the cycle as an automated regression test. ^keep-tdd-tests
- Do not delete an assertion to make a test pass. ^keep-the-assertions
- Do not refactor beyond the current test list. ^limit-the-refactor
- List each variant of the new behavior and each existing behavior that the change puts at risk. ^list-variants-and-risks
- Change the code until the new test and each earlier test pass. ^make-all-tests-pass
- Mark each item of the test list as done when its test passes. ^mark-passing-items
- Do not copy a value that the code computes into the expected value of its test. ^no-copied-expected-values
- Do not put an implementation design decision in the test list. ^no-design-in-test-list
- Do not write tests for the whole test list before the first test passes. ^no-speculative-tests
- Do not write a test without an assertion. ^no-test-without-assertion
- Write exactly `1` item of the test list as a runnable test before you change the code. ^one-test-at-a-time
- After each test passes, refactor the new code and the old code to keep a clean structure. ^refactor-after-green
- Repeat the cycle from the second step until the test list is empty. ^repeat-until-the-list-is-empty
- If a new case invalidates the earlier work, start over with a different test order. ^restart-in-a-new-order
- Before you change the code, confirm that each new test fails. ^see-the-test-fail
- Write the first test of a behavior from its interface, before you decide its implementation. ^test-the-interface-first
- Before you change a behavior, write a list of the test scenarios that the change needs. ^write-the-test-list

From [Test pyramid](../../../references/test-pyramid.md):

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

From [Unit testing](../../../references/unit-testing.md):

- Change an existing unit test only when the required behavior of the system changes, unless a pure refactor breaks it. ^change-tests-only-for-behavior
- Write each failure message with the expected outcome, the actual outcome, and the inputs that produced them. ^clear-failure-messages
- Put each fact that explains the result of a test in the body of the test. ^complete-test-body
- Move each construction detail that does not affect the result into a helper. ^concise-test-body
- Do not move a step of a test into shared code that hides what the test does. ^damp-over-dry
- If a test targets a private method, move the method into a new class with a public interface. ^extract-private-method
- Name each unit test after the action that it takes and the outcome that it requires. ^name-after-the-behavior
- Limit each validation helper to `1` conceptual fact about its inputs. ^one-fact-per-validation-helper
- Make the result of each unit test independent of the order in which the tests run. ^order-independent-tests
- If a pure refactor breaks a unit test, make the test verify state through the public API. ^refactor-breaks-test
- Run the unit tests in the development environment. ^run-in-development-environment
- Use a setup method to build the object under test and its collaborators with default values. ^setup-for-defaults
- If a test depends on a value from the setup method, set that value in the test body. ^state-setup-values
- Write a separate test for each behavior of a unit, not `1` test for each method. ^test-each-behavior
- Treat shared test infrastructure as a separate product with its own tests. ^test-infrastructure-as-product
- Build each test value with a helper that takes only the fields that the test depends on. ^test-value-helpers
- Test each code path of a unit with conditional logic, including the happy path and each edge case. ^unit-test-each-code-path
- Test the response of a unit to each error that the interface of its dependency declares. ^unit-test-each-error
- In a unit test, replace each dependency that uses a network, a disk, or another process with a test double. ^unit-test-in-one-process

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Accessibility](../../../references/accessibility.md), and follow each directive from Accessibility.

## Inputs

- The requirements of the change and their examples
- The interface contracts and the UI contracts of the change

The output of each node in this list is an input of this step:

- [Software design](software-design.md)

## Procedure

The procedure of this step is missing.

## Output

The automated tests of the contracts of the change.

The output of this step is an input of each node in this list:

- [Software construction](software-construction.md)

## Exit gate

Check the tests against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Software construction](software-construction.md).

## References

- You test the output of an AI model or an AI feature. Read [AI evaluations](../../../references/ai-evaluations.md).
- You choose the test inputs for a behavior from its specification. Read [Black-box test techniques](../../../references/black-box-test-techniques.md).
- You measure the code coverage of a test suite. Read [Code coverage](../../../references/code-coverage.md).
- A test uses a test double for another service. Read [Contract testing](../../../references/contract-testing.md).
- A test runs the whole deployed system through its user interface or its public API. Read [End-to-end testing](../../../references/end-to-end-testing.md).
- A test connects the code to a database, a file system, a queue, or another service. Read [Integration testing](../../../references/integration-testing.md).
- You generate tests from a model of the system under test. Read [Model-based testing](../../../references/model-based-testing.md).
- You check whether the tests detect a change in the covered code. Read [Mutation testing](../../../references/mutation-testing.md).
- You test the response time, the throughput, or the capacity of a system under load. Read [Performance testing](../../../references/performance-testing.md).
- You write a test that generates its own input values. Read [Property-based testing](../../../references/property-based-testing.md).
- You run the existing tests again after a change to the code. Read [Regression testing](../../../references/regression-testing.md).
- A test replaces a dependency with a stub, a mock, or a fake. Read [Test doubles](../../../references/test-doubles.md).
- You write the code for a new behavior. Read [Test-driven development](../../../references/test-driven-development.md).
- You choose the level of a new test. Read [Test pyramid](../../../references/test-pyramid.md).
- You write a test for one function, one class, or one module. Read [Unit testing](../../../references/unit-testing.md).
