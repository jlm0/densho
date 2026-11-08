<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Visual design

This file is step 3 of 4 of the skill `design-interface`.

## Directives

From [Information hierarchy](../../../references/information-hierarchy.md):

- Do not give a secondary button the color of the primary button. ^distinct-primary-button-color
- Limit each screen to `3` contrast levels. ^limit-contrast-levels
- Limit each screen to `2` elements at the largest size. ^limit-largest-elements
- Limit the text on each screen to `3` sizes. ^limit-text-sizes
- Make the most important element on each screen the biggest element. ^make-most-important-biggest
- Mark the preferred button in a set of choices with a prominent style, not a larger size. ^mark-preferred-with-style
- Give each screen one primary action, unless the screen is a settings screen. ^one-primary-action
- Use a bright color only for the primary action or the primary content of a screen. ^reserve-bright-color
- If a screen is a settings screen, give each control on it the same rank. ^settings-controls-same-rank

From [Visual communication](../../../references/visual-communication.md):

- Add a visible text label to each glyph, unless the glyph means home, print, or search. ^label-glyphs
- Do not hide a glyph label behind a hover. ^no-hover-labels
- Do not use one glyph for two different functions. ^no-shared-glyph
- If a glyph, an image, or a grouping states the same information as a sentence, replace the sentence with it. ^prefer-visual-form
- Test each new glyph with users for recognition before you use it. ^test-new-glyphs

From [Visual grouping](../../../references/visual-grouping.md):

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

## Inputs

- The controls of each screen and their order
- The brand guidelines of the project

The output of each node in this list is an input of this step:

- [Interaction design](interaction-design.md)

## Procedure

1. Group the options on each screen, and name each group.
2. Apply the brand guidelines.
3. Check the layout at the narrowest screen width.

The rest of the procedure of this step is missing.

## Output

The layout, the type, the color, the imagery, and the spacing of each screen.

The output of this step is an input of each node in this list:

- [Design systems](design-systems.md)

## Exit gate

Check the screens against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Design systems](design-systems.md).

## References

- You rank the elements of a screen. Read [Information hierarchy](../../../references/information-hierarchy.md).
- You choose between prose and a visual form. Read [Visual communication](../../../references/visual-communication.md).
- You place, style, or frame related elements on a screen. Read [Visual grouping](../../../references/visual-grouping.md).
