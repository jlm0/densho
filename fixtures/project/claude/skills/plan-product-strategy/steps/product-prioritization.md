<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Prioritization

This file is step 4 of 5 of the skill `plan-product-strategy`.

## Directives

From [RICE scoring](../../../references/rice-scoring.md):

- Set confidence to `100%`, `80%`, or `50%`. ^confidence-scale
- State effort in person-months for the whole team, with `0.5` as the minimum. ^effort-in-person-months
- If no product metric measures the reach of an item, set its confidence below `100%`. ^estimated-reach-confidence
- Set impact to `3`, `2`, `1`, `0.5`, or `0.25`. ^impact-scale
- Take the reach of each item from product metrics, unless no product metric measures it. ^reach-from-metrics
- Measure reach as the number of people or events in one fixed period. ^reach-per-period
- Compute the RICE score as reach times impact times confidence, divided by effort. ^rice-formula

## Inputs

- The items to order: features, projects, or requirements
- The goal that the order serves, the timeframe, and the capacity of the team
- The data that RICE needs: product metrics for reach, the results of assumption tests for confidence, and estimates of effort

The output of each node in this list is an input of this step:

- [Product discovery](product-discovery.md)

## Procedure

1. State the goal that the order serves, the timeframe, and the capacity of the team.
2. Collect the reach, the impact, the confidence, and the effort of each item. Mark each value that rests on an estimate and not on data.
3. Compute the RICE score of each item, then sort the items by score.
4. Check the order against dependencies and commitments to customers. Move an item only with a stated reason.

## Output

A table of the items in their final order. Each row gives the reach, the impact, the confidence, the effort, the score, and the reason for each move against the score. The table names the timeframe.

The output of this step is an input of each node in this list:

- [Information architecture](../../../references/information-architecture.md)
- [Software requirements](../../../references/software-requirements.md)

## Exit gate

Check the table against each directive of this step and of the skill, and report each one that it misses. A reader can trace the position of each item to its score or to a stated reason.

## Next step

Read [Product positioning](product-positioning.md).

## References

- You compare a long list of items for one goal. Read [RICE scoring](../../../references/rice-scoring.md).
