---
id: visual-communication
kind: densho:Concept
title: Visual communication
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/icon-usability/
broader:
  - visual-design
related:
  - accessibility
---

## Definition

Using glyphs, images, and spatial composition to say what prose would otherwise say. A well-made glyph is fast to recognize and needs no translation, but few glyphs mean the same thing to everyone.

## Directives

- If a glyph, an image, or a grouping states the same information as a sentence, replace the sentence with it. ^prefer-visual-form
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Add a visible text label to each glyph, unless the glyph means home, print, or search. ^label-glyphs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/icon-usability/
- Do not hide a glyph label behind a hover. ^no-hover-labels
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/icon-usability/
- Do not use one glyph for two different functions. ^no-shared-glyph
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-similarity/
- Test each new glyph with users for recognition before you use it. ^test-new-glyphs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/icon-usability/

## Notes

These rules work together. A glyph can replace a sentence, but it keeps a short label unless its meaning is universal.
