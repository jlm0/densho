<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Secrets management

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

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

The control of each secret over its whole life: its creation, its storage, its access, its rotation, and its revocation. A secret is a value that gives access to a system, such as a password, an API key, a private key, or a database credential.

## Notes

After an exposure, the cheat sheet gives this order: revoke the secret, then rotate it, then delete it from the exposed system.
