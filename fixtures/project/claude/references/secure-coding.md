<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Secure coding

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

## Definition

The writing of code that resists attack. Here, it holds four concerns: access control, injection, secrets management, and the software supply chain. The OWASP Application Security Verification Standard gives the security requirements for the design, the development, and the testing of web applications and web services.

## Comes from

The output of each node in this list is an input of this node.

- [Threat modeling](threat-modeling.md)

## Goes to

The output of this node is an input of each node in this list.

- [Security review](security-review.md)

## References

- You set which users read or change a resource. Read [Access control](access-control.md).
- Input from outside the code reaches a query, a command, or an output. Read [Injection](injection.md).
- You store, pass, or log a secret. Read [Secrets management](secrets-management.md).
- You add, update, or remove a dependency. Read [Software supply chain](software-supply-chain.md).
