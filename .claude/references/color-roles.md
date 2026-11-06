<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Color roles

## Directives

No directive is in force at this node.

## Definition

The job that each color does in a palette, apart from its value. Material Design names three groups of accent roles: primary, secondary, and tertiary. Each group has a role for the color, an "on" role for the text and the icons on that color, and a container role for areas with less emphasis. Material adds error, surface, outline, and background roles that define the interface. A brand palette holds the named colors of the brand. A role points to one palette color, and it can point to another one in the dark appearance.

## Notes

Material names a custom color by what it is, such as `brand_blue`, and not by the slot that it fills, such as `color_primary`. A theme then maps each role to a palette color. The Design Tokens Format Module shows the same two levels in an example: a text color token whose value is an alias of a palette token. The rules for the token file itself are in the design tokens node.

GitHub builds its primary palette around one hero color and a set of neutrals, and gives each color as HEX, RGB, CMYK, and a Pantone number. A wider palette serves illustration. Material warns that a custom color for a role needs the same lightness as the default for that role, or text on it can lose its contrast. The contrast rules of the accessibility practice area set the limits.
