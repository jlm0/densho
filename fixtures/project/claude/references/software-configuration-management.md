<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software configuration management

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

## Definition

The control of the versions of software and of each change to it, from the commit to the released version. SWEBOK `v4` makes software configuration management a knowledge area. Here, it covers the branch model, the commit messages, the build pipeline, and the version numbers.

## Comes from

The output of each node in this list is an input of this node.

- [Software construction](software-construction.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software quality](software-quality.md)

## References

- You set up or change the automated build of a repository. Read [Build pipeline](build-pipeline.md).
- You write a commit message. Read [Conventional Commits](conventional-commits.md).
- You choose the version number of a release. Read [Semantic versioning](semantic-versioning.md).
- You create, merge, or release a branch. Read [Trunk-based development](trunk-based-development.md).
