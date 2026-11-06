<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# RICE scoring

## Directives

No directive is in force at this node.

## Definition

A prioritization score from Intercom, described by Sean McBride. Reach is the number of people or events that an item affects in a period. Impact is the effect on each person, on a fixed scale. Confidence is the share of support that the team has for its estimates. Effort is the total work of product, design, and engineering, in person-months. The score is reach times impact times confidence, divided by effort. It measures the total impact for each unit of work.

## Notes

The impact scale reads `3` for massive, `2` for high, `1` for medium, `0.5` for low, and `0.25` for minimal. The confidence scale reads `100%` for high, `80%` for medium, and `50%` for low. Intercom calls anything below `50%` a moonshot. Nielsen Norman Group allows `25%` for a wild guess. This node follows Intercom.

Intercom does not treat the score as a hard rule. A dependency, or a feature that a set of customers requires before they buy, can move an item with a lower score first.
