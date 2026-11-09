<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Write the brand guidelines

This file is step 3 of 3 of the skill `design-brand`.

## Pages

- You write brand guidelines, store brand values as tokens, or relate the brands of a company. Read [Brand systems](../../../references/brand-systems.md).
- You write, structure, or publish the brand guidelines. Read [Brand guidelines](../../../references/brand-guidelines.md).
- You name a new product, a sub-brand, or an acquired company. Read [Brand architecture](../../../references/brand-architecture.md).
- You name, store, or reference a color, a size, a space, or a type style. Read [Design tokens](../../../references/design-tokens.md).

## Directives

- Label each element of the brand guidelines as `sacred`, `interpretive`, or `customizable`. ^label-element-freedom
- Label an element of the brand guidelines `sacred` if the guidelines allow no change to it. ^sacred-element
- Label an element of the brand guidelines `interpretive` if the guidelines allow a change to it within a stated range. ^interpretive-element
- Label an element of the brand guidelines `customizable` if the guidelines allow each team to change it. ^customizable-element
- Show each logo rule with a correct example and an incorrect example. ^do-and-dont-examples
- Write a section of the brand guidelines for each group of users, such as designers, writers, and partners. ^guidelines-per-audience
- Publish the brand guidelines and the asset files in one online source. ^one-online-source
- Store the colors and the typography of the brand as a set of design tokens, the brand theme. ^brand-values-as-tokens
- Define each color role as an alias of a palette color token. ^role-as-alias

## Branches

If a heading matches the work, follow each directive under it.

### If the company has more than one brand

- State the brand architecture type of each product: monolithic, endorsed, or pluralistic. ^state-architecture-type
- In a monolithic brand architecture, name each product with the parent brand and a generic descriptor. ^monolithic-descriptors

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

## Next step

Return to the exit checklist of [the skill](../SKILL.md).
