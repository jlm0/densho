<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Build pipeline

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

## Definition

The automated build that runs on each change to a repository. Martin Fowler's continuous integration makes the build self-testing, and each push to the mainline triggers a build. A deployment pipeline breaks the build into stages. Early stages find most problems and give fast feedback. Later stages give slower and more thorough probing.

## Comes from

The output of each node in this list is an input of this node.

- [Conventional Commits](conventional-commits.md)

## Goes to

The output of this node is an input of each node in this list.

- [Semantic versioning](semantic-versioning.md)
