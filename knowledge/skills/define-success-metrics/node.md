---
id: define-success-metrics
kind: ka:Skill
title: Define success metrics
status: proposed
origin: template
knowledge_type: domain
description: Define the goals, the signals, and the metrics of a product or a feature. Use when you decide how to measure the success of a product or a feature.
invocation: agent
uses:
  - product-measurement
  - heart-framework
  - north-star-metric
  - objectives-and-key-results
pointers:
  - kind: ka:TextPointer
    target: product-measurement
    trigger: You link a metric to its goal or choose its unit.
  - kind: ka:TextPointer
    target: heart-framework
    trigger: You choose the categories, the goals, the signals, or the metrics.
  - kind: ka:TextPointer
    target: north-star-metric
    trigger: You measure a whole product, not one feature.
  - kind: ka:TextPointer
    target: objectives-and-key-results
    trigger: The team sets its targets as objectives and key results.
---

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
