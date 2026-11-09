---
name: review-screen-hierarchy
description: "Review a screen for its hierarchy, its grouping, and its use of prose. Use when a person asks for a review of the hierarchy of a screen. Do not use it for a whole interface (`review-interface`) or a flow (`review-usability`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review the hierarchy of a screen

## Run the skill

1. Check the work against each directive of the skill.
2. If a branch heading matches the work, check the work against each directive under it.
3. If you need the definition or the notes of a page, read the page.

## Review the screen

1. Collect the screen, as a design or a running interface, and the task that a person does on it.
2. Name the element that a viewer sees first, then second, then third.
3. Compare that order with the order of importance for the task.
4. Mark each group that the spacing shows.
5. Compare the marked groups with the groups that the task needs.
6. Mark each sentence and label that a glyph, an image, or a grouping replaces.
7. Write each finding with the element, the directive that it breaks, and the change that you recommend.

Pages:

- You judge which element a viewer sees first. Read [Information hierarchy](../../references/information-hierarchy.md).
- You judge which elements read as one group. Read [Visual grouping](../../references/visual-grouping.md).
- You find prose that a visual form replaces. Read [Visual communication](../../references/visual-communication.md).

Directives:

- Give each screen one primary action, unless the screen is a settings screen. ^one-primary-action
- Make the most important element on each screen the biggest element. ^make-most-important-biggest
- Limit each screen to `2` elements at the largest size. ^limit-largest-elements
- Limit the text on each screen to `3` sizes. ^limit-text-sizes
- Limit each screen to `3` contrast levels. ^limit-contrast-levels
- Use a bright color only for the primary action or the primary content of a screen. ^reserve-bright-color
- Do not give a secondary button the color of the primary button. ^distinct-primary-button-color
- Mark the preferred button in a set of choices with a prominent style, not a larger size. ^mark-preferred-with-style
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

### If the design adds a new glyph

- Test each new glyph with users for recognition before you use it. ^test-new-glyphs

Output: A list of findings for the screen.

## Exit checklist

- [ ] Each finding names a directive of this skill, or a label marks it as an opinion.

## Output

A list of findings. Each finding names the element, the directive that it breaks, and the change that you recommend.
