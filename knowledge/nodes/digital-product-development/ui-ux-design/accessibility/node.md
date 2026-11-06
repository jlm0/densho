---
id: accessibility
kind: ka:PracticeArea
title: Accessibility
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.w3.org/TR/WCAG22/
broader:
  - ui-ux-design
---

## Definition

Making a product usable by people with disabilities, including people with low vision, limited movement, or hearing loss.

## Directives

- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
  - scope: subtree
  - status: proposed
  - origin: template
  - also_attached_to: visual-design
  - also_attached_to: brand-design
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Give each meaningful image a text alternative. ^text-alternative
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html
- Hide each decorative image from assistive technology. ^hide-decoration
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html
- Give each input field a label or an instruction. ^label-each-field
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html

## Notes

The contrast rules read large text as `18` points or more. The standard also counts bold text of `14` points as large, so these rules are stricter for that one size.
