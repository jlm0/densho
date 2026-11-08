---
name: prioritize-work
description: "Order a backlog or a roadmap by RICE score. Use when you set the order of the work of a team."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Prioritize the work of a team

If compaction cuts this skill, invoke the skill again.

## Directives

From [Digital product development](../../references/digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Product strategy](../../references/product-strategy.md):

- State the user problem of each feature in one sentence. ^state-user-problem
- Write the success measure of each feature before you build the feature. ^write-success-measure

From [RICE scoring](../../references/rice-scoring.md):

- Set confidence to `100%`, `80%`, or `50%`. ^confidence-scale
- State effort in person-months for the whole team, with `0.5` as the minimum. ^effort-in-person-months
- If no product metric measures the reach of an item, set its confidence below `100%`. ^estimated-reach-confidence
- Set impact to `3`, `2`, `1`, `0.5`, or `0.25`. ^impact-scale
- Take the reach of each item from product metrics, unless no product metric measures it. ^reach-from-metrics
- Measure reach as the number of people or events in one fixed period. ^reach-per-period
- Compute the RICE score as reach times impact times confidence, divided by effort. ^rice-formula

From [Prioritization](../../references/product-prioritization.md):

- Give each product team business objectives with key results, not a list of features to build. ^objectives-not-feature-lists

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
