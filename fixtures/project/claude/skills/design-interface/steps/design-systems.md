<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Design systems

This file is step 4 of 4 of the skill `design-interface`.

## Directives

From [Atomic design](../../../references/atomic-design.md):

- Build each new organism from the atoms and molecules that the system holds. ^compose-from-the-system
- Give each molecule one job. ^one-job-per-molecule
- State the image sizes and the text lengths that each template accepts. ^state-content-limits
- Test each template with its shortest and its longest real content. ^test-content-extremes
- Test each template with real, representative content. ^test-with-real-content

From [Design tokens](../../../references/design-tokens.md):

- Write each reference to another token as its path in curly braces, such as `{color.text.base}`. ^alias-in-braces
- Mark each token that you plan to remove with `$deprecated`. ^deprecate-tokens
- Do not give two tokens in one group names that differ only in case. ^no-case-only-token-names
- Do not make a chain of token references that leads back to its start. ^no-circular-alias
- Do not start the name of a token or a group with `$`. ^no-dollar-token-name
- Do not put data in `$extensions` that the meaning of a token value depends on. ^no-required-extension-data
- Do not put `{`, `}`, or `.` in the name of a token or a group. ^no-reserved-token-characters
- Do not give a `$value` to an object that holds tokens or groups. ^no-value-on-group
- Declare a `$type` on each design token or on a group above it. ^token-type
- Give each design token a `$value`. ^token-value
- Name each design token file with the extension `.tokens` or `.tokens.json`. ^tokens-file-extension
- Put the data of each tool in `$extensions` under a key in reverse domain notation. ^vendor-key-extensions

## Inputs

- The screens of the visual design
- The design tokens and the components that the product has

The output of each node in this list is an input of this step:

- [Visual design](visual-design.md)
- [Visual identity](../../../references/visual-identity.md)

## Procedure

The procedure of this step is missing.

## Output

The design tokens and the components that the screens use, with the rules for their use.

The output of this step is an input of each node in this list:

- [Software design](../../../references/software-design.md)

## Exit gate

Check the tokens and the components against each directive of this step and of the skill, and report each one that it misses.

## Next step

This step is the last step of the skill.

## References

- You build, combine, or test the components of a design system. Read [Atomic design](../../../references/atomic-design.md).
- You name, store, or reference a color, a size, a space, or a type style. Read [Design tokens](../../../references/design-tokens.md).
