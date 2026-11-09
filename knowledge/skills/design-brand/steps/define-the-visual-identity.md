---
title: Define the visual identity
pages:
  - target: visual-identity
    trigger: You design or apply a logo, a brand color, or a type style.
  - target: brand-logo
    trigger: You design, place, or specify a logo or a lockup.
  - target: color-roles
    trigger: You define the colors of a brand or assign them to roles.
  - target: type-scale
    trigger: You choose the typefaces, the text sizes, or the text styles of a brand.
  - target: distinctive-brand-assets
    trigger: You choose, measure, or replace a color, a shape, a character, or a sound that signals the brand.
  - target: accessibility
    trigger: You check the contrast of a pair of brand colors.
directives:
  - uniqueness-before-fame
  - no-famous-shared-elements
  - name-each-lockup
  - logo-clear-space
  - logo-minimum-size
  - logo-color-versions
  - nothing-in-clear-space
  - no-logo-effects
  - keep-logo-proportions
  - no-busy-logo-background
  - assign-color-roles
  - content-role-for-container
  - light-and-dark-role-values
  - color-values-per-medium
  - palette-names-not-roles
  - contrast-regular-text
  - contrast-large-text
  - contrast-ui-components
  - scale-from-body-size
  - record-the-scale
  - text-style-values
  - text-style-roles
  - sizes-from-the-scale
branches:
  - condition: If the brand has a logo, a color, or a typeface in use
    directives:
      - measure-asset-strength
      - measure-before-replacing
      - remove-unlisted-variants
missing_rules:
  - No directive covers the style of the photos, the illustrations, and the icons of the brand.
---

## Procedure

1. If step `1` lists no section that this step writes, skip this step.
2. Collect the current brand assets: the logo files, the colors, the typefaces, and samples of their use.
3. Write the logo section: each lockup, the clear space, the minimum sizes, the color versions, and the misuse examples.
4. Write the palette of the color section, with the values for each medium.
5. Assign a role to each color, with a light value and a dark value.
6. Check the contrast of each pair of a container role and its content role.
7. Write the typography section: the typefaces, the type scale with its base and its ratio, and the text styles.

## Output

The logo section, the color section, and the typography section of the brand guidelines.
