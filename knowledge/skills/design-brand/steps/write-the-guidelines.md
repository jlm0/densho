---
title: Write the brand guidelines
pages:
  - target: brand-systems
    trigger: You write brand guidelines, store brand values as tokens, or relate the brands of a company.
  - target: brand-guidelines
    trigger: You write, structure, or publish the brand guidelines.
  - target: brand-architecture
    trigger: You name a new product, a sub-brand, or an acquired company.
  - target: design-tokens
    trigger: You name, store, or reference a color, a size, a space, or a type style.
directives:
  - label-element-freedom
  - sacred-element
  - interpretive-element
  - customizable-element
  - do-and-dont-examples
  - guidelines-per-audience
  - one-online-source
  - brand-values-as-tokens
  - role-as-alias
branches:
  - condition: If the company has more than one brand
    directives:
      - state-architecture-type
      - monolithic-descriptors
  - condition: If you add or change a token file
    directives:
      - token-value
      - token-type
      - alias-in-braces
      - no-circular-alias
      - no-value-on-group
      - no-dollar-token-name
      - no-reserved-token-characters
      - no-case-only-token-names
      - deprecate-tokens
      - no-required-extension-data
      - vendor-key-extensions
      - tokens-file-extension
missing_rules:
  - No directive states how to choose the architecture type of a new product or an acquired company.
---

## Procedure

01. If step `1` lists no section that this step writes, skip this step.
02. Collect the products and the brands of the company.
03. Collect the groups of people who apply the brand, inside and outside the company.
04. If the company has more than one brand, state the architecture type of each product.
05. If the brand has no voice and tone guide, run `define-brand-voice`.
06. Add the voice and tone section from the voice and tone guide.
07. Label each element as `sacred`, `interpretive`, or `customizable`.
08. Add a correct and an incorrect example for each logo rule.
09. Store the colors, the typefaces, and the type scale as design tokens.
10. Link the token files from the guidelines.
11. Give each group of people who apply the brand a section with the rules and the assets that it uses.

## Output

One set of brand guidelines in one online source, with the asset files and the token files beside it.
