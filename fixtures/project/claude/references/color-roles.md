<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Color roles

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Accessibility](accessibility.md):

- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only

From [Brand design](brand-design.md):

- Take each color, typeface, and logo from the brand definition of the project. ^use-brand-definition
- Write each message to a user in the voice of the brand definition. ^write-in-brand-voice

From [Visual identity](visual-identity.md):

- Remove each variant of a color, a typeface, or a logo that the brand guidelines do not list. ^remove-unlisted-variants

From [Color roles](color-roles.md):

- Assign a role to each brand color, such as primary, secondary, tertiary, neutral, or error. ^assign-color-roles
- Give each brand color a value for each medium that the brand uses, such as HEX or CMYK. ^color-values-per-medium
- Give each container color role a content color role for the text and the icons on it. ^content-role-for-container
- Define a value for the light appearance and a value for the dark appearance for each color role. ^light-and-dark-role-values
- Do not give a palette color the name of a color role. ^palette-names-not-roles
- Define each color role as an alias of a palette color token. ^role-as-alias

## Definition

The job that each color does in a palette, apart from its value. Material Design names three groups of accent roles: primary, secondary, and tertiary. Each group has a role for the color, an "on" role for the text and the icons on that color, and a container role for areas with less emphasis. Material adds error, surface, outline, and background roles that define the interface. A brand palette holds the named colors of the brand. A role points to one palette color, and it can point to another one in the dark appearance.

## Notes

Material names a custom color by what it is, such as `brand_blue`, and not by the slot that it fills, such as `color_primary`. A theme then maps each role to a palette color. The Design Tokens Format Module shows the same two levels in an example: a text color token whose value is an alias of a palette token. The rules for the token file itself are in the design tokens node.

GitHub builds its primary palette around one hero color and a set of neutrals, and gives each color as HEX, RGB, CMYK, and a Pantone number. A wider palette serves illustration. Material warns that a custom color for a role needs the same lightness as the default for that role, or text on it can lose its contrast. The contrast rules of the accessibility practice area set the limits.

## Comes from

The output of each node in this list is an input of this node.

- [Logo](brand-logo.md)

## Goes to

The output of this node is an input of each node in this list.

- [Type scale](type-scale.md)
