---
id: material-design
kind: densho:Concept
title: Material Design
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://developer.android.com/design/ui/mobile/guides/foundations/accessibility
  - https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
  - https://github.com/material-components/material-components-android/blob/master/docs/components/BottomNavigation.md
broader:
  - platform-conventions
---

## Definition

The open design system of Google, and the base of the Android interface. The current version is Material 3. Android measures layout in density-independent pixels (`dp`) and text in scalable pixels (`sp`), which follow the font size setting of the user. Window size classes group the width of the app window: compact under `600` dp, medium from `600` dp, expanded from `840` dp, large from `1200` dp, and extra large from `1600` dp.

## Directives

- Make each touch target on Android at least `48` by `48` dp, even when it extends past the visible element. ^android-touch-target
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.android.com/design/ui/mobile/guides/foundations/accessibility
- Set each font size on Android in `sp`. ^android-text-in-sp
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.android.com/design/ui/mobile/guides/foundations/accessibility
- Do not set body text on Android below `12` sp. ^android-minimum-body-size
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.android.com/design/ui/mobile/guides/foundations/accessibility
- Give a navigation bar `3` to `5` destinations. ^navigation-bar-destinations
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/components/BottomNavigation.md
- Test each Android layout at the compact, medium, and expanded window width classes. ^android-test-size-classes
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes

## Notes

A window size class comes from the window of the app, not from the device. Split screen, a resizable window, or a foldable can give a phone or a tablet any class.
