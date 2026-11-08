---
name: review-code-change
description: "Review a code change for its design, its behavior, its tests, and its security. Use when a code change is ready for review."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review a code change

If compaction cuts this skill, invoke the skill again.

## Directives

From [Software supply chain](../../references/software-supply-chain.md):

- Before you add a dependency, check its version for known vulnerabilities. ^check-new-dependency
- Remove each dependency that the code does not use. ^remove-unused-dependency
- Replace each dependency that no longer receives security fixes. ^replace-unmaintained-dependency
- Download each dependency from a trusted registry over a secure connection. ^trusted-registry

From [Secrets management](../../references/secrets-management.md):

- Give each secret only the permissions that its use needs. ^least-privilege-secret
- Do not write a secret, a password, or a session token to a log. ^no-secret-in-log
- Run a secret scanner in the pre-commit hook of each repository. ^scan-for-secrets-before-commit
- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Software testing](../../references/software-testing.md):

- Do not put a conditional or a loop in an example-based test, unless the loop polls for an asynchronous result. ^no-logic-in-tests
- Do not treat an automatic rerun of a flaky test as a fix of its cause. ^no-rerun-for-flaky-test
- Split each test into its setup, its action, and its verification. ^setup-action-verification
- Do not write a test for code without conditional logic, such as a plain getter or setter. ^skip-trivial-code
- Include a test that reproduces the bug in each bug fix. ^test-before-bug-fix
- Test each unit through its public interface, unless a property checks the invariant of its representation. ^test-public-interface

From [Software engineering](../../references/software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

From [Test pyramid](../../references/test-pyramid.md):

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

From [Code review](../../references/code-review.md):

- Approve a change once it improves the overall health of the code, unless it adds an unwanted feature. ^approve-on-improvement
- When a reviewer asks what code does, make the code clearer instead of replying only in the review. ^clarify-the-code
- Write each review comment about the code, not about its author. ^comment-on-the-code
- Write each code comment to explain why the code exists, not what it does. ^comments-explain-why
- State the problem and the reason for the approach in each change description. ^explain-each-change
- State the reason for each review comment. ^explain-each-comment
- Write the first line of each change description as a short imperative sentence. ^imperative-first-line
- Label each optional review comment with `Nit:`, `Optional:`, or `FYI:`. ^label-comment-severity
- Limit each change to one self-contained purpose. ^one-purpose-per-change
- Read each human-written line of a change before you approve it. ^read-every-line
- Do not approve a change that makes the health of the code worse. ^reject-worse-code
- Keep a refactor or a reformat in a separate change from a change in behavior. ^separate-refactors
- Split a change of `1000` or more changed lines, unless a tool generated it. ^split-large-change
- Check that each test in a change fails when the code under test breaks. ^tests-fail-on-breakage
- When a change affects how to build, test, or release the code, update the docs in the same change. ^update-docs-with-change

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

From [Review a code change](SKILL.md):

- If you review only part of a change, state which parts you reviewed. ^state-the-reviewed-parts

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.
- Read [Accessibility](../../references/accessibility.md), and follow these directives from it: `act-on-pointer-up`, `allow-text-spacing`, `bypass-repeated-blocks`, `consistent-identification`, `contrast-graphics`, `contrast-large-text`, `contrast-regular-text`, `contrast-ui-components`, `declare-input-purpose`, `declare-page-language`, `describe-input-error`, `descriptive-headings-and-labels`, `descriptive-page-title`, `expose-status-messages`, `focus-not-obscured`, `hide-decoration`, `keep-focus-visible`, `keyboard-operable`, `label-each-field`, `label-in-name`, `link-purpose`, `logical-focus-order`, `minimum-target-size`, `name-non-text-controls`, `name-role-value`, `no-change-on-focus`, `no-change-on-input`, `no-color-only`, `no-images-of-text`, `no-keyboard-trap`, `no-orientation-lock`, `no-sensory-only-instructions`, `reading-order-in-code`, `resize-text`, `structure-in-code`, `suggest-error-fix`, `text-alternative`, `two-ways-to-each-page`.

## Inputs

- The change: its diff and its description
- The code around the change, and the style guide of the project if it has one
- The result of the tests on the change, if the project ran them

## Procedure

1. Read each directive that this skill lists.
2. Read the description, and state the purpose of the change in one sentence.
3. Check that the change has one purpose and a size that a reviewer reads in one session.
4. Read each human-written line. Check the design, the behavior on edge cases and under concurrency, and each part that the change does not need.
5. Check that each change in behavior has a test, and that each test fails when its code breaks.
6. Check each input, each access check, and each secret that the change touches.
7. Check the names, the comments, the style, and the docs.
8. Write each finding with the directive that it breaks, its label, and the change that you recommend.
9. Approve the change, or ask for changes, from the directives on the health of the code.

## Output

A list of findings and a decision. Each finding names the file and the line, the directive that it breaks, its label, and the change that you recommend. The decision approves the change or asks for changes.

## Validation

Each finding names a directive from the first step of the procedure. A finding with no directive is an opinion, so label it `Optional:` or `FYI:`.

## References

- The change reads or changes data for a user. Read [Access control](../../references/access-control.md).
- You judge whether the change is ready to merge. Read [Code review](../../references/code-review.md).
- The change passes input to a query, a command, or an output. Read [Injection](../../references/injection.md).
- The change handles a password, a session, an error, or a connection. Read [Software security](../../references/software-security.md).
- You judge the tests of the change. Read [Software testing](../../references/software-testing.md).
- Read [Test pyramid](../../references/test-pyramid.md).
