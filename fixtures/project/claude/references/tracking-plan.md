<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Tracking plan

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

## Definition

A document that defines each product event and each property that a product collects, why it collects each one, and which source emits it. Amplitude advises a team to build it before it instruments the code, so that analysts, product managers, and engineers work from one schema. Mixpanel builds it from the key metrics, maps them to user flows, and turns the flows into events and properties.

## Comes from

The output of each node in this list is an input of this node.

- [Observability](observability.md)

## Goes to

The output of this node is an input of each node in this list.

- [Product measurement](product-measurement.md)
