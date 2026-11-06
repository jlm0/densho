---
id: visual-communication
kind: ka:Concept
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

- Prefer a glyph, an image, or a grouping over prose when it states the same information. ^prefer-visual-form
  - scope: subtree
  - status: proposed
  - origin: template
- Add a visible text label to each glyph, unless the glyph means home, print, or search. ^label-glyphs
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/icon-usability/
- Do not hide a glyph label behind a hover. ^no-hover-labels
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/icon-usability/

## Notes

These rules work together. A glyph can replace a sentence, but it keeps a short label unless its meaning is universal.
