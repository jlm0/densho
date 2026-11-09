<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Conventional Commits

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Conventional Commits](conventional-commits.md):

- Use the Conventional Commits `1.0.0` format for each commit message. ^conventional-commit-format
- Give a commit the type `feat` when it adds a feature. ^feat-type
- Give a commit the type `fix` when it fixes a bug. ^fix-type
- Mark each breaking change with `!` before the colon or with a `BREAKING CHANGE:` footer. ^mark-breaking-change

## Definition

A specification for commit messages that a person and a tool can both read. Each message starts with a type, an optional scope in parentheses, an optional `!`, a colon, a space, and a short description. A body and footers can follow, each after a blank line. A tool can derive the next semantic version from the types: `fix` gives a patch release, `feat` gives a minor release, and a breaking change gives a major release.

## Notes

The specification also permits other types, such as `docs`, `refactor`, `test`, and `chore`. Only `feat`, `fix`, and a breaking change affect the version.

## Comes from

The output of each node in this list is an input of this node.

- [Trunk-based development](trunk-based-development.md)

## Goes to

The output of this node is an input of each node in this list.

- [Build pipeline](build-pipeline.md)
