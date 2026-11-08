<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Architecture style

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

From [Access control](access-control.md):

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
- Block access to each resource by default, unless the resource is public. ^deny-by-default

From [Software security](software-security.md):

- Do not put an API key or a session token in a URL. ^no-secret-in-url
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections

From [Secrets management](secrets-management.md):

- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Injection](injection.md):

- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server

## Definition

The overall form of a system, such as one deployable monolith or a set of services. Martin Fowler reports that almost every successful microservice system started as a monolith that grew too big and was split. Almost every system that he heard of that started as microservices ended up in serious trouble. Microservices carry a premium, the cost of managing a suite of services, that pays off only for complex systems. A monolith first, with modular boundaries, lets a team find the right boundaries before it splits out a service.

## Goes to

The output of this node is an input of each node in this list.

- [Integration style](integration-style.md)
