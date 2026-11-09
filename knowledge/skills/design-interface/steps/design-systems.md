---
title: Specify the components and the tokens
pages:
  - target: design-systems
    trigger: You build or use the tokens and the components of a design system.
  - target: atomic-design
    trigger: You build, combine, or test the components of a design system.
  - target: design-tokens
    trigger: You name, store, or reference a color, a size, a space, or a type style.
  - target: accessibility
    trigger: You build a control, a form, a text style, a color choice, or media.
directives:
  - use-tokens-not-values
  - compose-from-the-system
  - one-job-per-molecule
  - state-content-limits
  - test-with-real-content
  - test-content-extremes
  - name-non-text-controls
  - name-role-value
branches:
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
  - condition: If the target is an Apple device
    directives:
      - apple-system-color-values
missing_rules:
  - No directive covers how to record a new component in the design system, with its states and its rules for use.
---

## Procedure

1. Map each element of each screen to a component that the system holds.
2. If an element has no component, build a new component for it.
3. Map each color, size, and space to a design token.
4. State the name, the role, and each state of each custom control.
5. Test each template with real content.

## Output

The design tokens and the components that the screens use, with the rules for their use.
