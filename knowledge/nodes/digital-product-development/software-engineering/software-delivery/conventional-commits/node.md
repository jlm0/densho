---
id: conventional-commits
kind: densho:Concept
title: Conventional Commits
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.conventionalcommits.org/en/v1.0.0/
broader:
  - software-delivery
related:
  - semantic-versioning
---

## Definition

A specification for commit messages that a person and a tool can both read. Each message starts with a type, an optional scope in parentheses, an optional `!`, a colon, a space, and a short description. A body and footers can follow, each after a blank line. A tool can derive the next semantic version from the types: `fix` gives a patch release, `feat` gives a minor release, and a breaking change gives a major release.

## Directives

- Use the Conventional Commits `1.0.0` format for each commit message. ^conventional-commit-format
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.conventionalcommits.org/en/v1.0.0/
- Give a commit the type `feat` when it adds a feature. ^feat-type
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.conventionalcommits.org/en/v1.0.0/
- Give a commit the type `fix` when it fixes a bug. ^fix-type
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.conventionalcommits.org/en/v1.0.0/
- Mark each breaking change with `!` before the colon or with a `BREAKING CHANGE:` footer. ^mark-breaking-change
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.conventionalcommits.org/en/v1.0.0/

## Notes

The specification also permits other types, such as `docs`, `refactor`, `test`, and `chore`. Only `feat`, `fix`, and a breaking change affect the version.
