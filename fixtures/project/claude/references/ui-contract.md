<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# UI contract

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

## Definition

The agreed states and inputs of each interface component, written down before the team builds the component. A Storybook story captures the rendered state of a UI component, and a component gets a story for each interesting state that it supports. Component Story Format is an open standard for stories, based on ES6 modules. A UI contract is not the contract of contract testing, which covers the messages between a consumer and a provider.

## Comes from

The output of each node in this list is an input of this node.

- [Interface contract](interface-contract.md)
