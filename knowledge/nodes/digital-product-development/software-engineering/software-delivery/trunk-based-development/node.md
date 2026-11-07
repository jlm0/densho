---
id: trunk-based-development
kind: densho:Concept
title: Trunk-based development
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://trunkbaseddevelopment.com/
  - https://dora.dev/capabilities/trunk-based-development/
broader:
  - software-delivery
depends_on:
  - software-testing
---

## Definition

A branching model in which each developer merges small batches of work into one shared branch, the trunk, at least once a day. Branches live for hours, not for days or weeks. The trunk stays in a state that a team can release at any time. Continuous integration depends on this model.

## Directives

- Merge each branch into the trunk within `1` day of its creation. ^merge-to-trunk-daily
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://dora.dev/capabilities/trunk-based-development/
- Keep `3` or fewer active branches in a repository. ^limit-active-branches
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://dora.dev/capabilities/trunk-based-development/
- Run the tests before you push a change to the trunk. ^test-before-push
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://dora.dev/capabilities/trunk-based-development/
  - sources: https://trunkbaseddevelopment.com/
- Do not push a change to a trunk whose build fails, unless the change fixes the build. ^repair-broken-trunk
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://dora.dev/capabilities/trunk-based-development/
- Fix each bug on the trunk before you copy the fix to a release branch. ^fix-on-trunk-first
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://trunkbaseddevelopment.com/branch-for-release/
- Do not merge a release branch into the trunk. ^no-release-branch-merge
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://trunkbaseddevelopment.com/branch-for-release/

## Notes

The DORA research linked these practices with higher delivery performance: `3` or fewer active branches, a merge into the trunk at least once a day, and no code freeze or integration phase.
