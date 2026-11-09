---
name: prioritize-work
description: "Order the items of a backlog or a roadmap by RICE score. Use when you set the order of the items in a backlog or a roadmap. Do not use it for the choice of a customer need (`map-opportunities`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Prioritize the work of a team

## Run the skill

1. Follow each directive of the skill.
2. If you need the definition or the notes of a page, read the page.

## Order the items

1. Collect the items to order: features, projects, or requirements.
2. State the goal that the order serves, the timeframe, and the capacity of the team.
3. Collect the reach, the impact, the confidence, and the effort of each item.
4. Mark each value that rests on an estimate and not on data.
5. Compute the RICE score of each item.
6. Sort the items by score.
7. Check the order against dependencies and commitments to customers.
8. Write the reason for each item that leaves its place in the score order.

Missing rule: No directive of prioritization requires the goal, the timeframe, and the capacity before the order.

Missing rule: No directive of prioritization chooses the method for items with deadlines.

Pages:

- You set the order of the items in a backlog or a roadmap. Read [Prioritization](../../references/product-prioritization.md).
- You score items by reach, impact, confidence, and effort. Read [RICE scoring](../../references/rice-scoring.md).

Directives:

- State the user problem of each feature in one sentence. ^state-user-problem
- Measure reach as the number of people or events in one fixed period. ^reach-per-period
- Take the reach of each item from product metrics, unless no product metric measures it. ^reach-from-metrics
- If no product metric measures the reach of an item, set its confidence below `100%`. ^estimated-reach-confidence
- Set impact to `3`, `2`, `1`, `0.5`, or `0.25`. ^impact-scale
- Set confidence to `100%`, `80%`, or `50%`. ^confidence-scale
- State effort in person-months for the whole team, with `0.5` as the minimum. ^effort-in-person-months
- Compute the RICE score as reach times impact times confidence, divided by effort. ^rice-formula
- Order the items by RICE score, unless an item blocks another item or a customer requires it before a sale. ^order-by-rice-score
- If an item blocks another item or a customer requires it before a sale, put it first in the order. ^dependencies-first

Output: The items in their final order, each with its values, its score, and the reason for each move.

## Exit checklist

Check each line before you report the order as done.

- [ ] A reader traces the place of each item to its score or to a stated reason.
- [ ] Each value that rests on an estimate has a mark.
- [ ] The table names the goal and the timeframe.
- [ ] The report names each directive that the order misses, and each missing rule that the order reached.

## Output

- A table of the items in their final order. Each row gives the user problem, the reach, the impact, the confidence, the effort, the score, and the reason for each move.
- A list of each directive that the order misses, with the reason

To design or build the first items, run `design-interface` for a screen or `engineer-software` for code.
