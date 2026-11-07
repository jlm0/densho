---
id: color-roles
kind: densho:Concept
title: Color roles
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md
  - https://brand.github.com/foundations/color
  - https://www.designtokens.org/tr/2025.10/format/
broader:
  - visual-identity
related:
  - design-tokens
  - accessibility
---

## Definition

The job that each color does in a palette, apart from its value. Material Design names three groups of accent roles: primary, secondary, and tertiary. Each group has a role for the color, an "on" role for the text and the icons on that color, and a container role for areas with less emphasis. Material adds error, surface, outline, and background roles that define the interface. A brand palette holds the named colors of the brand. A role points to one palette color, and it can point to another one in the dark appearance.

## Directives

- Assign a role to each brand color, such as primary, secondary, tertiary, neutral, or error. ^assign-color-roles
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md
  - sources: https://brand.github.com/foundations/color
- Give each container color role a content color role for the text and the icons on it. ^content-role-for-container
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md
- Define a value for the light appearance and a value for the dark appearance for each color role. ^light-and-dark-role-values
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md
- Give each brand color a value for each medium that the brand uses, such as HEX or CMYK. ^color-values-per-medium
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://brand.github.com/foundations/color
- Do not give a palette color the name of a color role. ^palette-names-not-roles
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md
- Define each color role as an alias of a palette color token. ^role-as-alias
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md
  - sources: https://www.designtokens.org/tr/2025.10/format/

## Notes

Material names a custom color by what it is, such as `brand_blue`, and not by the slot that it fills, such as `color_primary`. A theme then maps each role to a palette color. The Design Tokens Format Module shows the same two levels in an example: a text color token whose value is an alias of a palette token. The rules for the token file itself are in the design tokens node.

GitHub builds its primary palette around one hero color and a set of neutrals, and gives each color as HEX, RGB, CMYK, and a Pantone number. A wider palette serves illustration. Material warns that a custom color for a role needs the same lightness as the default for that role, or text on it can lose its contrast. The contrast rules of the accessibility practice area set the limits.
