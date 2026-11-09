---
id: visual-design
kind: densho:PracticeArea
title: Visual design
status: proposed
origin: template
knowledge_type: domain
broader:
  - ui-ux-design
informs:
  - design-systems
pointers:
  - kind: densho:TextPointer
    target: information-hierarchy
    trigger: You rank the elements of a screen.
  - kind: densho:TextPointer
    target: visual-grouping
    trigger: You place, style, or frame related elements on a screen.
  - kind: densho:TextPointer
    target: visual-communication
    trigger: You choose between prose and a visual form.
---

## Definition

The visual form of an interface: its layout, type, color, imagery, and spacing. It decides what people notice first and how they read a screen.

## Directives

- Use at most `2` primary and `2` secondary colors in an interface, unless the brand guidelines set a larger palette. ^limit-color-palette
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/#toc-1-color-and-contrast-1
- If an interface uses more than `2` primary and `2` secondary colors, give each color a different value or saturation. ^vary-colors-in-large-palette
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/#toc-1-color-and-contrast-1
