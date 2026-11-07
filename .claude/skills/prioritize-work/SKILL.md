---
name: prioritize-work
description: "Order a backlog or a roadmap by RICE score. Use when you set the order of the work of a team."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Prioritize the work of a team

If compaction cuts this skill, invoke the skill again.

## Directives

No directive is in force at this node.

## Inputs

- The items to order: features, projects, or requirements
- The goal that the order serves, the timeframe, and the capacity of the team
- The data that RICE needs: product metrics for reach, the results of assumption tests for confidence, and estimates of effort

## Procedure

1. Read each directive that this skill lists.
2. State the goal that the order serves, the timeframe, and the capacity of the team.
3. Collect the reach, the impact, the confidence, and the effort of each item. Mark each value that rests on an estimate and not on data.
4. Compute the RICE score of each item, then sort the items by score.
5. Check the order against dependencies and commitments to customers. Move an item only with a stated reason.

## Output

A table of the items in their final order. Each row gives the reach, the impact, the confidence, the effort, the score, and the reason for each move against the score. The table names the timeframe.

## Validation

Check the table against each directive from the first step of the procedure, and report each one it misses. A reader can trace the position of each item to its score or to a stated reason.

## References

- You state the goal that the order of the work serves. Read [Prioritization](../../references/product-prioritization.md).
- You score items by reach, impact, confidence, and effort. Read [RICE scoring](../../references/rice-scoring.md).
