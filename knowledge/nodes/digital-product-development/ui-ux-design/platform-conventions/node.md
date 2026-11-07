---
id: platform-conventions
kind: densho:PracticeArea
title: Platform conventions
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/ten-usability-heuristics/
broader:
  - ui-ux-design
related:
  - usability-heuristics
pointers:
  - kind: densho:TextPointer
    target: apple-human-interface-guidelines
    trigger: You design an app for an Apple device.
  - kind: densho:TextPointer
    target: material-design
    trigger: You design for Android or with Material components.
---

## Definition

The rules that an operating system or a design language publishes for its own controls, gestures, layouts, and type. People learn these rules in the other apps on the platform and expect them in each new app. Heuristic 4 of Nielsen, consistency and standards, asks a product to follow them.

## Directives

- Follow the conventions of the target platform for each standard control, gesture, and layout. ^follow-platform-conventions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Use the standard glyph of the platform for each standard action, such as share or delete. ^platform-glyphs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/icon-usability/
  - sources: https://developer.apple.com/design/human-interface-guidelines/buttons
- Give each destination in a tab bar or a navigation bar a text label. ^label-each-tab
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/tab-bars
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/components/BottomNavigation.md
- Use a tab bar or a navigation bar only for navigation, not for actions. ^tabs-for-navigation
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/tab-bars
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/components/BottomNavigation.md
