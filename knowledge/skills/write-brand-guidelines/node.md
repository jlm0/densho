---
id: write-brand-guidelines
kind: ka:Skill
title: Write brand guidelines
status: proposed
origin: template
knowledge_type: domain
description: Write the brand guidelines of a product or a company, from its strategy to its logo, colors, type, and voice. Use when you write or update brand guidelines.
invocation: agent
uses:
  - brand-strategy
  - brand-identity-prism
  - brand-positioning-statement
  - visual-identity
  - brand-logo
  - color-roles
  - type-scale
  - brand-voice
  - brand-systems
  - brand-guidelines
  - brand-architecture
applies:
  - contrast-regular-text
  - contrast-large-text
  - contrast-ui-components
pointers:
  - kind: ka:TextPointer
    target: brand-strategy
    trigger: You write the strategy section of the guidelines.
  - kind: ka:TextPointer
    target: brand-identity-prism
    trigger: You describe the identity of the brand in the guidelines.
  - kind: ka:TextPointer
    target: brand-positioning-statement
    trigger: You write the positioning statement of the brand.
  - kind: ka:TextPointer
    target: visual-identity
    trigger: You list the colors, the typefaces, and the logo variants that the brand allows.
  - kind: ka:TextPointer
    target: brand-logo
    trigger: You write the logo section of the guidelines.
  - kind: ka:TextPointer
    target: color-roles
    trigger: You write the color section of the guidelines.
  - kind: ka:TextPointer
    target: type-scale
    trigger: You write the typography section of the guidelines.
  - kind: ka:TextPointer
    target: brand-voice
    trigger: You write the voice and tone section of the guidelines.
  - kind: ka:TextPointer
    target: brand-systems
    trigger: You store the brand values as design tokens.
  - kind: ka:TextPointer
    target: brand-guidelines
    trigger: You structure or publish the guidelines.
  - kind: ka:TextPointer
    target: brand-architecture
    trigger: The company has more than one brand, product name, or sub-brand.
  - kind: ka:TextPointer
    target: accessibility
    trigger: You check the contrast of a pair of brand colors.
---

## Inputs

- The positioning of the product, with its positioning components
- The current brand assets: the logo files, the colors, the typefaces, and samples of their use
- The voice and tone guide, if the brand has one
- The design token files, if the design system has them
- The groups of people who apply the brand, inside and outside the company

## Procedure

1. Read each directive that this skill lists.
2. Write the strategy section: the six facets of the identity prism and the positioning statement. If the product has no positioning, run `write-positioning` first. If the company has more than one brand, state the architecture type of each product.
3. Write the logo section: each lockup, the clear space, the minimum sizes, the color versions, and the misuse examples.
4. Write the color section: the palette with the values for each medium, the role of each color, and the light and dark values of each role. Check the contrast of each pair of a container role and its content role.
5. Write the typography section: the typefaces, the type scale with its base and its ratio, and the text styles by role.
6. Add the voice and tone section from the voice and tone guide. If the brand has no guide, run `define-brand-voice` first.
7. Label each element as sacred, interpretive, or customizable, and add a correct and an incorrect example for each logo rule.
8. Store the colors, the typefaces, and the type scale as design tokens, and link the token files from the guidelines.
9. Give each group of people who apply the brand a section with the rules and the assets that it uses.

## Output

One set of brand guidelines in one online source, with the asset files beside it. The guidelines hold the strategy, the architecture where it applies, the logo, the colors, the typography, the voice and tone, and the label of each element. The token files hold each color, typeface, and text size that the guidelines state.

## Validation

Check the guidelines against each directive from the first step of the procedure, and report each one it misses. Each pair of brand colors for text or controls passes the contrast rules. Each value in the guidelines matches the value in the token files.
