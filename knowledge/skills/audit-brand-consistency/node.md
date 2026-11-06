---
id: audit-brand-consistency
kind: ka:Skill
title: Audit brand consistency
status: proposed
origin: template
knowledge_type: domain
description: Check the touchpoints of a brand against its guidelines, and list each inconsistency. Use when you review the touchpoints of a brand for consistency.
invocation: agent
uses:
  - visual-identity
  - brand-logo
  - color-roles
  - type-scale
  - distinctive-brand-assets
  - brand-voice
  - brand-guidelines
pointers:
  - kind: ka:TextPointer
    target: visual-identity
    trigger: You find a color, a typeface, or a logo variant that the guidelines do not list.
  - kind: ka:TextPointer
    target: brand-logo
    trigger: You check the logo on a touchpoint.
  - kind: ka:TextPointer
    target: color-roles
    trigger: You check the colors on a touchpoint.
  - kind: ka:TextPointer
    target: type-scale
    trigger: You check the text styles on a touchpoint.
  - kind: ka:TextPointer
    target: distinctive-brand-assets
    trigger: You check where the distinctive assets of the brand appear.
  - kind: ka:TextPointer
    target: brand-voice
    trigger: You check the voice and the tone of the copy on a touchpoint.
  - kind: ka:TextPointer
    target: brand-guidelines
    trigger: You find a rule that the guidelines lack or state in two ways.
---

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
