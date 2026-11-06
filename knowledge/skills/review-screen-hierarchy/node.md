---
id: review-screen-hierarchy
kind: ka:Skill
title: Review the hierarchy of a screen
status: proposed
origin: template
knowledge_type: domain
description: Review a screen for its hierarchy, its grouping, and its use of prose. Use when a screen design is ready for review.
uses:
  - information-hierarchy
  - visual-grouping
  - visual-communication
applies:
  - contrast-regular-text
  - contrast-large-text
pointers:
  - kind: ka:TextPointer
    target: information-hierarchy
    trigger: You judge which element a viewer sees first.
  - kind: ka:TextPointer
    target: visual-grouping
    trigger: You judge which elements read as one group.
  - kind: ka:TextPointer
    target: visual-communication
    trigger: You find prose that a visual form replaces.
---

## Inputs

- The screen, as a design or a running interface
- The task that a person does on the screen

## Procedure

1. Read each directive that this skill lists.
2. Name the element that a viewer sees first, then second, then third.
3. Compare that order with the order of importance for the task.
4. Mark each group that the spacing shows, and compare it with the groups that the task needs.
5. Mark each sentence and label that a glyph, an image, or a grouping replaces.

## Output

A list of findings. Each finding names the element, the directive that it breaks, and the change that you recommend.

## Validation

Each finding names a directive from the first step of the procedure. A finding with no directive is an opinion, so label it as one.
