---
name: design-brand
description: "Define the strategy, the voice, the visual identity, and the guidelines of a brand. Use when you define or change the strategy, the voice, the visual identity, or the guidelines of a brand."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Design a brand

## Directives

From [Brand design](../../references/brand-design.md):

- Take each color, typeface, and logo from the brand definition of the project. ^use-brand-definition
- Write each message to a user in the voice of the brand definition. ^write-in-brand-voice

From [Brand voice](../../references/brand-voice.md):

- Remove each joke that makes a message less clear. ^clarity-over-jokes
- Do not add a joke to an error message. ^no-joke-in-errors
- Write the tone guidance for each type of message, such as an error, a success, or an onboarding step. ^tone-by-message-type
- Match the tone of each message to the emotional state of the reader. ^tone-matches-reader
- For each voice trait, list the emotional states of the reader that increase the trait and that reduce it. ^trait-by-reader-state
- Name a trait to avoid for each voice trait, such as direct but not curt. ^trait-to-avoid
- Describe the brand voice in `3` or `4` traits. ^voice-trait-count

From [Visual identity](../../references/visual-identity.md):

- Remove each variant of a color, a typeface, or a logo that the brand guidelines do not list. ^remove-unlisted-variants

From [Brand systems](../../references/brand-systems.md):

- Store the colors and the typography of the brand as a set of design tokens, the brand theme. ^brand-values-as-tokens

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Digital product development](../../references/digital-product-development.md), and follow each directive from Digital product development.
- Read [Accessibility](../../references/accessibility.md), and follow these directives from it: `contrast-large-text`, `contrast-regular-text`, `contrast-ui-components`, `no-color-only`.

## Steps

Run the steps in this order:

1. [Brand strategy](steps/brand-strategy.md)
2. [Brand voice](steps/brand-voice.md)
3. [Visual identity](steps/visual-identity.md)
4. [Brand systems](steps/brand-systems.md)

For each step:

1. Read its step file and each required read in it.
2. If the output of the step exists already, go to the next step.
3. Run the procedure of the step.
4. Go to the next step only after the exit gate of the step passes.
