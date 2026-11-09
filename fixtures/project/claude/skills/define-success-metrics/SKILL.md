---
name: define-success-metrics
description: "Define the goals, the signals, and the metrics of a product or a team. Use when you set a goal, a metric, or a target for a product, a feature, or a team. Do not use it for a strategy (`plan-product-strategy`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Define success metrics

## Run the skill

1. Follow each directive of the skill.
2. If a branch heading matches the work, follow each directive under it.
3. If you need the definition or the notes of a page, read the page.

## Define the goals, the signals, and the metrics

01. State the scope: the product or the feature, its users, and the decision that the metrics inform.
02. Collect the strategy or the outcome that the product or the feature serves.
03. Collect the data sources that exist: logs, analytics events, and surveys.
04. State for each HEART category whether it applies.
05. Write the goal of each category that applies.
06. For each goal, write the signals: the actions or the attitudes of users that show success or failure.
07. Name the data source of each signal.
08. For each signal, define a metric with its unit and its period.
09. If the scope is a whole product, choose the north star metric and its input metrics.
10. If the team uses OKRs, write each objective and its key results, with targets from the metrics.
11. Check that a data source records each metric today.
12. List the logging or the survey that each other metric needs.

Missing rule: No directive of product measurement chooses the concept for a scope, such as OKRs for the period of a team.

Pages:

- You link a metric to its goal or choose its unit. Read [Product measurement](../../references/product-measurement.md).
- You measure the user experience of a product or a feature. Read [HEART framework](../../references/heart-framework.md).
- You choose the one metric that a product team works to move. Read [North star metric](../../references/north-star-metric.md).
- You write objectives and key results for a team or a company. Read [Objectives and key results](../../references/objectives-and-key-results.md).

Directives:

- Write the success measure of each feature before you build the feature. ^write-success-measure
- Link each metric to the goal that it tracks. ^metric-tracks-a-goal
- State for each HEART category whether the product uses it. ^choose-heart-categories
- Write the goal of each HEART category before its signals and its metrics. ^goal-before-metric
- Choose signals that change only when the user experience changes. ^specific-signals
- Normalize each raw count to a ratio, a percentage, or an average for each user, unless it counts new users. ^normalize-raw-counts
- Report each engagement metric as an average for each user, not as a total. ^engagement-per-user

### If the scope is a whole product

- Choose one north star metric for each product. ^one-north-star
- Do not use active users or registered users as the north star metric. ^no-user-count-north-star
- Do not use a lagging measure such as revenue as the north star metric. ^leading-north-star
- Choose `3` to `5` input metrics that drive the north star metric and that the team influences. ^north-star-inputs

### If the team uses OKRs

- Set one outcome for each product team. ^one-outcome-per-team
- Give each product team business objectives with key results, not a list of features to build. ^objectives-not-feature-lists
- Write `3` to `5` key results for each objective. ^three-to-five-key-results
- If a score of `1.0` on `5` key results does not achieve an objective, split the objective. ^split-large-objectives
- Write each key result as a measured outcome, not as an activity. ^outcome-key-results
- Name the evidence of completion of each key result. ^key-result-evidence
- Write enough key results that a score of `1.0` on each one achieves the objective. ^sufficient-key-results
- Mark each OKR as committed or aspirational. ^committed-or-aspirational
- Give each key result a score from `0.0` to `1.0` at the end of the cycle. ^score-key-results
- Do not link OKR scores to compensation. ^okrs-apart-from-pay
- Write a postmortem for each committed OKR that ends below `1.0`. ^postmortem-on-missed-commitment

Output: A table with one row for each metric, the north star metric for a whole product, and the OKRs when the team uses them.

## Exit checklist

Check each line before you report the metrics as done.

- [ ] Each metric links to a goal, and each goal links to the scope of the metrics.
- [ ] Each metric has a unit, a period, and a data source.
- [ ] Each metric with no data source today names the logging or the survey that it needs.
- [ ] The report names each directive that the metrics miss.

## Output

- A table with one row for each metric: the HEART category, the goal, the signal, the metric, its unit, its period, and its data source
- For a whole product, the north star metric and its input metrics
- When the team uses OKRs, each objective and its key results
- A list of each directive that the metrics miss, with the reason

To find the customer needs under the outcome metric, run `map-opportunities`.
