---
title: Review the flow
pages:
  - target: usability-heuristics
    trigger: You judge the feedback, the exits, the confirmations, the error messages, or the help of the flow.
  - target: fitts-law
    trigger: You judge the size or the position of a target.
  - target: hicks-law
    trigger: You judge the number of choices in a menu or a step.
  - target: navigation
    trigger: You judge how people move between the screens of the flow.
  - target: platform-conventions
    trigger: The flow runs on a platform with its own conventions.
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
  - keep-navigation-order
  - show-current-location
  - two-ways-to-each-page
  - tabs-for-navigation
  - label-each-tab
  - rate-finding-severity
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
      - apple-keep-tabs-enabled
  - condition: If the target is Android
    directives:
      - android-touch-target
      - navigation-bar-destinations
---

## Procedure

01. Collect the screens of the flow in the order of the task, as designs or a running interface.
02. State the scope of the review: the users, the task, and the platform.
03. Follow the task once from its start to its end to learn the flow.
04. Do not record a finding on this first pass.
05. Follow the task a second time.
06. On each screen, check each heuristic and each directive.
07. Check the size and the position of each target, and the number of choices at each step.
08. Write each finding with the screen, the element, the heuristic or the directive, and the change that you recommend.
09. Give each finding its severity.
10. Sort the findings from the highest severity.

## Output

A list of findings for the flow, sorted by severity.
