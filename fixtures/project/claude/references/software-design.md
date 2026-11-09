<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software design

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

## Definition

The definition of the parts of a system and of the interfaces between them, at a level of detail that lets a team build and test each part on its own. SWEBOK `v4` makes software design a knowledge area next to software architecture.

## Notes

The output of this area is a set of contracts: the interface contract of each API and the UI contract of each component. Software testing and software construction take the contracts as their input.

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
