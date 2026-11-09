---
id: review-interface
kind: densho:Skill
title: Review an interface
status: proposed
origin: template
knowledge_type: domain
description: "Review an interface for its hierarchy, its usability, and its accessibility. Use when a screen or a flow is ready for review. Do not use it for a design (`design-interface`) or a code change (`review-code-change`)."
invocation: agent
skill_type: lens
uses:
  - ui-ux-design
steps:
  - run-the-lenses
pointers:
  - kind: densho:SkillPointer
    target: review-screen-hierarchy
    trigger: You review a screen of the interface.
  - kind: densho:SkillPointer
    target: review-usability
    trigger: You review a flow of the interface.
  - kind: densho:SkillPointer
    target: audit-accessibility
    trigger: You check the interface for accessibility.
---

## Exit checklist

- [ ] Each screen has a hierarchy review.
- [ ] Each flow has a usability review.
- [ ] The interface has an accessibility check.

## Output

One report with a section for each skill and its findings.
