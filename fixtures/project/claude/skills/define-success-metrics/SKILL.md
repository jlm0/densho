---
name: define-success-metrics
description: "Define the goals, the signals, and the metrics of a product or a feature. Use when you decide how to measure the success of a product or a feature."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Define success metrics

If compaction cuts this skill, invoke the skill again.

## Directives

From [Digital product development](../../references/digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Product strategy](../../references/product-strategy.md):

- State the user problem of each feature in one sentence. ^state-user-problem
- Write the success measure of each feature before you build the feature. ^write-success-measure

From [HEART framework](../../references/heart-framework.md):

- State for each HEART category whether the product uses it. ^choose-heart-categories
- Report each engagement metric as an average for each user, not as a total. ^engagement-per-user
- Write the goal of each HEART category before its signals and its metrics. ^goal-before-metric
- Choose signals that change only when the user experience changes. ^specific-signals

From [Objectives and key results](../../references/objectives-and-key-results.md):

- Mark each OKR as committed or aspirational. ^committed-or-aspirational
- Name the evidence of completion of each key result. ^key-result-evidence
- Do not link OKR scores to compensation. ^okrs-apart-from-pay
- Write each key result as a measured outcome, not as an activity. ^outcome-key-results
- Write a postmortem for each committed OKR that ends below `1.0`. ^postmortem-on-missed-commitment
- Give each key result a score from `0.0` to `1.0` at the end of the cycle. ^score-key-results
- If a score of `1.0` on `5` key results does not achieve an objective, split the objective. ^split-large-objectives
- Write enough key results that a score of `1.0` on each one achieves the objective. ^sufficient-key-results
- Write `3` to `5` key results for each objective. ^three-to-five-key-results

From [North star metric](../../references/north-star-metric.md):

- Do not use a lagging measure such as revenue as the north star metric. ^leading-north-star
- Do not use active users or registered users as the north star metric. ^no-user-count-north-star
- Choose `3` to `5` input metrics that drive the north star metric and that the team influences. ^north-star-inputs
- Choose one north star metric for each product. ^one-north-star

From [Product measurement](../../references/product-measurement.md):

- Link each metric to the goal that it tracks. ^metric-tracks-a-goal
- Normalize each raw count to a ratio, a percentage, or an average for each user, unless it counts new users. ^prefer-normalized-metrics

## Inputs

- The product or the feature, its users, and the decision that the metrics inform
- The data sources that exist: logs, analytics events, and surveys
- The strategy or the outcome that the product or the feature serves

## Procedure

1. Read each directive that this skill lists.
2. State the scope: the product or the feature, its users, and the decision that the metrics inform.
3. For each HEART category, decide if it applies. Write the goal of each category that applies.
4. For each goal, write the signals: the actions or attitudes of users that show success or failure. Name the data source of each signal.
5. For each signal, define a metric with its unit and its period.
6. If the scope is a whole product, choose the north star metric and its input metrics.
7. If the team uses OKRs, write an objective and its key results, with targets from the metrics.
8. Check that the team can measure each metric today. List the logging or the survey that each other metric needs.

## Output

A table with one row for each metric: the HEART category, the goal, the signal, the metric, its unit, its period, and its data source. For a whole product, the north star metric and its inputs. When the team uses OKRs, the objective and its key results.

## Validation

Check the output against each directive from the first step of the procedure, and report each one it misses. Each metric traces to a goal, and each goal traces to the scope of step 2.

## References

- You choose the categories, the goals, the signals, or the metrics. Read [HEART framework](../../references/heart-framework.md).
- You measure a whole product, not one feature. Read [North star metric](../../references/north-star-metric.md).
- The team sets its targets as objectives and key results. Read [Objectives and key results](../../references/objectives-and-key-results.md).
- You link a metric to its goal or choose its unit. Read [Product measurement](../../references/product-measurement.md).
