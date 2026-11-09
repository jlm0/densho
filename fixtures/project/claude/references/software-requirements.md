<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software requirements

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

## Definition

The discovery, the specification, and the validation of what a system must do, before the team builds it. SWEBOK `v4` makes software requirements its first knowledge area. ISO/IEC/IEEE 29148 is the standard for requirements engineering in the life cycle of systems and software.

## Notes

In specification by example, each requirement becomes a set of examples, and each example becomes a test.

## Comes from

The output of each node in this list is an input of this node.

- [Prioritization](product-prioritization.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software architecture](software-architecture.md)

## References

- You map each requirement of a change to its tests. Read [Requirements traceability](requirements-traceability.md).
- You write the acceptance scenarios of a change. Read [Specification by example](specification-by-example.md).
- A technical question blocks the specification of a change. Read [Spike](spike.md).
