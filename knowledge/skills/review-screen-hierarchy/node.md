---
id: review-screen-hierarchy
kind: densho:Skill
title: Review the hierarchy of a screen
status: proposed
origin: template
knowledge_type: domain
description: Review a screen for its hierarchy, its grouping, and its use of prose. Use when a person asks for a review of the hierarchy of a screen.
invocation: agent
skill_type: lens
uses:
  - information-hierarchy
  - visual-grouping
  - visual-communication
pointers:
  - kind: densho:TextPointer
    target: information-hierarchy
    trigger: You judge which element a viewer sees first.
  - kind: densho:TextPointer
    target: visual-grouping
    trigger: You judge which elements read as one group.
  - kind: densho:TextPointer
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
