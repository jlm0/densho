---
name: engineer-software
description: "Build software, from its requirements to its operation. Use when you write, test, or release software."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Engineer software

If compaction cuts this skill, invoke the skill again.

## Directives

From [Software engineering](../../references/software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

From [Software security](../../references/software-security.md):

- Do not show a stack trace, a query, or a secret in an error message to a user. ^generic-error-message
- Add a global handler that catches each exception that other code does not catch. ^global-exception-handler
- Store each password as an `argon2id`, `scrypt`, `bcrypt`, or `PBKDF2` hash. ^hash-each-password
- Replace the session token of a user at each login. ^new-session-at-login
- Do not include a default account or a default password in a release. ^no-default-credentials
- Do not put an API key or a session token in a URL. ^no-secret-in-url
- If a step of a transaction fails, revert the whole transaction. ^revert-failed-transaction
- Generate each token and each secret with a cryptographically secure random number generator. ^secure-random-for-secrets
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections

From [Access control](../../references/access-control.md):

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
- Check the permission of the user for each record that a request reads or changes. ^check-each-record
- Block access to each resource by default, unless the resource is public. ^deny-by-default
- Log each failed access control check. ^log-access-failures
- Add a test for each access control rule. ^test-access-control

From [Injection](../../references/injection.md):

- Encode each untrusted value for the context where the output uses it. ^encode-output-for-context
- Do not use `eval` or another feature that runs dynamic code. ^no-dynamic-code
- Pass each argument of an operating system command as a separate parameter, not through a shell string. ^no-shell-string
- Use parameterized queries or an ORM for each database query. ^parameterize-queries
- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server

From [Secrets management](../../references/secrets-management.md):

- Give each secret only the permissions that its use needs. ^least-privilege-secret
- Do not write a secret, a password, or a session token to a log. ^no-secret-in-log
- Run a secret scanner in the pre-commit hook of each repository. ^scan-for-secrets-before-commit
- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Software supply chain](../../references/software-supply-chain.md):

- Before you add a dependency, check its version for known vulnerabilities. ^check-new-dependency
- Remove each dependency that the code does not use. ^remove-unused-dependency
- Replace each dependency that no longer receives security fixes. ^replace-unmaintained-dependency
- Download each dependency from a trusted registry over a secure connection. ^trusted-registry

From [Software testing](../../references/software-testing.md):

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
- Run the automated component tests on each commit in continuous integration. ^tests-in-continuous-integration
- Link each test case to each element of the test basis that it covers. ^trace-tests-to-the-basis

From [Software operations](../../references/software-operations.md):

- Send a page only for a problem that needs human judgment at once. ^actionable-pages
- Make each alert detect a symptom that users see, not its cause, unless the cause is definite and imminent. ^alert-on-symptoms
- Monitor the latency, the traffic, the errors, and the saturation of each user-facing service. ^golden-signals
- Measure the latency of failed requests apart from the latency of successful requests. ^separate-error-latency

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.

## Steps

Run the steps in this order:

1. [Software requirements](steps/software-requirements.md)
2. [Software architecture](steps/software-architecture.md)
3. [Software design](steps/software-design.md)
4. [Software testing](steps/software-testing.md)
5. [Software construction](steps/software-construction.md)
6. [Software configuration management](steps/software-configuration-management.md)
7. [Software quality](steps/software-quality.md)
8. [Software operations](steps/software-operations.md)

For each step:

1. Read its step file and each required read in it.
2. If the output of the step exists already, go to the next step.
3. Run the procedure of the step.
4. Go to the next step only after the exit gate of the step passes.
