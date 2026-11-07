---
id: interaction-design
kind: densho:PracticeArea
title: Interaction design
status: proposed
origin: template
knowledge_type: domain
broader:
  - ui-ux-design
pointers:
  - kind: densho:TextPointer
    target: progressive-disclosure
    trigger: You choose which options appear first.
  - kind: densho:TextPointer
    target: navigation
    trigger: You design how people move between screens.
  - kind: densho:TextPointer
    target: usability-heuristics
    trigger: You design feedback, an exit, a confirmation, an error message, or help.
  - kind: densho:TextPointer
    target: fitts-law
    trigger: You choose the size or the position of a button, a link, or a menu.
  - kind: densho:TextPointer
    target: hicks-law
    trigger: You choose the number of options in a menu, a step, or a first screen.
---

## Definition

The design of how an interface responds when people act on it: which controls appear, in what order, and what happens next.

## Directives

- Show the result of each user action on the screen. ^show-action-result
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Give each custom button a visible pressed state. ^show-pressed-state
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/buttons
