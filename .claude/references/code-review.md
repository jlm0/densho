<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Code review

## Directives

No directive is in force at this node.

## Definition

The reading of a change by a person other than its author before the change merges. A change is one commit or one pull request that a reviewer reads as a unit. The review keeps the overall health of the code improving over time. It checks the design, the behavior, the complexity, the tests, the names, the comments, the style, and the docs of the change.

## Notes

The source is the code review guide of Google engineering practices, which calls a change a CL. About `100` changed lines is a reasonable size for one change. A small cleanup, such as the rename of a local variable, can stay in a change in behavior. With Conventional Commits, the type comes first, and the imperative summary follows the colon.
