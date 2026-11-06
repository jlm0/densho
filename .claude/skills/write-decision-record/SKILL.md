---
name: write-decision-record
description: "Write an architecture decision record for one decision. Use when you make or change a decision about the structure of a system."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Write a decision record

If compaction cuts this skill, invoke the skill again.

## Directives

No directive is in force at this node.

## Inputs

- The decision, and each option that the person considered
- The forces on the decision: the requirements, the constraints, and the quality goals
- The decision records that the repository already holds

## Procedure

1. Read each directive that this skill lists.
2. Find the folder and the format of the decision records in the repository. If the repository has none, ask the person where to keep them.
3. Give the record the next unused number and a title that names the decision.
4. Write the context: the forces that bear on the decision, stated as facts.
5. Write the decision in full sentences in the active voice.
6. List each consequence of the decision: positive, negative, and neutral.
7. If the decision replaces an earlier decision, mark the earlier record as superseded and link it to the new record.

## Output

One decision record file. Each record that the decision replaces carries the superseded status and a link to the new record.

## Validation

Check the record against each directive from the first step of the procedure, and report each one it misses. A reader who did not take part in the decision can state the decision and its main reason from the record alone.

## References

- You choose the sections, the number, or the status of the record. Read [Architecture decision record](../../references/architecture-decision-record.md).
