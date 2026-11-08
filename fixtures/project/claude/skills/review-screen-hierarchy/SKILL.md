---
name: review-screen-hierarchy
description: "Review a screen for its hierarchy, its grouping, and its use of prose. Use when a person asks for a review of the hierarchy of a screen."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review the hierarchy of a screen

If compaction cuts this skill, invoke the skill again.

## Directives

From [Accessibility](../../references/accessibility.md):

- Run each single-pointer action on the up event, not on the down event. ^act-on-pointer-up
- Keep each text visible when a user raises its line, paragraph, letter, or word spacing. ^allow-text-spacing
- Give a way to bypass each block of content that repeats across pages. ^bypass-repeated-blocks
- Give components with the same function the same label and the same glyph on each page. ^consistent-identification
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
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Do not lock the keyboard focus in a component, unless the component states the key that exits it. ^no-keyboard-trap
- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock
- Do not name a control only by its shape, color, size, position, or sound in an instruction. ^no-sensory-only-instructions
- Keep the order of the content in the code the same as its visual reading order. ^reading-order-in-code
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Use the element or role that matches the visual structure of each heading, list, table, and form label. ^structure-in-code
- When a check finds an input error with a known fix, state the fix, unless it weakens security. ^suggest-error-fix
- Give each meaningful image a text alternative. ^text-alternative
- Give `2` or more ways to reach each page, unless the page is a step in a process. ^two-ways-to-each-page
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only

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

From [Visual design](../../references/visual-design.md):

- Limit each interface to `2` primary colors and `2` secondary colors. ^limit-color-palette

From [Visual grouping](../../references/visual-grouping.md):

- If the space between two groups is fixed, put each group inside a border or a background. ^boundary-for-fixed-space
- Put the image, the title, and the details of each item in a grid inside one container. ^contain-item-parts
- Group the related fields of each form. ^group-related-fields
- Place each heading closer to the text below it than to the text above it. ^heading-near-its-section
- Do not give a decorative element the color or the shape of a control. ^no-decoration-like-control
- Do not give text that is not a link the color of the links. ^no-link-color-on-plain-text
- Do not group unrelated controls. ^no-unrelated-group
- Give each text link in an interface the same color. ^one-link-color
- Place each label closer to its field than to any other field. ^place-label-near-field
- Place related elements closer to each other than to other elements. ^place-related-elements-close
- Separate two groups with whitespace, not with a divider line, unless the space between them is fixed. ^prefer-space-over-divider
- Give elements with the same function the same visual style. ^same-style-same-function
- Give a sticky header a background or a border that separates it from the content under it. ^separate-sticky-header
- Show part of the next item at the edge of each carousel. ^show-partial-next-item
- Show the selected tab and its panel inside one shared boundary. ^tab-joins-panel

From [Information hierarchy](../../references/information-hierarchy.md):

- Do not give a secondary button the color of the primary button. ^distinct-primary-button-color
- Limit each screen to `3` contrast levels. ^limit-contrast-levels
- Limit each screen to `2` elements at the largest size. ^limit-largest-elements
- Limit the text on each screen to `3` sizes. ^limit-text-sizes
- Make the most important element on each screen the biggest element. ^make-most-important-biggest
- Mark the preferred button in a set of choices with a prominent style, not a larger size. ^mark-preferred-with-style
- Give each screen one primary action, unless the screen is a settings screen. ^one-primary-action
- Use a bright color only for the primary action or the primary content of a screen. ^reserve-bright-color
- If a screen is a settings screen, give each control on it the same rank. ^settings-controls-same-rank

From [Visual communication](../../references/visual-communication.md):

- Add a visible text label to each glyph, unless the glyph means home, print, or search. ^label-glyphs
- Do not hide a glyph label behind a hover. ^no-hover-labels
- Do not use one glyph for two different functions. ^no-shared-glyph
- If a glyph, an image, or a grouping states the same information as a sentence, replace the sentence with it. ^prefer-visual-form
- Test each new glyph with users for recognition before you use it. ^test-new-glyphs

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.

## Inputs

- The screen, as a design or a running interface
- The task that a person does on the screen

## Procedure

1. Read each directive that this skill lists.
2. Name the element that a viewer sees first, then second, then third.
3. Compare that order with the order of importance for the task.
4. Mark each group that the spacing shows, and compare it with the groups that the task needs.
5. Mark each sentence and label that a glyph, an image, or a grouping replaces.

## Output

A list of findings. Each finding names the element, the directive that it breaks, and the change that you recommend.

## Validation

Each finding names a directive from the first step of the procedure. A finding with no directive is an opinion, so label it as one.

## References

- You judge which element a viewer sees first. Read [Information hierarchy](../../references/information-hierarchy.md).
- You find prose that a visual form replaces. Read [Visual communication](../../references/visual-communication.md).
- You judge which elements read as one group. Read [Visual grouping](../../references/visual-grouping.md).
