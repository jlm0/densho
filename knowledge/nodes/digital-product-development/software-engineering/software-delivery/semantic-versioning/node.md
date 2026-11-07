---
id: semantic-versioning
kind: densho:Concept
title: Semantic versioning
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://semver.org/
broader:
  - software-delivery
---

## Definition

A version number of the form `MAJOR.MINOR.PATCH` that states how a release changes the public API. The major version counts incompatible changes, the minor version counts compatible additions, and the patch version counts compatible bug fixes. Major version `0` is for initial development, and its public API is not stable. The specification is Semantic Versioning `2.0.0`.

## Directives

- Declare the public API of each package that uses semantic versioning. ^declare-public-api
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://semver.org/
- Increment the major version when a release breaks compatibility with the public API. ^major-for-breaking-change
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://semver.org/
- Increment the minor version when a release adds a compatible feature or a deprecation. ^minor-for-compatible-feature
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://semver.org/
- Increment the patch version when a release holds only compatible bug fixes. ^patch-for-bug-fix
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://semver.org/
- Do not change the contents of a released version. ^keep-released-version
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://semver.org/

## Notes

An increment of the major version resets the minor and the patch versions to `0`. An increment of the minor version resets the patch version to `0`. If a minor release breaks compatibility by mistake, release a new minor version that restores compatibility, and leave the faulty release as it is.
