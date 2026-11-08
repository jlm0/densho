<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software quality

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

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

From [Secrets management](secrets-management.md):

- Give each secret only the permissions that its use needs. ^least-privilege-secret
- Do not write a secret, a password, or a session token to a log. ^no-secret-in-log
- Run a secret scanner in the pre-commit hook of each repository. ^scan-for-secrets-before-commit
- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

## Definition

The degree to which software meets its requirements and the needs of the people who use it. SWEBOK `v4` makes software quality a knowledge area. ISO/IEC 25010 sets the product quality model: the characteristics against which a team specifies and evaluates the quality of software. Here, quality covers the review of a change, the search for the cause of each defect, and the acceptance of the work.

## Comes from

The output of each node in this list is an input of this node.

- [Software configuration management](software-configuration-management.md)

## Goes to

The output of this node is an input of each node in this list.

- [Documentation](documentation.md)
- [Software operations](software-operations.md)

## References

- You verify a change against its acceptance scenarios. Read [Acceptance testing](acceptance-testing.md).
- You review a change or prepare a change for review. Read [Code review](code-review.md).
- You decide whether a change is complete. Read [Definition of done](definition-of-done.md).
- You test a user journey without a script. Read [Exploratory testing](exploratory-testing.md).
- You look for the cause of a bug or an incident. Read [Root cause analysis](root-cause-analysis.md).
- A change adds a capability for a future need. Read [YAGNI](yagni.md).
