<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# C4 model

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

From [C4 model](c4-model.md):

- Give each architecture diagram a key for its shapes, colors, borders, and lines. ^diagram-key
- Give each architecture diagram a title that states its type and its scope. ^diagram-title
- Label each element of an architecture diagram with its type and a short description. ^label-diagram-elements
- Label each line in an architecture diagram with the purpose of its relationship. ^label-diagram-lines
- Name the technology of each container and each component in an architecture diagram. ^name-diagram-technology

## Definition

A set of abstractions and diagrams for software architecture by Simon Brown. People use software systems. A software system holds containers, a container holds components, and code implements each component. A container is an application or a data store that must run for the system to work. It is not a Docker container. The four core diagrams follow the same levels: the system context, the containers, the components, and the code.

## Notes

The C4 model sets no notation. Each line shows a relationship in one direction. A label such as `Uses` says too little, so the label names what flows or what depends.

## Comes from

The output of each node in this list is an input of this node.

- [Integration style](integration-style.md)

## Goes to

The output of this node is an input of each node in this list.

- [Architecture decision record](architecture-decision-record.md)
