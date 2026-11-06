---
id: design-tokens
kind: ka:Concept
title: Design tokens
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.designtokens.org/tr/2025.10/format/
  - https://www.designtokens.org/glossary/
broader:
  - design-systems
---

## Definition

A named design decision, such as a color, a size, or a duration, that design tools and code read from one source. The Design Tokens Community Group of the W3C publishes the file format as the Design Tokens Format Module `2025.10`. A token file is JSON. An object with a `$value` is a token, and an object without one is a group. A group can set a `$type` for the tokens in it, and an alias is a token whose value names another token.

## Directives

- Give each design token a `$value`. ^token-value
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Declare a `$type` on each design token or on a group above it. ^token-type
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Do not start the name of a token or a group with `$`. ^no-dollar-token-name
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Do not put `{`, `}`, or `.` in the name of a token or a group. ^no-reserved-token-characters
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Do not give a `$value` to an object that holds tokens or groups. ^no-value-on-group
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Write each reference to another token as its path in curly braces, such as `{color.text.base}`. ^alias-in-braces
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Do not make a chain of token references that leads back to its start. ^no-circular-alias
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Name each design token file with the extension `.tokens` or `.tokens.json`. ^tokens-file-extension
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Do not give two tokens in one group names that differ only in case. ^no-case-only-token-names
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Put the data of each tool in `$extensions` under a key in reverse domain notation. ^vendor-key-extensions
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Do not put data in `$extensions` that the meaning of a token value depends on. ^no-required-extension-data
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/
- Mark each token that you plan to remove with `$deprecated`. ^deprecate-tokens
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/tr/2025.10/format/

## Notes

The format defines these types: `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, and `number`, and the composite types `strokeStyle`, `border`, `transition`, `shadow`, `gradient`, and `typography`. A `dimension` uses `px` or `rem`, and a translation tool converts `px` to `dp` on Android and to `pt` on Apple platforms. A tool must not guess a type from a value. The format is a report of a community group, not a W3C standard.
