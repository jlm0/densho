<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software architecture

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

The structure of a system: its parts, the responsibilities of each part, and the relationships between them. It also covers the decisions that set that structure and the reasons for them.

## Comes from

The output of each node in this list is an input of this node.

- [Software requirements](software-requirements.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software design](software-design.md)

## References

- You make or change a decision about the structure of a system. Read [Architecture decision record](architecture-decision-record.md).
- You choose between one deployable unit and a set of services. Read [Architecture style](architecture-style.md).
- You draw or update a diagram of the structure of a system. Read [C4 model](c4-model.md).
- You connect two applications or two services. Read [Integration style](integration-style.md).
