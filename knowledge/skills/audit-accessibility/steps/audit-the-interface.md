---
title: Audit the interface
pages:
  - target: accessibility
    trigger: You check the interface against a success criterion or its exception.
directives:
  - state-the-audit-scope
  - audit-complete-processes
  - contrast-regular-text
  - contrast-large-text
  - no-color-only
  - keyboard-operable
  - keep-focus-visible
  - minimum-target-size
  - name-non-text-controls
  - structure-in-code
  - reading-order-in-code
  - resize-text
  - no-images-of-text
  - contrast-ui-components
  - contrast-graphics
  - allow-text-spacing
  - bypass-repeated-blocks
  - descriptive-page-title
  - logical-focus-order
  - link-purpose
  - two-ways-to-each-page
  - descriptive-headings-and-labels
  - act-on-pointer-up
  - label-in-name
  - declare-page-language
  - declare-passage-language
  - no-change-on-focus
  - no-change-on-input
  - consistent-identification
  - name-role-value
  - expose-status-messages
  - keep-navigation-order
branches:
  - condition: If the interface holds a form
    directives:
      - label-each-field
      - declare-input-purpose
      - describe-input-error
      - suggest-error-fix
      - review-before-commitment
      - no-redundant-entry
  - condition: If the interface holds a login
    directives:
      - allow-paste-in-login
      - no-puzzle-login
  - condition: If the interface opens a dialog or an overlay
    directives:
      - no-keyboard-trap
  - condition: If the interface holds help or an instruction
    directives:
      - no-sensory-only-instructions
      - consistent-help-order
  - condition: If the interface uses a gesture, a drag, a device motion, or a single-key shortcut
    directives:
      - character-key-shortcuts
      - single-pointer-alternative
      - motion-alternative
      - drag-alternative
  - condition: If the interface sets a time limit
    directives:
      - adjustable-time-limits
  - condition: If content shows on hover or focus
    directives:
      - dismissible-hover-content
      - hoverable-content
      - persistent-hover-content
  - condition: If the interface holds a sticky header, a banner, or another fixed element
    directives:
      - focus-not-obscured
  - condition: If the interface shows an image
    directives:
      - text-alternative
      - hide-decoration
  - condition: If the interface shows video, audio, or content that moves, blinks, flashes, or updates by itself
    directives:
      - transcript-for-audio-only
      - alternative-for-silent-video
      - caption-prerecorded-video
      - describe-prerecorded-video
      - caption-live-video
      - pause-autoplay-audio
      - pause-moving-content
      - pause-auto-updates
      - no-flashing-content
  - condition: If the product runs on a phone or a tablet
    directives:
      - no-orientation-lock
---

## Procedure

01. Collect the interface, as a design or as running code.
02. If the person names no conformance level, use level AA.
03. Collect the browsers, the devices, and the assistive technologies that the product supports.
04. State the scope: the screens, the complete processes, the conformance level, and the supported technologies.
05. List the common screens, the essential functions, and each complete process of the interface.
06. Check each screen against each directive.
07. Use a keyboard alone, a screen reader, text at `200` percent, and a width of `320` CSS pixels.
08. Check each step of each complete process in the same way.
09. Write each failure with the screen, the element, the directive, and the change that you recommend.
10. List each directive with no content to check, such as the caption rules on a screen with no video.

## Output

A list of failures, and a list of the directives with no content to check.
