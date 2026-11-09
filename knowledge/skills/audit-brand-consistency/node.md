---
id: audit-brand-consistency
kind: densho:Skill
title: Audit brand consistency
status: proposed
origin: template
knowledge_type: domain
description: "Check the touchpoints of a brand against its guidelines, and list each inconsistency. Use when you review the touchpoints of a brand for consistency. Do not use it for a change to the brand (`design-brand`)."
invocation: agent
skill_type: lens
uses:
  - visual-identity
  - brand-logo
  - color-roles
  - type-scale
  - distinctive-brand-assets
  - brand-voice
  - brand-guidelines
steps:
  - audit-the-touchpoints
---

## Exit checklist

- [ ] Each finding names a rule of the guidelines or a directive of this skill.
- [ ] Each touchpoint in the list has a result.

## Output

A table with one row for each finding: the touchpoint, the element, the rule that applies, what the sample shows, and the fix. Below it, a list of the gaps and the conflicts in the guidelines.
