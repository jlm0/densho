---
title: Review the screen
pages:
  - target: information-hierarchy
    trigger: You judge which element a viewer sees first.
  - target: visual-grouping
    trigger: You judge which elements read as one group.
  - target: visual-communication
    trigger: You find prose that a visual form replaces.
directives:
  - one-primary-action
  - make-most-important-biggest
  - limit-largest-elements
  - limit-text-sizes
  - limit-contrast-levels
  - reserve-bright-color
  - distinct-primary-button-color
  - mark-preferred-with-style
  - place-related-elements-close
  - no-unrelated-group
  - heading-near-its-section
  - prefer-space-over-divider
  - boundary-for-fixed-space
  - same-style-same-function
  - one-link-color
  - no-link-color-on-plain-text
  - no-decoration-like-control
  - label-glyphs
  - no-hover-labels
  - no-shared-glyph
  - platform-glyphs
  - prefer-visual-form
  - no-repeated-text
branches:
  - condition: If the screen holds a form
    directives:
      - group-related-fields
      - place-label-near-field
  - condition: If the screen is a settings screen
    directives:
      - settings-controls-same-rank
  - condition: If the screen holds a grid of items, a carousel, tabs, or a sticky header
    directives:
      - contain-item-parts
      - show-partial-next-item
      - tab-joins-panel
      - separate-sticky-header
  - condition: If the design adds a new glyph
    directives:
      - test-new-glyphs
---

## Procedure

1. Collect the screen, as a design or a running interface, and the task that a person does on it.
2. Name the element that a viewer sees first, then second, then third.
3. Compare that order with the order of importance for the task.
4. Mark each group that the spacing shows.
5. Compare the marked groups with the groups that the task needs.
6. Mark each sentence and label that a glyph, an image, or a grouping replaces.
7. Write each finding with the element, the directive that it breaks, and the change that you recommend.

## Output

A list of findings for the screen.
