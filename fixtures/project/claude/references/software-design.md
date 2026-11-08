<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software design

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

## Definition

The definition of the parts of a system and of the interfaces between them, at a level of detail that lets a team build and test each part on its own. SWEBOK `v4` makes software design a knowledge area next to software architecture. Here, design writes the contracts that the tests and the code follow: the interface contract of each API and the UI contract of each component.

## Comes from

The output of each node in this list is an input of this node.

- [Design systems](design-systems.md)
- [Software architecture](software-architecture.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software testing](software-testing.md)

## References

- You define or change the API or the events of a service. Read [Interface contract](interface-contract.md).
- You define the states and the inputs of an interface component. Read [UI contract](ui-contract.md).
