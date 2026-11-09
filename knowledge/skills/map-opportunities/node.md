---
id: map-opportunities
kind: densho:Skill
title: Map the opportunities of an outcome
status: proposed
origin: template
knowledge_type: domain
description: "Map the needs of customers under a product outcome, and choose the target need and its solutions. Use when you map customer needs and solutions under a product outcome. Do not use it for assumption tests (`test-assumptions`)."
invocation: agent
skill_type: task
uses:
  - product-discovery
steps:
  - map-the-opportunities
  - choose-the-solutions
---

## Exit checklist

Check each line before you report the map as done.

- [ ] Steps `1` and `2` each have their output.
- [ ] The root of the tree holds `1` product outcome.
- [ ] Each opportunity names its interview note.
- [ ] Each solution sits under the target opportunity.
- [ ] The report names each directive that the tree misses, and each missing rule that the map reached.

## Output

- The opportunity solution tree as a nested list, from the outcome to the solutions, with the target opportunity marked
- A list of each directive that the tree misses, with the reason

To test the solutions, run `test-assumptions`.
