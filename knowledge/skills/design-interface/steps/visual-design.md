---
title: Lay out and style each screen
pages:
  - target: information-hierarchy
    trigger: You rank the elements of a screen.
  - target: visual-grouping
    trigger: You place, style, or frame related elements on a screen.
  - target: visual-communication
    trigger: You choose between prose and a visual form.
  - target: visual-identity
    trigger: You design or apply a logo, a brand color, or a type style.
  - target: type-scale
    trigger: You choose the typefaces, the text sizes, or the text styles of a brand.
  - target: responsive-design
    trigger: You fit a layout to a screen size.
  - target: accessibility
    trigger: You build a control, a form, a text style, a color choice, or media.
directives:
  - one-primary-action
  - make-most-important-biggest
  - limit-largest-elements
  - limit-text-sizes
  - limit-contrast-levels
  - reserve-bright-color
  - distinct-primary-button-color
  - mark-preferred-with-style
  - limit-color-palette
  - sizes-from-the-scale
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
  - contrast-regular-text
  - contrast-large-text
  - contrast-ui-components
  - contrast-graphics
  - no-color-only
  - keep-focus-visible
  - no-images-of-text
  - resize-text
  - single-column-base
  - layout-from-window-width
  - reflow-at-narrow-width
  - keep-groups-at-each-width
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
      - focus-not-obscured
  - condition: If the design adds a new glyph
    directives:
      - test-new-glyphs
  - condition: If the screen shows an image
    directives:
      - text-alternative
      - hide-decoration
  - condition: If the screen shows video, audio, or content that moves, blinks, flashes, or updates by itself
    directives:
      - caption-prerecorded-video
      - caption-live-video
      - describe-prerecorded-video
      - alternative-for-silent-video
      - transcript-for-audio-only
      - pause-autoplay-audio
      - pause-moving-content
      - pause-auto-updates
      - no-flashing-content
  - condition: If the product runs on a phone or a tablet
    directives:
      - no-orientation-lock
  - condition: If the target is an Apple device
    directives:
      - apple-safe-area
      - apple-default-body-size
      - apple-minimum-text-size
      - apple-dynamic-type
      - apple-scale-icons-with-text
      - apple-both-appearances
      - apple-no-appearance-setting
      - apple-system-color-meaning
  - condition: If the target is Android
    directives:
      - android-minimum-body-size
      - android-text-in-sp
      - android-test-size-classes
---

## Procedure

1. Group the options on each screen.
2. Name each group.
3. Name the element that a viewer sees first, then second, then third.
4. Compare that order with the order of importance for the task.
5. Apply the brand guidelines.
6. Mark each sentence and label that a glyph, an image, or a grouping replaces.
7. Check the layout at the narrowest screen width.

## Output

The layout, the type, the color, the imagery, and the spacing of each screen.
