---
id: information-hierarchy
kind: densho:Concept
title: Information hierarchy
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
broader:
  - visual-design
---

## Definition

The organization of design elements so that the eye takes them in the order of their importance. Color and contrast, scale, and grouping set that order.

## Directives

- Make the primary action or the primary content of each screen its biggest element. ^make-most-important-biggest
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/#toc-2-scale-2
- Limit the text on each screen to `3` sizes. ^limit-text-sizes
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- Limit each screen to `2` elements at the largest size. ^limit-largest-elements
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- Use at most `3` contrast treatments of text on each screen, such as for headers, subheaders, and body text. ^limit-contrast-levels
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/#toc-1-color-and-contrast-1
- Use a bright color that is not warm only for the primary action or the primary content of a screen. ^reserve-bright-color
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/#toc-1-color-and-contrast-1
- Use a warm bright color, such as red, only for a warning or an error. ^reserve-warm-bright-color
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/#toc-1-color-and-contrast-1
- Mark the preferred button in a set of choices with a prominent style, not a larger size. ^mark-preferred-with-style
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/buttons
- Do not give a secondary button the color of the primary button. ^distinct-primary-button-color
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-similarity/
- Give each screen one primary action, unless the screen is a settings screen. ^one-primary-action
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- If a screen is a settings screen, give each control on it the same rank. ^settings-controls-same-rank
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
