<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Brand systems

This file is step 4 of 4 of the skill `design-brand`.

## Directives

From [Brand architecture](../../../references/brand-architecture.md):

- In a monolithic brand architecture, name each product with the parent brand and a generic descriptor. ^monolithic-descriptors
- State the brand architecture type of each product: monolithic, endorsed, or pluralistic. ^state-architecture-type

From [Brand guidelines](../../../references/brand-guidelines.md):

- Label an element of the brand guidelines `customizable` if the guidelines allow each team to change it. ^customizable-element
- Show each logo rule with a correct example and an incorrect example. ^do-and-dont-examples
- Write a section of the brand guidelines for each group of users, such as designers, writers, and partners. ^guidelines-per-audience
- Label an element of the brand guidelines `interpretive` if the guidelines allow a change to it within a stated range. ^interpretive-element
- Label each element of the brand guidelines as `sacred`, `interpretive`, or `customizable`. ^label-element-freedom
- Publish the brand guidelines and the asset files in one online source. ^one-online-source
- Label an element of the brand guidelines `sacred` if the guidelines allow no change to it. ^sacred-element

## Inputs

- The strategy, logo, color, and typography sections of the brand guidelines
- The voice and tone guide
- The products and the brands of the company
- The design token files, if the design system has them
- The groups of people who apply the brand, inside and outside the company

The output of each node in this list is an input of this step:

- [Visual identity](visual-identity.md)

## Procedure

1. If the company has more than one brand, state the architecture type of each product.
2. Add the voice and tone section from the voice and tone guide. If the brand has no guide, run the brand voice step first.
3. Label each element as sacred, interpretive, or customizable, and add a correct and an incorrect example for each logo rule.
4. Store the colors, the typefaces, and the type scale as design tokens, and link the token files from the guidelines.
5. Give each group of people who apply the brand a section with the rules and the assets that it uses.

## Output

One set of brand guidelines in one online source, with the asset files beside it. The guidelines hold the strategy, the architecture where it applies, the logo, the colors, the typography, the voice and tone, and the label of each element. The token files hold each color, typeface, and text size that the guidelines state.

## Exit gate

Check the guidelines against each directive of this step and of the skill, and report each one that it misses. Each value in the guidelines matches the value in the token files.

## Next step

This step is the last step of the skill.

## References

- You name a new product, a sub-brand, or an acquired company. Read [Brand architecture](../../../references/brand-architecture.md).
- You write, structure, or publish the brand guidelines. Read [Brand guidelines](../../../references/brand-guidelines.md).
