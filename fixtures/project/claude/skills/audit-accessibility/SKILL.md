---
name: audit-accessibility
description: "Check an interface against the WCAG `2.2` success criteria of level A and AA. Use when a person asks for an accessibility check of an interface. Do not use it for a whole interface review (`review-interface`) or a code change (`review-code-change`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Audit the accessibility of an interface

## Run the skill

1. Check the work against each directive of the skill.
2. If a branch heading matches the work, check the work against each directive under it.
3. If you need the definition or the notes of a page, read the page.

## Audit the interface

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

Pages:

- You check the interface against a success criterion or its exception. Read [Accessibility](../../references/accessibility.md).

Directives:

- State the conformance level and the screens that the audit covers. ^state-the-audit-scope
- Check each screen of a complete process, not only its first screen. ^audit-complete-processes
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Make each function operable through a keyboard, unless the function depends on the path of the pointer. ^keyboard-operable
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
- Give each pointer target a size of at least `24` by `24` CSS pixels, unless a sentence holds the target. ^minimum-target-size
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
- Use the element or role that matches the visual structure of each heading, list, table, and form label. ^structure-in-code
- Keep the order of the content in the code the same as its visual reading order. ^reading-order-in-code
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Keep each text visible when a user raises its line, paragraph, letter, or word spacing. ^allow-text-spacing
- Give a way to bypass each block of content that repeats across pages. ^bypass-repeated-blocks
- Give each page a title that states its topic or purpose. ^descriptive-page-title
- Set a focus order that keeps the meaning and the operation of the content. ^logical-focus-order
- State the purpose of each link in its text or in the sentence that holds it. ^link-purpose
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page
- Make each heading and label state the topic or the purpose of its content. ^descriptive-headings-and-labels
- Run each single-pointer action on the up event, not on the down event. ^act-on-pointer-up
- Include the visible label text of each control in its accessible name. ^label-in-name
- Declare the main language of each page in the code. ^declare-page-language
- Declare the language of each passage in another language, unless it is a name or a technical term. ^declare-passage-language
- Do not change the context when a control receives focus. ^no-change-on-focus
- Do not change the context when a user changes a setting, unless the control warns of it first. ^no-change-on-input
- Give components with the same function the same label and the same glyph on each page. ^consistent-identification
- Expose the name, the role, and the state of each custom control to assistive technology. ^name-role-value
- Expose each status message to assistive technology without moving the focus to it. ^expose-status-messages
- Keep repeated navigation elements in the same relative order on each screen. ^keep-navigation-order

### If the interface holds a form

- Give each input field a label or an instruction. ^label-each-field
- Declare the purpose of each field that collects data about the user, such as with `autocomplete`. ^declare-input-purpose
- When a check finds an input error, describe the error and its field in text. ^describe-input-error
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Give a review step before each payment, each legal agreement, and each deletion of user data, unless it is reversible. ^review-before-commitment
- Do not ask a user to type again a value that they entered earlier in the same process. ^no-redundant-entry

### If the interface holds a login

- Do not block paste or password autofill in a login field. ^allow-paste-in-login
- Do not require a puzzle or a memory test for authentication, unless another method needs neither. ^no-puzzle-login

### If the interface opens a dialog or an overlay

- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap

### If the interface holds help or an instruction

- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions
- Keep each repeated help mechanism, such as contact details or a chat, in the same relative order on each page. ^consistent-help-order

### If the interface uses a gesture, a drag, a device motion, or a single-key shortcut

- Give each single-character keyboard shortcut a setting to disable it or change its key, unless it works only on focus. ^character-key-shortcuts
- Give each action that a multipoint or path-based gesture does a single-pointer alternative, unless the gesture is essential. ^single-pointer-alternative
- Give each action that a device motion starts an on-screen control and a setting that disables the motion. ^motion-alternative
- Give each drag action a single-pointer alternative that needs no drag, unless dragging is essential. ^drag-alternative

### If the interface sets a time limit

- Give the user a way to disable, change, or extend each time limit, unless the limit exceeds `20` hours. ^adjustable-time-limits

### If content shows on hover or focus

- Make content that appears on hover or focus dismissible without moving the pointer or the focus. ^dismissible-hover-content
- Keep content that appears on hover visible while the pointer moves over that content. ^hoverable-content
- Keep hover and focus content visible until the hover or the focus ends, or the user dismisses it. ^persistent-hover-content

### If the interface holds a sticky header, a banner, or another fixed element

- Do not hide the focused control completely behind a sticky header, a banner, or another element. ^focus-not-obscured

### If the interface shows an image

- Give each meaningful image a text alternative. ^text-alternative
- Hide each decorative image from assistive technology. ^hide-decoration

### If the interface shows video, audio, or content that moves, blinks, flashes, or updates by itself

- Give each prerecorded audio-only clip a transcript, unless the clip is a labeled alternative for text. ^transcript-for-audio-only
- Give each prerecorded silent video a text alternative or an audio track, unless it is a labeled alternative for text. ^alternative-for-silent-video
- Give captions to each prerecorded video with sound, unless the video is a labeled alternative for text. ^caption-prerecorded-video
- Give each prerecorded video an audio description of the visual content that its soundtrack does not state. ^describe-prerecorded-video
- Give captions to each live video with sound. ^caption-live-video
- Give a pause control to each audio that plays automatically for more than `3` seconds. ^pause-autoplay-audio
- Give a pause control to each moving or blinking content that starts automatically and lasts over `5` seconds. ^pause-moving-content
- Give a control to pause or hide each automatic update that runs in parallel with other content. ^pause-auto-updates
- Do not show content that flashes more than `3` times in any `1` second. ^no-flashing-content

### If the product runs on a phone or a tablet

- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock

Output: A list of failures, and a list of the directives with no content to check.

## Exit checklist

- [ ] Each failure names a directive of this skill.
- [ ] If the audit reads a design file, the report names each check that needs the running code.

## Output

A list of failures, and a list of the directives with no content to check. Each failure names the screen, the element, the directive that it breaks, and the change that you recommend. A design file does not show the checks of the code, such as names, roles, and the language of the page.
