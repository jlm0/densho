---
name: design-interface
description: "Create or change a user interface, from its information architecture to its design system. Use when you create or change a user interface."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Design a user interface

If compaction cuts this skill, invoke the skill again.

## Directives

From [Accessibility](../../references/accessibility.md):

- Run each single-pointer action on the up event, not on the down event. ^act-on-pointer-up
- Give the user a way to disable, change, or extend each time limit, unless the limit exceeds `20` hours. ^adjustable-time-limits
- Do not block paste or password autofill in a login field. ^allow-paste-in-login
- Keep each text visible when a user raises its line, paragraph, letter, or word spacing. ^allow-text-spacing
- Give each prerecorded silent video a text alternative or an audio track, unless it is a labeled alternative for text. ^alternative-for-silent-video
- Give a way to bypass each block of content that repeats across pages. ^bypass-repeated-blocks
- Give captions to each live video with sound. ^caption-live-video
- Give captions to each prerecorded video with sound, unless the video is a labeled alternative for text. ^caption-prerecorded-video
- Give each single-character keyboard shortcut a setting to disable it or change its key, unless it works only on focus. ^character-key-shortcuts
- Keep each repeated help mechanism, such as contact details or a chat, in the same relative order on each page. ^consistent-help-order
- Give components with the same function the same label and the same glyph on each page. ^consistent-identification
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components
- Declare the purpose of each field that collects data about the user, such as with `autocomplete`. ^declare-input-purpose
- Declare the main language of each page in the code. ^declare-page-language
- Declare the language of each passage in another language, unless it is a name or a technical term. ^declare-passage-language
- When a check finds an input error, describe the error and its field in text. ^describe-input-error
- Give each prerecorded video an audio description of the visual content that its soundtrack does not state. ^describe-prerecorded-video
- Make each heading and label state the topic or the purpose of its content. ^descriptive-headings-and-labels
- Give each page a title that states its topic or purpose. ^descriptive-page-title
- Make content that appears on hover or focus dismissible without moving the pointer or the focus. ^dismissible-hover-content
- Give each drag action a single-pointer alternative that needs no drag, unless dragging is essential. ^drag-alternative
- Expose each status message to assistive technology without moving the focus to it. ^expose-status-messages
- Do not hide the focused control completely behind a sticky header, a banner, or another element. ^focus-not-obscured
- Hide each decorative image from assistive technology. ^hide-decoration
- Keep content that appears on hover visible while the pointer moves over that content. ^hoverable-content
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
- Give each input field a label or an instruction. ^label-each-field
- Include the visible label text of each control in its accessible name. ^label-in-name
- State the purpose of each link in its text or in the sentence that holds it. ^link-purpose
- Set a focus order that keeps the meaning and the operation of the content. ^logical-focus-order
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
- Give each action that a device motion starts an on-screen control and a setting that disables the motion. ^motion-alternative
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
- Expose the name, the role, and the state of each custom control to assistive technology. ^name-role-value
- Do not change the context when a control receives focus. ^no-change-on-focus
- Do not change the context when a user changes a setting, unless the control warns of it first. ^no-change-on-input
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Do not show content that flashes more than `3` times in any `1` second. ^no-flashing-content
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap
- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock
- Do not require a puzzle or a memory test for authentication, unless another method needs neither. ^no-puzzle-login
- Do not ask a user to type again a value that they entered earlier in the same process. ^no-redundant-entry
- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions
- Give a control to pause or hide each automatic update that runs in parallel with other content. ^pause-auto-updates
- Give a pause control to each audio that plays automatically for more than `3` seconds. ^pause-autoplay-audio
- Give a pause control to each moving or blinking content that starts automatically and lasts over `5` seconds. ^pause-moving-content
- Keep hover and focus content visible until the hover or the focus ends, or the user dismisses it. ^persistent-hover-content
- Keep the order of the content in the code the same as its visual reading order. ^reading-order-in-code
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Give a review step before each payment, each legal agreement, and each deletion of user data, unless it is reversible. ^review-before-commitment
- Give each action that a multipoint or path-based gesture does a single-pointer alternative, unless the gesture is essential. ^single-pointer-alternative
- Use the element or role that matches the visual structure of each heading, list, table, and form label. ^structure-in-code
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Give each meaningful image a text alternative. ^text-alternative
- Give each prerecorded audio-only clip a transcript, unless the clip is a labeled alternative for text. ^transcript-for-audio-only
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page

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

From [Platform conventions](../../references/platform-conventions.md):

- Follow the conventions of the target platform for each standard control, gesture, and layout. ^follow-platform-conventions
- Give each destination in a tab bar or a navigation bar a text label. ^label-each-tab
- Use the standard glyph of the platform for each standard action, such as share or delete. ^platform-glyphs
- Use a tab bar or a navigation bar only for navigation, not for actions. ^tabs-for-navigation

From [Apple Human Interface Guidelines](../../references/apple-human-interface-guidelines.md):

- In an `iOS` app, use an action sheet, not an alert, for choices of an action that the user started. ^apple-action-sheet-for-choices
- Check each screen for legibility in both the light and the dark appearance. ^apple-both-appearances
- Give each alert that offers a destructive action a `Cancel` button. ^apple-cancel-with-destructive
- In an `iOS` or `iPadOS` app, use `17` points as the default size of body text. ^apple-default-body-size
- Make each layout adapt to each Dynamic Type size. ^apple-dynamic-type
- In a `macOS` app, add an ellipsis to the title of each button that opens another window or view. ^apple-ellipsis-for-more-input
- In an `iOS` or `iPadOS` app, give each button a hit region of at least `44` by `44` points. ^apple-hit-region
- Keep each tab bar item visible and enabled, even when its content is not available. ^apple-keep-tabs-enabled
- In an `iOS` or `iPadOS` app, do not set text below `11` points. ^apple-minimum-text-size
- Do not add an appearance setting that overrides the system light or dark mode. ^apple-no-appearance-setting
- Do not use an alert only to give information that needs no action. ^apple-no-information-alert
- Do not show an alert when the app starts. ^apple-no-launch-alert
- Do not open a modal view over another modal view. ^apple-one-modal-at-a-time
- Keep each control and each piece of primary content inside the safe area. ^apple-safe-area
- Increase the size of each meaningful icon when the text size increases. ^apple-scale-icons-with-text
- Do not give a system color a new meaning. ^apple-system-color-meaning
- Do not copy the value of a system color into the code. ^apple-system-color-values

From [Material Design](../../references/material-design.md):

- Do not set body text on Android below `12` sp. ^android-minimum-body-size
- Test each Android layout at the compact, medium, and expanded window width classes. ^android-test-size-classes
- Set each font size on Android in `sp`. ^android-text-in-sp
- Make each touch target on Android at least `48` by `48` dp, even when it extends past the visible element. ^android-touch-target
- Give a navigation bar `3` to `5` destinations. ^navigation-bar-destinations

From [Information architecture](../../references/information-architecture.md):

- Define a controlled vocabulary for the content of each product. ^define-controlled-vocabulary

From [Interaction design](../../references/interaction-design.md):

- Show the result of each user action on the screen. ^show-action-result
- Show the current value of each setting next to its name. ^show-current-setting-value
- Give each custom button a visible pressed state. ^show-pressed-state

From [Visual design](../../references/visual-design.md):

- Limit each interface to `2` primary colors and `2` secondary colors. ^limit-color-palette

From [Design systems](../../references/design-systems.md):

- Use a design token, not a raw value, for each color, size, and space in a component. ^use-tokens-not-values

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.

## Steps

Run the steps in this order:

1. [Information architecture](steps/information-architecture.md)
2. [Interaction design](steps/interaction-design.md)
3. [Visual design](steps/visual-design.md)
4. [Design systems](steps/design-systems.md)

For each step:

1. Read its step file and each required read in it.
2. If the output of the step exists already, go to the next step.
3. Run the procedure of the step.
4. Go to the next step only after the exit gate of the step passes.
