<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Semantic versioning

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

From [Semantic versioning](semantic-versioning.md):

- Declare the public API of each package that uses semantic versioning. ^declare-public-api
- Do not change the contents of a released version. ^keep-released-version
- Increment the major version when a release breaks compatibility with the public API. ^major-for-breaking-change
- Increment the minor version when a release adds a compatible feature or a deprecation. ^minor-for-compatible-feature
- Increment the patch version when a release holds only compatible bug fixes. ^patch-for-bug-fix

## Definition

A version number of the form `MAJOR.MINOR.PATCH` that states how a release changes the public API. The major version counts incompatible changes, the minor version counts compatible additions, and the patch version counts compatible bug fixes. Major version `0` is for initial development, and its public API is not stable. The specification is Semantic Versioning `2.0.0`.

## Notes

An increment of the major version resets the minor and the patch versions to `0`. An increment of the minor version resets the patch version to `0`. If a minor release breaks compatibility by mistake, release a new minor version that restores compatibility, and leave the faulty release as it is.

## Comes from

The output of each node in this list is an input of this node.

- [Build pipeline](build-pipeline.md)
