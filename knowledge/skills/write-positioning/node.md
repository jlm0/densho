---
id: write-positioning
kind: densho:Skill
title: Write the positioning of a product
status: proposed
origin: template
knowledge_type: domain
description: "Define the positioning of a product from its alternatives, unique attributes, value, target customers, and market category. Use when you write or change the positioning of a product. Do not use it for a brand positioning statement (`design-brand`)."
invocation: agent
skill_type: task
uses:
  - product-positioning
steps:
  - define-the-positioning
---

## Exit checklist

Check each line before you report the positioning as done.

- [ ] Each value claim links to a unique attribute, and each unique attribute links to an alternative that lacks it.
- [ ] Each component names the evidence behind it.
- [ ] The document marks the positioning as a candidate until the person confirms it with prospects or with the sales team.
- [ ] The report names each directive that the positioning misses.

## Output

- One positioning document with the `5` components in order
- A list of each directive that the positioning misses, with the reason

For the positioning statement and the rest of the brand, run `design-brand`.
