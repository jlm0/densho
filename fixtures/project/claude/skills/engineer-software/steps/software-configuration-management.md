<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software configuration management

This file is step 6 of 8 of the skill `engineer-software`. If compaction cuts this file, read it again.

## Directives

From [Conventional Commits](../../../references/conventional-commits.md):

- Use the Conventional Commits `1.0.0` format for each commit message. ^conventional-commit-format
- Give a commit the type `feat` when it adds a feature. ^feat-type
- Give a commit the type `fix` when it fixes a bug. ^fix-type
- Mark each breaking change with `!` before the colon or with a `BREAKING CHANGE:` footer. ^mark-breaking-change

From [Semantic versioning](../../../references/semantic-versioning.md):

- Declare the public API of each package that uses semantic versioning. ^declare-public-api
- Do not change the contents of a released version. ^keep-released-version
- Increment the major version when a release breaks compatibility with the public API. ^major-for-breaking-change
- Increment the minor version when a release adds a compatible feature or a deprecation. ^minor-for-compatible-feature
- Increment the patch version when a release holds only compatible bug fixes. ^patch-for-bug-fix

From [Trunk-based development](../../../references/trunk-based-development.md):

- Fix each bug on the trunk before you copy the fix to a release branch. ^fix-on-trunk-first
- Keep `3` or fewer active branches in a repository. ^limit-active-branches
- Merge each branch into the trunk within `1` day of its creation. ^merge-to-trunk-daily
- Do not merge a release branch into the trunk. ^no-release-branch-merge
- Do not push a change to a trunk whose build fails, unless the change fixes the build. ^repair-broken-trunk
- Run the tests before you push a change to the trunk. ^test-before-push

## Inputs

- The code and the tests of the change

The output of each node in this list is an input of this step:

- [Software construction](software-construction.md)

## Procedure

The procedure of this step is missing.

## Output

The commits, the branch, the build, and the version number of the change.

The output of this step is an input of each node in this list:

- [Software quality](software-quality.md)

## Exit gate

Check the commits, the branch, the build, and the version number against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Software quality](software-quality.md).

## References

- You set up or change the automated build of a repository. Read [Build pipeline](../../../references/build-pipeline.md).
- You write a commit message. Read [Conventional Commits](../../../references/conventional-commits.md).
- You choose the version number of a release. Read [Semantic versioning](../../../references/semantic-versioning.md).
- You create, merge, or release a branch. Read [Trunk-based development](../../../references/trunk-based-development.md).
