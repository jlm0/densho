---
id: apple-human-interface-guidelines
kind: ka:Concept
title: Apple Human Interface Guidelines
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://developer.apple.com/design/human-interface-guidelines
broader:
  - platform-conventions
---

## Definition

The design guidance that Apple publishes for iOS, iPadOS, macOS, tvOS, visionOS, and watchOS. The guidelines have no version number. Each page carries a change log with the date of each change. Apple measures sizes in points, and its system colors and text styles adapt to the light and dark appearance, to Dynamic Type, and to the accessibility settings.

## Directives

- In an `iOS` or `iPadOS` app, give each button a hit region of at least `44` by `44` points. ^apple-hit-region
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/buttons
- In an `iOS` or `iPadOS` app, do not set text below `11` points. ^apple-minimum-text-size
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/accessibility
- In an `iOS` or `iPadOS` app, use `17` points as the default size of body text. ^apple-default-body-size
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Make each layout adapt to each Dynamic Type size. ^apple-dynamic-type
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/typography
- Increase the size of each meaningful icon when the text size increases. ^apple-scale-icons-with-text
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/typography
- Do not copy the value of a system color into the code. ^apple-system-color-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/color
- Do not give a system color a new meaning. ^apple-system-color-meaning
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/color
- Check each screen for legibility in both the light and the dark appearance. ^apple-both-appearances
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/dark-mode
- Do not add an appearance setting that overrides the system light or dark mode. ^apple-no-appearance-setting
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/dark-mode
- Keep each tab bar item visible and enabled, even when its content is not available. ^apple-keep-tabs-enabled
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/tab-bars
- Do not show an alert when the app starts. ^apple-no-launch-alert
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/alerts
- Do not use an alert only to give information that needs no action. ^apple-no-information-alert
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/alerts
- Give each alert that offers a destructive action a `Cancel` button. ^apple-cancel-with-destructive
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/alerts
- In an `iOS` app, use an action sheet, not an alert, for choices of an action that the user started. ^apple-action-sheet-for-choices
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/alerts
- Do not open a modal view over another modal view. ^apple-one-modal-at-a-time
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/modality
- Keep each control and each piece of primary content inside the safe area. ^apple-safe-area
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/layout
- In a `macOS` app, add an ellipsis to the title of each button that opens another window or view. ^apple-ellipsis-for-more-input
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/buttons

## Notes

The buttons page gives `44` by `44` points as the general hit region of a button, and `60` by `60` points in visionOS. The accessibility page gives `28` by `28` points as the smallest control size on iOS. The default sizes of body text on the other platforms are `13` points on macOS, `29` on tvOS, `17` on visionOS, and `16` on watchOS.
