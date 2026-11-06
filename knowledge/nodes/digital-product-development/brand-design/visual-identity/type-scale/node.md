---
id: type-scale
kind: ka:Concept
title: Type scale
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://alistapart.com/article/more-meaningful-typography/
  - https://github.com/material-components/material-components-android/blob/master/docs/theming/Typography.md
broader:
  - visual-identity
related:
  - information-hierarchy
---

## Definition

The fixed set of text sizes and text styles that a brand uses. Tim Brown describes a modular scale: a start number, such as the size of the body text, multiplied and divided by a ratio, such as `1.618`, to give each size. Material Design names each text style by its role: display, headline, title, body, and label, each in a large, a medium, and a small size. A text style combines a typeface, a weight, a size, a letter spacing, and any change of case.

## Directives

- Set the base size of the type scale to the size of the body text. ^scale-from-body-size
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://alistapart.com/article/more-meaningful-typography/
- Take each text size in a design from the type scale. ^sizes-from-the-scale
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://alistapart.com/article/more-meaningful-typography/
- Record the base size and the ratio of the type scale in the brand guidelines. ^record-the-scale
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://alistapart.com/article/more-meaningful-typography/
- Define each text style with a typeface, a weight, a size, and a letter spacing. ^text-style-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Typography.md
- Name each text style by its role, such as display, headline, title, body, or label. ^text-style-roles
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Typography.md

## Notes

Brown chooses the body text size first, at the size where the text face looks crisp, and builds the scale from it. A second important number, such as the width of a media slot, can give a second strand of sizes. He records the base and the ratio in a comment at the top of the style sheet, so that other people can rebuild the scale and change it with care.

The information hierarchy concept limits each screen to three text sizes. Those sizes come from the scale.
