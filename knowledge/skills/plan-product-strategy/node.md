---
id: plan-product-strategy
kind: densho:Skill
title: Write a strategy
status: proposed
origin: template
knowledge_type: domain
description: "Write a strategy as a diagnosis, a guiding policy, and coherent actions. Use when you write or review the strategy of a product, a team, or a company. Do not use it for metrics (`define-success-metrics`) or an order of work (`prioritize-work`)."
invocation: agent
skill_type: task
uses:
  - strategy-formulation
steps:
  - write-the-strategy
---

## Exit checklist

Check each line before you report the strategy as done.

- [ ] The diagnosis names `1` main challenge.
- [ ] The guiding policy links to each obstacle that the diagnosis names.
- [ ] Each action links to the guiding policy.
- [ ] Each goal or target stays a goal, apart from the strategy.
- [ ] A new reader states the challenge, the approach, and the first actions from the document alone.
- [ ] The report names each directive that the strategy misses.

## Output

- One strategy document with 4 sections: the diagnosis, the guiding policy, the coherent actions, and what the strategy sets aside
- A list of each directive that the strategy misses, with the reason

For the metrics of the strategy, run `define-success-metrics`.
