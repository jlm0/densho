---
id: review-interface
kind: densho:Skill
title: Review an interface
status: proposed
origin: template
knowledge_type: domain
description: Review an interface for its hierarchy, its usability, and its accessibility. Use when a screen or a flow is ready for review.
invocation: agent
skill_type: lens
uses:
  - ui-ux-design
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

## Inputs

- The screens and the flows of the interface, as designs or as a running product

## Procedure

1. Run the skill `review-screen-hierarchy` on each screen.
2. Run the skill `review-usability` on each flow.
3. Run the skill `audit-accessibility` on the interface.
4. Put the findings of the 3 skills in one report, with a section for each skill.

## Output

One report with a section for each skill and its findings.

## Validation

Each screen has a hierarchy review, each flow has a usability review, and the interface has an accessibility check.
