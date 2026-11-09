<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Lay out and style each screen

This file is step 4 of 5 of the skill `design-interface`.

## Pages

- You rank the elements of a screen. Read [Information hierarchy](../../../references/information-hierarchy.md).
- You place, style, or frame related elements on a screen. Read [Visual grouping](../../../references/visual-grouping.md).
- You choose between prose and a visual form. Read [Visual communication](../../../references/visual-communication.md).
- You design or apply a logo, a brand color, or a type style. Read [Visual identity](../../../references/visual-identity.md).
- You choose the typefaces, the text sizes, or the text styles of a brand. Read [Type scale](../../../references/type-scale.md).
- You fit a layout to a screen size. Read [Responsive design](../../../references/responsive-design.md).
- You build a control, a form, a text style, a color choice, or media. Read [Accessibility](../../../references/accessibility.md).

## Directives

- Give each screen one primary action, unless the screen is a settings screen. ^one-primary-action
- Make the most important element on each screen the biggest element. ^make-most-important-biggest
- Limit each screen to `2` elements at the largest size. ^limit-largest-elements
- Limit the text on each screen to `3` sizes. ^limit-text-sizes
- Limit each screen to `3` contrast levels. ^limit-contrast-levels
- Use a bright color only for the primary action or the primary content of a screen. ^reserve-bright-color
- Do not give a secondary button the color of the primary button. ^distinct-primary-button-color
- Mark the preferred button in a set of choices with a prominent style, not a larger size. ^mark-preferred-with-style
- Limit each interface to `2` primary colors and `2` secondary colors. ^limit-color-palette
- Take each text size in a design from the type scale. ^sizes-from-the-scale
- Place related elements closer to each other than to other elements. ^place-related-elements-close
- Do not group unrelated controls. ^no-unrelated-group
- Place each heading closer to the text below it than to the text above it. ^heading-near-its-section
- Separate two groups with whitespace, not with a divider line, unless the space between them is fixed. ^prefer-space-over-divider
- If the space between two groups is fixed, put each group inside a border or a background. ^boundary-for-fixed-space
- Give elements with the same function the same visual style. ^same-style-same-function
- Give each text link in an interface the same color. ^one-link-color
- Do not give text that is not a link the color of the links. ^no-link-color-on-plain-text
- Do not give a decorative element the color or the shape of a control. ^no-decoration-like-control
- Add a visible text label to each glyph, unless the glyph means home, print, or search. ^label-glyphs
- Do not hide a glyph label behind a hover. ^no-hover-labels
- Do not use one glyph for two different functions. ^no-shared-glyph
- Use the standard glyph of the platform for each standard action, such as share or delete. ^platform-glyphs
- If a glyph, an image, or a grouping states the same information as a sentence, replace the sentence with it. ^prefer-visual-form
- Do not add a sentence that repeats what a heading, a label, or a value states. ^no-repeated-text
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components
- Give each graphic part that carries meaning at least `3:1` contrast against the colors next to it. ^contrast-graphics
- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Keep the keyboard focus indicator visible on each control. ^keep-focus-visible
- Use text, not an image of text, to show words, unless the words are part of a logo. ^no-images-of-text
- Keep the content and the controls usable at a text size of `200` percent. ^resize-text
- Build each base layout as a single column. ^single-column-base
- Choose each layout from the width of the window, not from the type of device. ^layout-from-window-width
- Show content at a width of `320` CSS pixels with no horizontal scroll, unless the content needs a two-dimensional layout. ^reflow-at-narrow-width
- Keep the related elements of each group close together at each breakpoint. ^keep-groups-at-each-width

## Branches

If a heading matches the work, follow each directive under it.

### If the screen holds a form

- Group the related fields of each form. ^group-related-fields
- Place each label closer to its field than to any other field. ^place-label-near-field

### If the screen is a settings screen

- If a screen is a settings screen, give each control on it the same rank. ^settings-controls-same-rank

### If the screen holds a grid of items, a carousel, tabs, or a sticky header

- Put the image, the title, and the details of each item in a grid inside one container. ^contain-item-parts
- Show part of the next item at the edge of each carousel. ^show-partial-next-item
- Show the selected tab and its panel inside one shared boundary. ^tab-joins-panel
- Give a sticky header a background or a border that separates it from the content under it. ^separate-sticky-header
- Do not hide the focused control completely behind a sticky header, a banner, or another element. ^focus-not-obscured

### If the design adds a new glyph

- Test each new glyph with users for recognition before you use it. ^test-new-glyphs

### If the screen shows an image

- Give each meaningful image a text alternative. ^text-alternative
- Hide each decorative image from assistive technology. ^hide-decoration

### If the screen shows video, audio, or content that moves, blinks, flashes, or updates by itself

- Give captions to each prerecorded video with sound, unless the video is a labeled alternative for text. ^caption-prerecorded-video
- Give captions to each live video with sound. ^caption-live-video
- Give each prerecorded video an audio description of the visual content that its soundtrack does not state. ^describe-prerecorded-video
- Give each prerecorded silent video a text alternative or an audio track, unless it is a labeled alternative for text. ^alternative-for-silent-video
- Give each prerecorded audio-only clip a transcript, unless the clip is a labeled alternative for text. ^transcript-for-audio-only
- Give a pause control to each audio that plays automatically for more than `3` seconds. ^pause-autoplay-audio
- Give a pause control to each moving or blinking content that starts automatically and lasts over `5` seconds. ^pause-moving-content
- Give a control to pause or hide each automatic update that runs in parallel with other content. ^pause-auto-updates
- Do not show content that flashes more than `3` times in any `1` second. ^no-flashing-content

### If the product runs on a phone or a tablet

- Do not lock content to portrait or landscape, unless the task needs one orientation. ^no-orientation-lock

### If the target is an Apple device

- Keep each control and each piece of primary content inside the safe area. ^apple-safe-area
- In an `iOS` or `iPadOS` app, use `17` points as the default size of body text. ^apple-default-body-size
- In an `iOS` or `iPadOS` app, do not set text below `11` points. ^apple-minimum-text-size
- Make each layout adapt to each Dynamic Type size. ^apple-dynamic-type
- Increase the size of each meaningful icon when the text size increases. ^apple-scale-icons-with-text
- Check each screen for legibility in both the light and the dark appearance. ^apple-both-appearances
- Do not add an appearance setting that overrides the system light or dark mode. ^apple-no-appearance-setting
- Do not give a system color a new meaning. ^apple-system-color-meaning

### If the target is Android

- Do not set body text on Android below `12` sp. ^android-minimum-body-size
- Set each font size on Android in `sp`. ^android-text-in-sp
- Test each Android layout at the compact, medium, and expanded window width classes. ^android-test-size-classes

## Next step

Return to step 5 of [the skill](../SKILL.md).
