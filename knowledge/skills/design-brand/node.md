---
id: design-brand
kind: densho:Skill
title: Design a brand
status: proposed
origin: template
knowledge_type: domain
description: "Define a brand, from its strategy to its logo, colors, type, and guidelines. Use when you define or change the strategy, the visual identity, or the guidelines of a brand. Do not use it for the voice alone (`define-brand-voice`)."
invocation: agent
skill_type: task
uses:
  - brand-strategy
  - visual-identity
  - brand-systems
steps:
  - define-the-strategy
  - define-the-visual-identity
  - write-the-guidelines
---

## Exit checklist

Check each line before you report the brand as done.

- [ ] Each section from step `1` that the task creates or changes has its output.
- [ ] The positioning statement is false with the name of a competitor in place of the name of the brand.
- [ ] Each pair of brand colors for text or controls passes the contrast rules.
- [ ] Each value in the guidelines matches the value in the token files.
- [ ] The report names each directive that the brand misses, and each missing rule that the brand reached.

## Output

- One set of brand guidelines in one online source, with the asset files and the token files beside it. The guidelines hold the strategy, the architecture where it applies, the logo, the colors, the typography, the voice and tone, and the label of each element.
- A list of each directive that the brand misses, with the reason

To check the touchpoints of the brand against the guidelines, run `audit-brand-consistency`.
