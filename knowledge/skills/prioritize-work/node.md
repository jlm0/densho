---
id: prioritize-work
kind: densho:Skill
title: Prioritize the work of a team
status: proposed
origin: template
knowledge_type: domain
description: "Order the items of a backlog or a roadmap by RICE score. Use when you set the order of the items in a backlog or a roadmap. Do not use it for the choice of a customer need (`map-opportunities`)."
invocation: agent
skill_type: task
uses:
  - product-prioritization
steps:
  - order-the-items
---

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
