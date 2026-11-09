---
title: Define the behavior of each screen
pages:
  - target: progressive-disclosure
    trigger: You choose which options appear first.
  - target: hicks-law
    trigger: You choose the number of options in a menu, a step, or a first screen.
  - target: usability-heuristics
    trigger: You design feedback, an exit, a confirmation, an error message, or help.
  - target: fitts-law
    trigger: You choose the size or the position of a button, a link, or a menu.
  - target: interaction-design
    trigger: You decide how an interface responds to a person.
  - target: accessibility
    trigger: You build a control, a form, a text style, a color choice, or media.
directives:
  - show-frequent-options-first
  - move-advanced-options
  - one-route-to-secondary-options
  - limit-disclosure-levels
  - keep-disclosure-control-visible
  - label-disclosure-control
  - mark-recommended-option
  - accelerators-for-frequent-actions
  - visible-path-for-shortcuts
  - show-action-result
  - show-pressed-state
  - show-busy-state
  - undo-each-change
  - no-routine-confirmation
  - confirm-destructive-action
  - tell-before-consequences
  - visible-exit
  - back-one-step
  - keep-browser-back
  - no-recall-across-screens
  - keyboard-operable
  - logical-focus-order
  - no-change-on-focus
  - no-change-on-input
  - visible-target-matches-active
  - label-in-target
  - space-between-targets
  - sequence-targets-close
  - menu-near-its-control
  - minimum-target-size
branches:
  - condition: If the screen holds a form
    directives:
      - label-each-field
      - no-placeholder-as-label
      - declare-input-purpose
      - no-redundant-entry
      - no-early-error
      - error-near-source
      - keep-input-after-error
      - describe-input-error
      - suggest-error-fix
      - plain-error-message
      - no-blame-in-errors
      - warning-differs-from-error
      - confirm-unsaved-close
      - review-before-commitment
      - submit-near-last-field
  - condition: If the screen holds a login
    directives:
      - allow-paste-in-login
      - no-puzzle-login
  - condition: If the screen opens a dialog or an overlay
    directives:
      - specific-confirmation
      - action-labels-in-dialogs
      - no-destructive-default
      - back-closes-overlay
      - no-keyboard-trap
  - condition: If an operation takes more than `10` seconds
    directives:
      - percent-done-indicator
      - stop-long-operation
  - condition: If the product removes an item that a user saved
    directives:
      - explain-removed-items
  - condition: If the screen holds help or an instruction
    directives:
      - help-in-context
      - help-lists-steps
      - consistent-help-order
      - no-sensory-only-instructions
  - condition: If the product shows a new user its features
    directives:
      - show-features-one-at-a-time
  - condition: If the screen is a settings screen
    directives:
      - show-current-setting-value
  - condition: If the design uses a gesture, a drag, a device motion, or a single-key shortcut
    directives:
      - single-pointer-alternative
      - drag-alternative
      - motion-alternative
      - character-key-shortcuts
  - condition: If the screen sets a time limit
    directives:
      - adjustable-time-limits
  - condition: If content shows on hover or focus
    directives:
      - dismissible-hover-content
      - hoverable-content
      - persistent-hover-content
  - condition: If the target is an Apple device
    directives:
      - apple-hit-region
      - apple-action-sheet-for-choices
      - apple-cancel-with-destructive
      - apple-no-information-alert
      - apple-no-launch-alert
      - apple-one-modal-at-a-time
      - apple-ellipsis-for-more-input
  - condition: If the target is Android
    directives:
      - android-touch-target
missing_rules:
  - No directive covers the empty state of a screen or a list.
  - No directive covers a transition or an animation, because motion design has no node.
---

## Procedure

1. Sort the options by how frequently people use them.
2. Split the options into a first screen and a secondary screen.
3. Choose a control for each option.
4. State the result of each action and the screen that comes next.
5. Define the undo of each change to user content or settings.
6. Define the exit and the back path of each modal view and each multi-step process.
7. Set the order of the keyboard focus on each screen.
8. Set the size and the position of each target.

## Output

A design that states which controls appear on each screen, in what order, and what happens after each action.
