<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Design tokens

## Directives

No directive is in force at this node.

## Definition

A named design decision, such as a color, a size, or a duration, that design tools and code read from one source. The Design Tokens Community Group of the W3C publishes the file format as the Design Tokens Format Module `2025.10`. A token file is JSON. An object with a `$value` is a token, and an object without one is a group. A group can set a `$type` for the tokens in it, and an alias is a token whose value names another token.

## Notes

The format defines these types: `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, and `number`, and the composite types `strokeStyle`, `border`, `transition`, `shadow`, `gradient`, and `typography`. A `dimension` uses `px` or `rem`, and a translation tool converts `px` to `dp` on Android and to `pt` on Apple platforms. A tool must not guess a type from a value. The format is a report of a community group, not a W3C standard.
