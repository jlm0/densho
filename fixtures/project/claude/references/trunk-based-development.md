<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Trunk-based development

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Trunk-based development](trunk-based-development.md):

- Fix each bug on the trunk before you copy the fix to a release branch. ^fix-on-trunk-first
- Keep `3` or fewer active branches in a repository. ^limit-active-branches
- Merge each branch into the trunk within `1` day of its creation. ^merge-to-trunk-daily
- Do not merge a release branch into the trunk. ^no-release-branch-merge
- Do not push a change to a trunk whose build fails, unless the change fixes the build. ^repair-broken-trunk
- Run the tests before you push a change to the trunk. ^test-before-push

## Definition

A branching model in which each developer merges small batches of work into one shared branch, the trunk, at least once a day. Branches live for hours, not for days or weeks. The trunk stays in a state that a team can release at any time. Continuous integration depends on this model.

## Notes

The DORA research linked these practices with higher delivery performance: `3` or fewer active branches, a merge into the trunk at least once a day, and no code freeze or integration phase.

## Goes to

The output of this node is an input of each node in this list.

- [Conventional Commits](conventional-commits.md)
