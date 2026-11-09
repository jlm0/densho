<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Threat modeling

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

The analysis of a design to find what can go wrong in a system and to decide what to do about it. The Threat Modeling Manifesto asks four questions: what are we working on, what can go wrong, what are we going to do about it, and did we do a good enough job. Microsoft's STRIDE names six classes of threat: spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege.

## Goes to

The output of this node is an input of each node in this list.

- [Secure coding](secure-coding.md)
