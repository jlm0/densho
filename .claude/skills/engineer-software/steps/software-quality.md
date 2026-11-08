<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software quality

This file is step 7 of 8 of the skill `engineer-software`. If compaction cuts this file, read it again.

## Directives

No directive is in force at this step.

## Inputs

- The change, with its requirements and its tests

The output of each node in this list is an input of this step:

- [Software configuration management](software-configuration-management.md)

## Procedure

1. Run the skill `review-code-change` on the change.

The rest of the procedure of this step is missing.

## Output

The review of the change, the cause of each defect, and the decision to accept the work or not.

The output of this step is an input of each node in this list:

- [Documentation](../../../references/documentation.md)
- [Software operations](software-operations.md)

## Exit gate

Check the review and the acceptance against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Software operations](software-operations.md).

## References

- You verify a change against its acceptance scenarios. Read [Acceptance testing](../../../references/acceptance-testing.md).
- You review a change or prepare a change for review. Read [Code review](../../../references/code-review.md).
- You decide whether a change is complete. Read [Definition of done](../../../references/definition-of-done.md).
- You test a user journey without a script. Read [Exploratory testing](../../../references/exploratory-testing.md).
- You look for the cause of a bug or an incident. Read [Root cause analysis](../../../references/root-cause-analysis.md).
- A change adds a capability for a future need. Read [YAGNI](../../../references/yagni.md).
