---
id: design-settings-interface
kind: densho:Skill
title: Design a settings interface
status: proposed
origin: template
knowledge_type: domain
description: Design a settings interface from its options and its users. Use when you design or change a settings screen.
invocation: agent
uses:
  - progressive-disclosure
  - information-hierarchy
  - visual-grouping
  - brand-design
  - responsive-design
exceptions:
  - directive: one-primary-action
    reason: A settings screen holds controls of equal rank.
    status: proposed
pointers:
  - kind: densho:TextPointer
    target: progressive-disclosure
    trigger: You choose which settings appear first.
  - kind: densho:TextPointer
    target: information-hierarchy
    trigger: You rank the settings on a screen.
  - kind: densho:TextPointer
    target: visual-grouping
    trigger: You group the settings on a screen.
  - kind: densho:TextPointer
    target: accessibility
    trigger: You choose a control for a setting.
  - kind: densho:TextPointer
    target: brand-design
    trigger: You choose a color, a typeface, or the voice of a message.
  - kind: densho:TextPointer
    target: responsive-design
    trigger: You fit the settings to a narrow screen.
---

## Directives

- Show the current value of each setting next to its name. ^show-current-setting-value
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template

## Inputs

- The list of settings, with what each one changes
- Who changes each setting, and how frequently, from usage data or task analysis if the project has it
- The brand definition of the project

## Procedure

1. Read each directive that this skill lists.
2. Rank the settings by how frequently people change them.
3. Split the settings into a first screen and a secondary screen.
4. Group the settings on each screen, and name each group.
5. Choose a control for each setting, then apply the brand definition.
6. Check the layout at the narrowest screen width.

## Output

A settings design that states which settings sit on which screen, how they are grouped, and which control each one uses.

## Validation

Check the design against each directive from the first step of the procedure, and report each one it misses.
