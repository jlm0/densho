---
id: responsive-design
kind: ka:PracticeArea
title: Responsive design
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
broader:
  - ui-ux-design
---

## Definition

Designing a layout that adapts to each screen size and resolution and stays usable on all of them. Flexible grids, fluid images, and breakpoints are its usual means.

## Directives

- Show content at a width of `320` CSS pixels with no horizontal scroll, unless the content needs a two-dimensional layout. ^reflow-at-narrow-width
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
- Define each breakpoint in relative units. ^relative-breakpoints
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
- Do not set text size with viewport units alone. ^no-viewport-only-text
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
- Prefer a single-column base layout over a multi-column base layout. ^single-column-base
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
