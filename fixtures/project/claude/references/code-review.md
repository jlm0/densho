<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Code review

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Give each secret only the permissions that its use needs. ^least-privilege-secret
- Do not write a secret, a password, or a session token to a log. ^no-secret-in-log
- Run a secret scanner in the pre-commit hook of each repository. ^scan-for-secrets-before-commit
- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Access control](access-control.md):

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
- Check the permission of the user for each record that a request reads or changes. ^check-each-record
- Block access to each resource by default, unless the resource is public. ^deny-by-default
- Log each failed access control check. ^log-access-failures
- Add a test for each access control rule. ^test-access-control

From [Software supply chain](software-supply-chain.md):

- Before you add a dependency, check its version for known vulnerabilities. ^check-new-dependency
- Remove each dependency that the code does not use. ^remove-unused-dependency
- Replace each dependency that no longer receives security fixes. ^replace-unmaintained-dependency
- Download each dependency from a trusted registry over a secure connection. ^trusted-registry

From [Injection](injection.md):

- Encode each untrusted value for the context where the output uses it. ^encode-output-for-context
- Do not use `eval` or another feature that runs dynamic code. ^no-dynamic-code
- Pass each argument of an operating system command as a separate parameter, not through a shell string. ^no-shell-string
- Use parameterized queries or an ORM for each database query. ^parameterize-queries
- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server

From [Software security](software-security.md):

- Do not show a stack trace, a query, or a secret in an error message to a user. ^generic-error-message
- Add a global handler that catches each exception that other code does not catch. ^global-exception-handler
- Store each password as an `argon2id`, `scrypt`, `bcrypt`, or `PBKDF2` hash. ^hash-each-password
- Replace the session token of a user at each login. ^new-session-at-login
- Do not include a default account or a default password in a release. ^no-default-credentials
- Do not put an API key or a session token in a URL. ^no-secret-in-url
- If a step of a transaction fails, revert the whole transaction. ^revert-failed-transaction
- Generate each token and each secret with a cryptographically secure random number generator. ^secure-random-for-secrets
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections

From [Code review](code-review.md):

- Approve a change once it improves the overall health of the code, unless it adds an unwanted feature. ^approve-on-improvement
- When a reviewer asks what code does, make the code clearer instead of replying only in the review. ^clarify-the-code
- Write each review comment about the code, not about its author. ^comment-on-the-code
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

From [Software construction](software-construction.md):

- Write each code comment to explain why the code exists, not what it does. ^comments-explain-why

## Definition

The reading of a change by a person other than its author before the change merges. A change is one commit or one pull request that a reviewer reads as a unit. The review keeps the overall health of the code improving over time. It checks the design, the behavior, the complexity, the tests, the names, the comments, the style, and the docs of the change.

## Notes

The source is the code review guide of Google engineering practices, which calls a change a CL. About `100` changed lines is a reasonable size for one change. A small cleanup, such as the rename of a local variable, can stay in a change in behavior. With Conventional Commits, the type comes first, and the imperative summary follows the colon.
