<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software security

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

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

## Definition

Protecting a system and its data from people who act outside their permissions. The OWASP Top 10 states a broad consensus on the most critical security risks to web applications. The OWASP Application Security Verification Standard (ASVS) gives a basis for testing the technical security controls of a web application, and lists the requirements for secure development.

## Notes

The directives cite OWASP Top 10:2025 and ASVS 5.0.0. ASVS gives each requirement a level from 1 to 3. Level 1 holds the minimum requirements to secure an application.

| Level | Directives on this node                                                                                 |
| ----- | ------------------------------------------------------------------------------------------------------- |
| 1     | `new-session-at-login`, `no-default-credentials`, `tls-for-external-connections`, `no-secret-in-url`    |
| 2     | `hash-each-password`, `secure-random-for-secrets`, `generic-error-message`, `revert-failed-transaction` |
| 3     | `global-exception-handler`, which the Top 10 also names                                                 |

## References

- You write code that handles input, access, a secret, or a dependency. Read [Secure coding](secure-coding.md).
- You audit the security of a system that already runs. Read [Security assessment](security-assessment.md).
- You review a change for security flaws. Read [Security review](security-review.md).
- You design a new system or a new feature. Read [Threat modeling](threat-modeling.md).
- A vulnerability is reported in a system or in a dependency. Read [Vulnerability management](vulnerability-management.md).
