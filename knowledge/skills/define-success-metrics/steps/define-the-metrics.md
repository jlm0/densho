---
title: Define the goals, the signals, and the metrics
pages:
  - target: product-measurement
    trigger: You link a metric to its goal or choose its unit.
  - target: heart-framework
    trigger: You measure the user experience of a product or a feature.
  - target: north-star-metric
    trigger: You choose the one metric that a product team works to move.
  - target: objectives-and-key-results
    trigger: You write objectives and key results for a team or a company.
directives:
  - write-success-measure
  - metric-tracks-a-goal
  - choose-heart-categories
  - goal-before-metric
  - specific-signals
  - normalize-raw-counts
  - engagement-per-user
branches:
  - condition: If the scope is a whole product
    directives:
      - one-north-star
      - no-user-count-north-star
      - leading-north-star
      - north-star-inputs
  - condition: If the team uses OKRs
    directives:
      - one-outcome-per-team
      - objectives-not-feature-lists
      - three-to-five-key-results
      - split-large-objectives
      - outcome-key-results
      - key-result-evidence
      - sufficient-key-results
      - committed-or-aspirational
      - score-key-results
      - okrs-apart-from-pay
      - postmortem-on-missed-commitment
missing_rules:
  - No directive of product measurement chooses the concept for a scope, such as OKRs for the period of a team.
---

## Procedure

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

## Output

A table with one row for each metric, the north star metric for a whole product, and the OKRs when the team uses them.
