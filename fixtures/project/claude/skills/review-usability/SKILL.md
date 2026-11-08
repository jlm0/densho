---
name: review-usability
description: "Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a person asks for a usability review of a flow."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review the usability of a flow

If compaction cuts this skill, invoke the skill again.

## Directives

From [Accessibility](../../references/accessibility.md):

- Run each single-pointer action on the up event, not on the down event. ^act-on-pointer-up
- Keep each text visible when a user raises its line, paragraph, letter, or word spacing. ^allow-text-spacing
- Give components with the same function the same label and the same glyph on each page. ^consistent-identification
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components
- Declare the purpose of each field that collects data about the user, such as with `autocomplete`. ^declare-input-purpose
- Declare the main language of each page in the code. ^declare-page-language
- When a check finds an input error, describe the error and its field in text. ^describe-input-error
- Make each heading and label state the topic or the purpose of its content. ^descriptive-headings-and-labels
- Give each page a title that states its topic or purpose. ^descriptive-page-title
- Expose each status message to assistive technology without moving the focus to it. ^expose-status-messages
- Do not hide the focused control completely behind a sticky header, a banner, or another element. ^focus-not-obscured
- Hide each decorative image from assistive technology. ^hide-decoration
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
- Give each input field a label or an instruction. ^label-each-field
- Include the visible label text of each control in its accessible name. ^label-in-name
- State the purpose of each link in its text or in the sentence that holds it. ^link-purpose
- Set a focus order that keeps the meaning and the operation of the content. ^logical-focus-order
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
- Expose the name, the role, and the state of each custom control to assistive technology. ^name-role-value
- Do not change the context when a control receives focus. ^no-change-on-focus
- Do not change the context when a user changes a setting, unless the control warns of it first. ^no-change-on-input
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap
- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock
- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions
- Keep the order of the content in the code the same as its visual reading order. ^reading-order-in-code
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Use the element or role that matches the visual structure of each heading, list, table, and form label. ^structure-in-code
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Give each meaningful image a text alternative. ^text-alternative
- Give a way to bypass each block of content that repeats across pages. ^bypass-repeated-blocks
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page

From [Information architecture](../../references/information-architecture.md):

- Define a controlled vocabulary for the content of each product. ^define-controlled-vocabulary

From [Responsive design](../../references/responsive-design.md):

- Keep the related elements of each group close together at each breakpoint. ^keep-groups-at-each-width
- Choose each layout from the width of the window, not from the type of device. ^layout-from-window-width
- Do not set text size with viewport units alone. ^no-viewport-only-text
- Show content at a width of `320` CSS pixels with no horizontal scroll, unless the content needs a two-dimensional layout. ^reflow-at-narrow-width
- Define each breakpoint in relative units. ^relative-breakpoints
- Build each base layout as a single column. ^single-column-base

From [UI/UX design](../../references/ui-ux-design.md):

- Do not add a sentence that repeats what a heading, a label, or a value states. ^no-repeated-text
- Use one word for one meaning in each interface. ^one-word-one-meaning
- Show only the content and the controls that the current task needs. ^show-what-the-task-needs

From [Interaction design](../../references/interaction-design.md):

- Show the result of each user action on the screen. ^show-action-result
- Give each custom button a visible pressed state. ^show-pressed-state

From [Usability heuristics](../../references/usability-heuristics.md):

- Give each frequent action an accelerator, such as a keyboard shortcut. ^accelerators-for-frequent-actions
- Label each button of a confirmation dialog with its action, not with `Yes`, `No`, or `OK`. ^action-labels-in-dialogs
- Make the back button close a full-screen overlay. ^back-closes-overlay
- Make each back control return to the previous screen, not to the start of the flow. ^back-one-step
- Ask for confirmation before an action that destroys user work and has no undo. ^confirm-destructive-action
- Ask for confirmation before a view with unsaved changes closes. ^confirm-unsaved-close
- Show each error message next to the element that caused it. ^error-near-source
- Do not remove an item that a user saved without a message that states why. ^explain-removed-items
- Put each help text next to the field or the step that it explains. ^help-in-context
- Write each help topic as a list of concrete steps. ^help-lists-steps
- Do not disable the back button of the browser. ^keep-browser-back
- Keep the input of the user in each field that shows an error. ^keep-input-after-error
- Do not use words that blame the user, such as `invalid` or `illegal`, in an error message. ^no-blame-in-errors
- Do not make a destructive button the default button of a dialog. ^no-destructive-default
- Do not show an error for an empty field before the user submits the form. ^no-early-error
- Do not use placeholder text as the only label of a field. ^no-placeholder-as-label
- Show on each screen the information that the user needs from an earlier screen. ^no-recall-across-screens
- Do not ask for confirmation of a routine action that has an undo. ^no-routine-confirmation
- Show a percent-done indicator for each operation that takes more than `10` seconds. ^percent-done-indicator
- Write each error message in the words of the user, with no error code. ^plain-error-message
- Show a busy indicator while an operation takes more than `1` second. ^show-busy-state
- Name the object and the effect of the action in each confirmation dialog. ^specific-confirmation
- Give a visible control to stop each operation that takes more than `10` seconds. ^stop-long-operation
- Tell the user before the product takes an action with consequences for them. ^tell-before-consequences
- Give an undo for each change that a user makes to their content or settings. ^undo-each-change
- Use the words of the users in each label and message, not internal terms. ^use-the-words-of-users
- Give each modal view and each multi-step process a visible control that exits it. ^visible-exit
- Give a visible control for each action that a shortcut or a gesture starts. ^visible-path-for-shortcuts
- Show a warning that does not block the task in a different style from an error. ^warning-differs-from-error

From [Platform conventions](../../references/platform-conventions.md):

- Follow the conventions of the target platform for each standard control, gesture, and layout. ^follow-platform-conventions
- Give each destination in a tab bar or a navigation bar a text label. ^label-each-tab
- Use the standard glyph of the platform for each standard action, such as share or delete. ^platform-glyphs
- Use a tab bar or a navigation bar only for navigation, not for actions. ^tabs-for-navigation

From [Navigation](../../references/navigation.md):

- Keep repeated navigation elements in the same relative order on each screen. ^keep-navigation-order
- Show the current location of the user in the navigation. ^show-current-location

From [Fitts's law](../../references/fitts-law.md):

- Make the text label of each icon button part of its target area. ^label-in-target
- Show the options of a menu next to the control that opens it. ^menu-near-its-control
- Place controls that users press in sequence close to each other. ^sequence-targets-close
- Leave visible space between each pair of adjacent targets. ^space-between-targets
- Place the submit button of a form next to its last field. ^submit-near-last-field
- Make the visible area of each target as large as its active area. ^visible-target-matches-active

From [Hick's law](../../references/hicks-law.md):

- Mark the recommended option when a step asks the user to choose between options of equal rank. ^mark-recommended-option
- Show a new user the features of a product one at a time. ^show-features-one-at-a-time

From [Review the usability of a flow](SKILL.md):

- Give each finding a severity from `0` to `4`. ^rate-finding-severity

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.

## Inputs

- The flow: its screens in the order of the task, as designs or a running interface
- The task, the users, and the target platform of the flow

## Procedure

1. Read each directive that this skill lists.
2. State the scope of the review: the users, the task, and the platform.
3. Go through the task once to learn the flow. Do not judge anything on this pass.
4. Go through the task a second time. On each screen, check each heuristic and each directive.
5. Check the size and the position of each target, and the number of choices at each step.
6. Write each finding with the screen, the element, the heuristic or the directive, and the change that you recommend.
7. Give each finding its severity, then sort the findings from the highest severity.

## Output

A list of findings, sorted by severity. Each finding names the screen, the element, the heuristic or the directive that it breaks, its severity, and the change that you recommend. The severity scale is `0` for no problem, `1` for a cosmetic problem, `2` for a minor problem, `3` for a major problem, and `4` for a problem that blocks a release.

## Validation

Each finding names a directive from the first step of the procedure or one of the ten heuristics. A finding with neither is an opinion, so label it as one. One reviewer gives a rough severity, so state that a second reviewer can change it.

## References

- You judge the size or the position of a target. Read [Fitts's law](../../references/fitts-law.md).
- You judge the number of choices in a menu or a step. Read [Hick's law](../../references/hicks-law.md).
- You judge how people move between the screens of the flow. Read [Navigation](../../references/navigation.md).
- The flow runs on a platform with its own conventions. Read [Platform conventions](../../references/platform-conventions.md).
- You judge the feedback, the exits, the confirmations, the error messages, or the help of the flow. Read [Usability heuristics](../../references/usability-heuristics.md).
