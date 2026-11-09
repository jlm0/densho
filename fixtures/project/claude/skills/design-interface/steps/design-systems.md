<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Specify the components and the tokens

This file is step 5 of 5 of the skill `design-interface`.

## Pages

- You build or use the tokens and the components of a design system. Read [Design systems](../../../references/design-systems.md).
- You build, combine, or test the components of a design system. Read [Atomic design](../../../references/atomic-design.md).
- You name, store, or reference a color, a size, a space, or a type style. Read [Design tokens](../../../references/design-tokens.md).
- You build a control, a form, a text style, a color choice, or media. Read [Accessibility](../../../references/accessibility.md).

## Directives

- Use a design token, not a raw value, for each color, size, and space in a component. ^use-tokens-not-values
- Build each new organism from the atoms and molecules that the system holds. ^compose-from-the-system
- Give each molecule one job. ^one-job-per-molecule
- State the image sizes and the text lengths that each template accepts. ^state-content-limits
- Test each template with real, representative content. ^test-with-real-content
- Test each template with its shortest and its longest real content. ^test-content-extremes
- Give each non-text control a name that describes its purpose. ^name-non-text-controls
- Expose the name, the role, and the state of each custom control to assistive technology. ^name-role-value

## Branches

If a heading matches the work, follow each directive under it.

### If you add or change a token file

- Give each design token a `$value`. ^token-value
- Declare a `$type` on each design token or on a group above it. ^token-type
- Write each reference to another token as its path in curly braces, such as `{color.text.base}`. ^alias-in-braces
- Do not make a chain of token references that leads back to its start. ^no-circular-alias
- Do not give a `$value` to an object that holds tokens or groups. ^no-value-on-group
- Do not start the name of a token or a group with `$`. ^no-dollar-token-name
- Do not put `{`, `}`, or `.` in the name of a token or a group. ^no-reserved-token-characters
- Do not give two tokens in one group names that differ only in case. ^no-case-only-token-names
- Mark each token that you plan to remove with `$deprecated`. ^deprecate-tokens
- Do not put data in `$extensions` that the meaning of a token value depends on. ^no-required-extension-data
- Put the data of each tool in `$extensions` under a key in reverse domain notation. ^vendor-key-extensions
- Name each design token file with the extension `.tokens` or `.tokens.json`. ^tokens-file-extension

### If the target is an Apple device

- Do not copy the value of a system color into the code. ^apple-system-color-values

## Next step

Return to the exit checklist of [the skill](../SKILL.md).
