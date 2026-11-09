<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Integration style

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Access control](access-control.md):

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
- Block access to each resource by default, unless the resource is public. ^deny-by-default

From [Software security](software-security.md):

- Do not put an API key or a session token in a URL. ^no-secret-in-url
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections

From [Injection](injection.md):

- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server

## Definition

The way that separate applications work together. Gregor Hohpe and Bobby Woolf name four integration styles: file transfer, a shared database, remote procedure invocation, and messaging. The choice depends on each point of integration, and one system can use several styles. Martin Fowler separates event notification, in which a system tells other systems of a change in its domain and does not care much about the response, from a command, in which the sender expects the receiver to act.

## Comes from

The output of each node in this list is an input of this node.

- [Architecture style](architecture-style.md)

## Goes to

The output of this node is an input of each node in this list.

- [C4 model](c4-model.md)
