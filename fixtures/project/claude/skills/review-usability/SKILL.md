---
name: review-usability
description: "Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a person asks for a usability review of a flow. Do not use it for a whole interface (`review-interface`) or an accessibility check (`audit-accessibility`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review the usability of a flow

## Run the skill

1. Check the work against each directive of the skill.
2. If a branch heading matches the work, check the work against each directive under it.
3. If you need the definition or the notes of a page, read the page.

## Review the flow

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

Pages:

- You judge the feedback, the exits, the confirmations, the error messages, or the help of the flow. Read [Usability heuristics](../../references/usability-heuristics.md).
- You judge the size or the position of a target. Read [Fitts's law](../../references/fitts-law.md).
- You judge the number of choices in a menu or a step. Read [Hick's law](../../references/hicks-law.md).
- You judge how people move between the screens of the flow. Read [Navigation](../../references/navigation.md).
- The flow runs on a platform with its own conventions. Read [Platform conventions](../../references/platform-conventions.md).

Directives:

- Show each frequently used option on the first screen. ^show-frequent-options-first
- Move each advanced or rarely used option to a secondary screen. ^move-advanced-options
- Give the secondary options one route from the first screen. ^one-route-to-secondary-options
- Limit progressive disclosure to `2` levels. ^limit-disclosure-levels
- Keep each disclosure control visible on the first screen. ^keep-disclosure-control-visible
- Name the hidden content in the label of each disclosure control. ^label-disclosure-control
- Mark the recommended option when a step asks the user to choose between options of equal rank. ^mark-recommended-option
- Give each frequent action an accelerator, such as a keyboard shortcut. ^accelerators-for-frequent-actions
- Give a visible control for each action that a shortcut or a gesture starts. ^visible-path-for-shortcuts
- Show the result of each user action on the screen. ^show-action-result
- Give each custom button a visible pressed state. ^show-pressed-state
- Show a busy indicator while an operation takes more than `1` second. ^show-busy-state
- Give an undo for each change that a user makes to their content or settings. ^undo-each-change
- Do not ask for confirmation of a routine action that has an undo. ^no-routine-confirmation
- Ask for confirmation before an action that destroys user work and has no undo. ^confirm-destructive-action
- Tell the user before the product takes an action with consequences for them. ^tell-before-consequences
- Give each modal view and each multi-step process a visible control that exits it. ^visible-exit
- Make each back control return to the previous screen, not to the start of the flow. ^back-one-step
- Do not disable the back button of the browser. ^keep-browser-back
- Show on each screen the information that the user needs from an earlier screen. ^no-recall-across-screens
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
- Set a focus order that keeps the meaning and the operation of the content. ^logical-focus-order
- Do not change the context when a control receives focus. ^no-change-on-focus
- Do not change the context when a user changes a setting, unless the control warns of it first. ^no-change-on-input
- Make the visible area of each target as large as its active area. ^visible-target-matches-active
- Make the text label of each icon button part of its target area. ^label-in-target
- Leave visible space between each pair of adjacent targets. ^space-between-targets
- Place controls that users press in sequence close to each other. ^sequence-targets-close
- Show the options of a menu next to the control that opens it. ^menu-near-its-control
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
- Keep repeated navigation elements in the same relative order on each screen. ^keep-navigation-order
- Show the current location of the user in the navigation. ^show-current-location
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page
- Use a tab bar or a navigation bar only for navigation, not for actions. ^tabs-for-navigation
- Give each destination in a tab bar or a navigation bar a text label. ^label-each-tab
- Give each finding a severity from `0` to `4`. ^rate-finding-severity

### If the screen holds a form

- Give each input field a label or an instruction. ^label-each-field
- Do not use placeholder text as the only label of a field. ^no-placeholder-as-label
- Declare the purpose of each field that collects data about the user, such as with `autocomplete`. ^declare-input-purpose
- Do not ask a user to type again a value that they entered earlier in the same process. ^no-redundant-entry
- Do not show an error for an empty field before the user submits the form. ^no-early-error
- Show each error message next to the element that caused it. ^error-near-source
- Keep the input of the user in each field that shows an error. ^keep-input-after-error
- When a check finds an input error, describe the error and its field in text. ^describe-input-error
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Write each error message in the words of the user, with no error code. ^plain-error-message
- Do not use words that blame the user, such as `invalid` or `illegal`, in an error message. ^no-blame-in-errors
- Show a warning that does not block the task in a different style from an error. ^warning-differs-from-error
- Ask for confirmation before a view with unsaved changes closes. ^confirm-unsaved-close
- Give a review step before each payment, each legal agreement, and each deletion of user data, unless it is reversible. ^review-before-commitment
- Place the submit button of a form next to its last field. ^submit-near-last-field

### If the screen holds a login

- Do not block paste or password autofill in a login field. ^allow-paste-in-login
- Do not require a puzzle or a memory test for authentication, unless another method needs neither. ^no-puzzle-login

### If the screen opens a dialog or an overlay

- Name the object and the effect of the action in each confirmation dialog. ^specific-confirmation
- Label each button of a confirmation dialog with its action, not with `Yes`, `No`, or `OK`. ^action-labels-in-dialogs
- Do not make a destructive button the default button of a dialog. ^no-destructive-default
- Make the back button close a full-screen overlay. ^back-closes-overlay
- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap

### If an operation takes more than `10` seconds

- Show a percent-done indicator for each operation that takes more than `10` seconds. ^percent-done-indicator
- Give a visible control to stop each operation that takes more than `10` seconds. ^stop-long-operation

### If the product removes an item that a user saved

- Do not remove an item that a user saved without a message that states why. ^explain-removed-items

### If the screen holds help or an instruction

- Put each help text next to the field or the step that it explains. ^help-in-context
- Write each help topic as a list of concrete steps. ^help-lists-steps
- Keep each repeated help mechanism, such as contact details or a chat, in the same relative order on each page. ^consistent-help-order
- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions

### If the product shows a new user its features

- Show a new user the features of a product one at a time. ^show-features-one-at-a-time

### If the screen is a settings screen

- Show the current value of each setting next to its name. ^show-current-setting-value

### If the design uses a gesture, a drag, a device motion, or a single-key shortcut

- Give each action that a multipoint or path-based gesture does a single-pointer alternative, unless the gesture is essential. ^single-pointer-alternative
- Give each drag action a single-pointer alternative that needs no drag, unless dragging is essential. ^drag-alternative
- Give each action that a device motion starts an on-screen control and a setting that disables the motion. ^motion-alternative
- Give each single-character keyboard shortcut a setting to disable it or change its key, unless it works only on focus. ^character-key-shortcuts

### If the screen sets a time limit

- Give the user a way to disable, change, or extend each time limit, unless the limit exceeds `20` hours. ^adjustable-time-limits

### If content shows on hover or focus

- Make content that appears on hover or focus dismissible without moving the pointer or the focus. ^dismissible-hover-content
- Keep content that appears on hover visible while the pointer moves over that content. ^hoverable-content
- Keep hover and focus content visible until the hover or the focus ends, or the user dismisses it. ^persistent-hover-content

### If the target is an Apple device

- In an `iOS` or `iPadOS` app, give each button a hit region of at least `44` by `44` points. ^apple-hit-region
- In an `iOS` app, use an action sheet, not an alert, for choices of an action that the user started. ^apple-action-sheet-for-choices
- Give each alert that offers a destructive action a `Cancel` button. ^apple-cancel-with-destructive
- Do not use an alert only to give information that needs no action. ^apple-no-information-alert
- Do not show an alert when the app starts. ^apple-no-launch-alert
- Do not open a modal view over another modal view. ^apple-one-modal-at-a-time
- In a `macOS` app, add an ellipsis to the title of each button that opens another window or view. ^apple-ellipsis-for-more-input
- Keep each tab bar item visible and enabled, even when its content is not available. ^apple-keep-tabs-enabled

### If the target is Android

- Make each touch target on Android at least `48` by `48` dp, even when it extends past the visible element. ^android-touch-target
- Give a navigation bar `3` to `5` destinations. ^navigation-bar-destinations

Output: A list of findings for the flow, sorted by severity.

## Exit checklist

- [ ] Each finding names a directive of this skill or a heuristic, or a label marks it as an opinion.
- [ ] The report states that each severity comes from one reviewer and needs a second review.

## Output

A list of findings, sorted by severity. Each finding names the screen, the element, the heuristic or the directive that it breaks, its severity, and the change that you recommend. The severity scale is `0` for no problem, `1` for a cosmetic problem, `2` for a minor problem, `3` for a major problem, and `4` for a problem that blocks a release.
