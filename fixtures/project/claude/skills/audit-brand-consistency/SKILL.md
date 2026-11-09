---
name: audit-brand-consistency
description: "Check the touchpoints of a brand against its guidelines, and list each inconsistency. Use when you review the touchpoints of a brand for consistency."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Audit brand consistency

## Directives

From [Brand systems](../../references/brand-systems.md):

- Store the colors and the typography of the brand as a set of design tokens, the brand theme. ^brand-values-as-tokens

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

From [Brand voice](../../references/brand-voice.md):

- Remove each joke that makes a message less clear. ^clarity-over-jokes
- Do not add a joke to an error message. ^no-joke-in-errors
- Write the tone guidance for each type of message, such as an error, a success, or an onboarding step. ^tone-by-message-type
- Match the tone of each message to the emotional state of the reader. ^tone-matches-reader
- For each voice trait, list the emotional states of the reader that increase the trait and that reduce it. ^trait-by-reader-state
- Name a trait to avoid for each voice trait, such as direct but not curt. ^trait-to-avoid
- Describe the brand voice in `3` or `4` traits. ^voice-trait-count

From [Brand guidelines](../../references/brand-guidelines.md):

- Label an element of the brand guidelines `customizable` if the guidelines allow each team to change it. ^customizable-element
- Show each logo rule with a correct example and an incorrect example. ^do-and-dont-examples
- Write a section of the brand guidelines for each group of users, such as designers, writers, and partners. ^guidelines-per-audience
- Label an element of the brand guidelines `interpretive` if the guidelines allow a change to it within a stated range. ^interpretive-element
- Label each element of the brand guidelines as `sacred`, `interpretive`, or `customizable`. ^label-element-freedom
- Publish the brand guidelines and the asset files in one online source. ^one-online-source
- Label an element of the brand guidelines `sacred` if the guidelines allow no change to it. ^sacred-element

From [Distinctive brand assets](../../references/distinctive-brand-assets.md):

- Do not remove a distinctive asset from an advertisement or a package design. ^keep-distinctive-assets
- Measure the fame and the uniqueness of a brand element before you treat it as a distinctive asset. ^measure-asset-strength
- Do not replace a distinctive asset before you measure its fame and its uniqueness. ^measure-before-replacing
- Do not choose a brand element that is famous but not unique. ^no-famous-shared-elements
- When you choose a brand element to build, choose by uniqueness first and by fame second. ^uniqueness-before-fame

From [Logo](../../references/brand-logo.md):

- Do not change the proportions or the order of the parts of a logo. ^keep-logo-proportions
- State the clear space around each logo as a part or a fraction of the logo. ^logo-clear-space
- Give each logo a version for light backgrounds and a version for dark backgrounds. ^logo-color-versions
- State a minimum size for each logo in print and on screens. ^logo-minimum-size
- Name each lockup of the logo and the layouts that it serves. ^name-each-lockup
- Place a logo only where each part of it has the contrast ratio that text of its size needs. ^no-busy-logo-background
- Do not add a shadow, an outline, or a gradient to a logo. ^no-logo-effects
- Do not place type, photos, or graphics inside the clear space of a logo. ^nothing-in-clear-space

From [Type scale](../../references/type-scale.md):

- Record the base size and the ratio of the type scale in the brand guidelines. ^record-the-scale
- Set the base size of the type scale to the size of the body text. ^scale-from-body-size
- Take each text size in a design from the type scale. ^sizes-from-the-scale
- Name each text style by its role, such as display, headline, title, body, or label. ^text-style-roles
- Define each text style with a typeface, a weight, a size, and a letter spacing. ^text-style-values

From [Visual identity](../../references/visual-identity.md):

- Remove each variant of a color, a typeface, or a logo that the brand guidelines do not list. ^remove-unlisted-variants

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.
- Read [Accessibility](../../references/accessibility.md), and follow these directives from it: `no-color-only`.

## Inputs

- The brand guidelines, the voice and tone guide, and the design token files
- The touchpoints to review: screens, emails, advertisements, packaging, documents, and social media
- The list of distinctive assets, with their measures of fame and uniqueness if the brand has them

## Procedure

1. Read each directive that this skill lists.
2. List the touchpoints in scope, and collect a current sample of each one.
3. For each sample, compare the logo with the logo rules: the lockup, the clear space, the size, the background, and the effects.
4. Compare each color with the palette and the color roles. Record each color that the palette does not hold.
5. Compare each text style with the type scale and the text styles of the guidelines.
6. Compare the voice and the tone of the copy with the guide for its type of message.
7. Check that each distinctive asset appears where the guidelines place it.
8. Record each rule that the guidelines lack, or that two parts of the guidelines state in different ways.
9. Group the findings by element, and order them by the number of people who see each touchpoint.

## Output

A table with one row for each finding: the touchpoint, the element, the rule that applies, what the sample shows, and the fix. Below it, a list of the gaps and the conflicts in the guidelines.

## Validation

Check the findings against each directive from the first step of the procedure, and report each one it misses. Each finding names a rule of the guidelines or a directive. Each touchpoint in the list of step 2 has a result.

## References

- You find a rule that the guidelines lack or state in two ways. Read [Brand guidelines](../../references/brand-guidelines.md).
- You check the logo on a touchpoint. Read [Logo](../../references/brand-logo.md).
- You check the voice and the tone of the copy on a touchpoint. Read [Brand voice](../../references/brand-voice.md).
- You check the colors on a touchpoint. Read [Color roles](../../references/color-roles.md).
- You check where the distinctive assets of the brand appear. Read [Distinctive brand assets](../../references/distinctive-brand-assets.md).
- You check the text styles on a touchpoint. Read [Type scale](../../references/type-scale.md).
- You find a color, a typeface, or a logo variant that the guidelines do not list. Read [Visual identity](../../references/visual-identity.md).
