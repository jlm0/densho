---
name: write-brand-guidelines
description: "Write the brand guidelines of a product or a company, from its strategy to its logo, colors, type, and voice. Use when you write or update brand guidelines."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Write brand guidelines

If compaction cuts this skill, invoke the skill again.

## Directives

From [Digital product development](../../references/digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Accessibility](../../references/accessibility.md):

- Do not use color as the only visual mark of information, an action, or a state. ^no-color-only
- Give text of `18` points or more at least `3:1` contrast, unless a logo or inactive control holds it. ^contrast-large-text
- Give text under `18` points at least `4.5:1` contrast, unless a logo or inactive control holds it. ^contrast-regular-text
- Give the visual parts that identify a control and its state at least `3:1` contrast, unless the control is inactive. ^contrast-ui-components

From [Brand design](../../references/brand-design.md):

- Take each color, typeface, and logo from the brand definition of the project. ^use-brand-definition
- Write each message to a user in the voice of the brand definition. ^write-in-brand-voice

From [Color roles](../../references/color-roles.md):

- Assign a role to each brand color, such as primary, secondary, tertiary, neutral, or error. ^assign-color-roles
- Give each brand color a value for each medium that the brand uses, such as HEX or CMYK. ^color-values-per-medium
- Give each container color role a content color role for the text and the icons on it. ^content-role-for-container
- Define a value for the light appearance and a value for the dark appearance for each color role. ^light-and-dark-role-values
- Do not give a palette color the name of a color role. ^palette-names-not-roles
- Define each color role as an alias of a palette color token. ^role-as-alias

From [Brand systems](../../references/brand-systems.md):

- Store the brand colors, typefaces, and type scale in design token files. ^brand-values-as-tokens

From [Brand voice](../../references/brand-voice.md):

- Remove each joke that makes a message less clear. ^clarity-over-jokes
- Do not add a joke to an error message. ^no-joke-in-errors
- Write the tone guidance for each type of message, such as an error, a success, or an onboarding step. ^tone-by-message-type
- Match the tone of each message to the emotional state of the reader. ^tone-matches-reader
- For each voice trait, list the emotional states of the reader that increase the trait and that reduce it. ^trait-by-reader-state
- Name a trait to avoid for each voice trait, such as direct but not curt. ^trait-to-avoid
- Describe the brand voice in `3` or `4` traits. ^voice-trait-count

From [Brand positioning statement](../../references/brand-positioning-statement.md):

- If a positioning statement stays true with the name of a competitor in it, replace the point of difference. ^competitor-name-test
- Give each point of difference a reason to believe: an attribute of the product or an image of its users. ^give-a-reason-to-believe
- Name the points of parity that the brand shares with its frame of reference. ^name-points-of-parity
- Do not choose a reason to believe that weakens another claim of the statement. ^no-conflicting-reason
- Write each positioning statement with a target, a frame of reference, a point of difference, and a reason to believe. ^positioning-statement-parts
- Take the target, the frame of reference, and the point of difference from the positioning components of the product. ^statement-from-components
- Do not publish a positioning statement as copy for customers. ^statement-is-internal
- Test each positioning statement with people outside the company for clarity and belief. ^test-statement-outside

From [Brand identity prism](../../references/brand-identity-prism.md):

- Describe each of the six facets of the identity prism for the brand. ^describe-six-facets
- Describe the physique facet first: what the brand is, what it does, and how it looks. ^physique-first
- Describe the reflection facet as the user that the brand portrays, not as the target market. ^reflection-is-not-the-target

From [Brand guidelines](../../references/brand-guidelines.md):

- Show each logo rule with a correct example and an incorrect example. ^do-and-dont-examples
- Write a section of the brand guidelines for each group of users, such as designers, writers, and partners. ^guidelines-per-audience
- Label each element of the brand guidelines as `sacred`, `interpretive`, or `customizable`. ^label-element-freedom
- Publish the brand guidelines and the asset files in one online source. ^one-online-source

From [Logo](../../references/brand-logo.md):

- Do not change the proportions or the order of the parts of a logo. ^keep-logo-proportions
- State the clear space around each logo as a part or a fraction of the logo. ^logo-clear-space
- Give each logo a version for light backgrounds and a version for dark backgrounds. ^logo-color-versions
- State a minimum size for each logo in print and on screens. ^logo-minimum-size
- Name each lockup of the logo and the layouts that it serves. ^name-each-lockup
- Do not place a logo on a busy or complex background. ^no-busy-logo-background
- Do not add a shadow, an outline, or a gradient to a logo. ^no-logo-effects
- Do not place type, photos, or graphics inside the clear space of a logo. ^nothing-in-clear-space

From [Brand architecture](../../references/brand-architecture.md):

- In a monolithic brand architecture, name each product with the parent brand and a generic descriptor. ^monolithic-descriptors
- State the brand architecture type of each product: monolithic, endorsed, or pluralistic. ^state-architecture-type

From [Type scale](../../references/type-scale.md):

- Record the base size and the ratio of the type scale in the brand guidelines. ^record-the-scale
- Set the base size of the type scale to the size of the body text. ^scale-from-body-size
- Take each text size in a design from the type scale. ^sizes-from-the-scale
- Name each text style by its role, such as display, headline, title, body, or label. ^text-style-roles
- Define each text style with a typeface, a weight, a size, and a letter spacing. ^text-style-values

From [Visual identity](../../references/visual-identity.md):

- Remove each variant of a color, a typeface, or a logo that the brand guidelines do not list. ^remove-unlisted-variants

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

## References

- You check the contrast of a pair of brand colors. Read [Accessibility](../../references/accessibility.md).
- The company has more than one brand, product name, or sub-brand. Read [Brand architecture](../../references/brand-architecture.md).
- You structure or publish the guidelines. Read [Brand guidelines](../../references/brand-guidelines.md).
- You describe the identity of the brand in the guidelines. Read [Brand identity prism](../../references/brand-identity-prism.md).
- You write the logo section of the guidelines. Read [Logo](../../references/brand-logo.md).
- You write the positioning statement of the brand. Read [Brand positioning statement](../../references/brand-positioning-statement.md).
- You write the strategy section of the guidelines. Read [Brand strategy](../../references/brand-strategy.md).
- You store the brand values as design tokens. Read [Brand systems](../../references/brand-systems.md).
- You write the voice and tone section of the guidelines. Read [Brand voice](../../references/brand-voice.md).
- You write the color section of the guidelines. Read [Color roles](../../references/color-roles.md).
- You write the typography section of the guidelines. Read [Type scale](../../references/type-scale.md).
- You list the colors, the typefaces, and the logo variants that the brand allows. Read [Visual identity](../../references/visual-identity.md).
