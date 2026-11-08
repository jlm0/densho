<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Product measurement

This file is step 2 of 5 of the skill `plan-product-strategy`.

## Directives

From [HEART framework](../../../references/heart-framework.md):

- State for each HEART category whether the product uses it. ^choose-heart-categories
- Report each engagement metric as an average for each user, not as a total. ^engagement-per-user
- Write the goal of each HEART category before its signals and its metrics. ^goal-before-metric
- Choose signals that change only when the user experience changes. ^specific-signals

From [North star metric](../../../references/north-star-metric.md):

- Do not use a lagging measure such as revenue as the north star metric. ^leading-north-star
- Do not use active users or registered users as the north star metric. ^no-user-count-north-star
- Choose `3` to `5` input metrics that drive the north star metric and that the team influences. ^north-star-inputs
- Choose one north star metric for each product. ^one-north-star

From [Objectives and key results](../../../references/objectives-and-key-results.md):

- Mark each OKR as committed or aspirational. ^committed-or-aspirational
- Name the evidence of completion of each key result. ^key-result-evidence
- Do not link OKR scores to compensation. ^okrs-apart-from-pay
- Write each key result as a measured outcome, not as an activity. ^outcome-key-results
- Write a postmortem for each committed OKR that ends below `1.0`. ^postmortem-on-missed-commitment
- Give each key result a score from `0.0` to `1.0` at the end of the cycle. ^score-key-results
- If a score of `1.0` on `5` key results does not achieve an objective, split the objective. ^split-large-objectives
- Write enough key results that a score of `1.0` on each one achieves the objective. ^sufficient-key-results
- Write `3` to `5` key results for each objective. ^three-to-five-key-results

## Inputs

- The product or the feature, its users, and the decision that the metrics inform
- The data sources that exist: logs, analytics events, and surveys
- The strategy or the outcome that the product or the feature serves

The output of each node in this list is an input of this step:

- [Software operations](../../../references/software-operations.md)
- [Strategy formulation](strategy-formulation.md)

## Procedure

1. State the scope: the product or the feature, its users, and the decision that the metrics inform.
2. For each HEART category, decide if it applies. Write the goal of each category that applies.
3. For each goal, write the signals: the actions or attitudes of users that show success or failure. Name the data source of each signal.
4. For each signal, define a metric with its unit and its period.
5. If the scope is a whole product, choose the north star metric and its input metrics.
6. If the team uses OKRs, write an objective and its key results, with targets from the metrics.
7. Check that the team can measure each metric today. List the logging or the survey that each other metric needs.

## Output

A table with one row for each metric: the HEART category, the goal, the signal, the metric, its unit, its period, and its data source. For a whole product, the north star metric and its inputs. When the team uses OKRs, the objective and its key results.

The output of this step is an input of each node in this list:

- [Product discovery](product-discovery.md)

## Exit gate

Check the output against each directive of this step and of the skill, and report each one that it misses. Each metric traces to a goal, and each goal traces to the scope of procedure step 1.

## Next step

Read [Product discovery](product-discovery.md).

## References

- You measure the user experience of a product or a feature. Read [HEART framework](../../../references/heart-framework.md).
- You choose the one metric that a product team works to move. Read [North star metric](../../../references/north-star-metric.md).
- You write objectives and key results for a team or a company. Read [Objectives and key results](../../../references/objectives-and-key-results.md).
