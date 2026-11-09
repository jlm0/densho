---
id: define-brand-voice
kind: densho:Skill
title: Define the voice of a brand
status: proposed
origin: template
knowledge_type: domain
description: "Define the voice traits and the tone guidance of a brand. Use when you define or change the voice of a brand. Do not use it for the copy of a product (`design-content`)."
invocation: agent
skill_type: task
uses:
  - brand-voice
steps:
  - define-the-voice
  - write-the-tone-guidance
---

## Exit checklist

Check each line before you report the guide as done.

- [ ] Steps `1` and `2` each have their output.
- [ ] Each voice trait has an explanation and a trait to avoid.
- [ ] Each piece of tone guidance names a type of message and a reader state.
- [ ] Each example message fits the tone profile.
- [ ] The report names each directive that the guide misses, and the missing rule that the guide reached.

## Output

- A voice and tone guide: the personality, the tone profile, the tone words and the anti-tone words, the voice traits, and the tone guidance for each type of message
- The plan of the test with users
- A list of each directive that the guide misses, with the reason

To write the copy of the product in this voice, run `design-content`.
