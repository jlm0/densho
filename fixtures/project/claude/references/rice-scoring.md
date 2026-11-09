<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# RICE scoring

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Product strategy](product-strategy.md):

- State the user problem of each feature in one sentence. ^state-user-problem
- Write the success measure of each feature before you build the feature. ^write-success-measure

From [RICE scoring](rice-scoring.md):

- Set confidence to `100%`, `80%`, or `50%`. ^confidence-scale
- If an item blocks another item or a customer requires it before a sale, put it first in the order. ^dependencies-first
- State effort in person-months for the whole team, with `0.5` as the minimum. ^effort-in-person-months
- If no product metric measures the reach of an item, set its confidence below `100%`. ^estimated-reach-confidence
- Set impact to `3`, `2`, `1`, `0.5`, or `0.25`. ^impact-scale
- Order the items by RICE score, unless an item blocks another item or a customer requires it before a sale. ^order-by-rice-score
- Take the reach of each item from product metrics, unless no product metric measures it. ^reach-from-metrics
- Measure reach as the number of people or events in one fixed period. ^reach-per-period
- Compute the RICE score as reach times impact times confidence, divided by effort. ^rice-formula

## Definition

A prioritization score from Intercom, described by Sean McBride. Reach is the number of people or events that an item affects in a period. Impact is the effect on each person, on a fixed scale. Confidence is the share of support that the team has for its estimates. Effort is the total work of product, design, and engineering, in person-months. The score is reach times impact times confidence, divided by effort. It measures the total impact for each unit of work.

## Notes

The impact scale reads `3` for massive, `2` for high, `1` for medium, `0.5` for low, and `0.25` for minimal. The confidence scale reads `100%` for high, `80%` for medium, and `50%` for low. Intercom calls anything below `50%` a moonshot. Nielsen Norman Group allows `25%` for a wild guess. This node follows Intercom.

Intercom does not treat the score as a hard rule. A dependency, or a feature that a set of customers requires before they buy, can move an item with a lower score first.
