---
id: define-success-metrics
kind: densho:Skill
title: Define success metrics
status: proposed
origin: template
knowledge_type: domain
description: "Define the goals, the signals, and the metrics of a product or a team. Use when you set a goal, a metric, or a target for a product, a feature, or a team. Do not use it for a strategy (`plan-product-strategy`)."
invocation: agent
skill_type: task
uses:
  - product-measurement
steps:
  - define-the-metrics
---

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
