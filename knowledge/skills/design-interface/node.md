---
id: design-interface
kind: densho:Skill
title: Design a user interface
status: proposed
origin: template
knowledge_type: domain
description: "Design a new or changed screen or flow, from its structure and behavior to its layout and components. Use when you create or change a user interface: a screen, a form, a settings page, or a flow. Do not use it for a review (`review-interface`), a brand (`design-brand`), or interface copy alone (`design-content`)."
invocation: agent
skill_type: task
uses:
  - ui-ux-design
steps:
  - frame-the-task
  - information-architecture
  - interaction-design
  - visual-design
  - design-systems
---

## Exit checklist

Check each line before you report the design as done.

- [ ] Steps `1` to `5` each have their output.
- [ ] Each screen holds only the content and the controls that the task needs.
- [ ] Each screen has one primary action, or it is a settings screen.
- [ ] Each action has a stated result, and each change has an undo or a confirmation.
- [ ] Each text and each control meets its contrast ratio.
- [ ] Each screen works at `320` CSS pixels wide and at a text size of `200` percent.
- [ ] Each color, size, and space comes from a token.
- [ ] Each branch heading from step `1` has its directives checked.
- [ ] The report names each directive that the design misses, and each missing rule that the design reached.

## Output

- The outputs of steps 1 to 5, as one design for each screen and each flow
- A list of each directive that the design misses, with the reason

For the code of the design, run `engineer-software`.
