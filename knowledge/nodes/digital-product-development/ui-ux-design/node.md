---
id: ui-ux-design
kind: ka:Discipline
title: UI/UX design
status: proposed
origin: template
knowledge_type: domain
broader:
  - digital-product-development
informs:
  - software-engineering
pointers:
  - kind: ka:TextPointer
    target: information-architecture
    trigger: You organize or name the content of a product.
  - kind: ka:TextPointer
    target: interaction-design
    trigger: You decide how an interface responds to a person.
  - kind: ka:TextPointer
    target: visual-design
    trigger: You decide how a screen looks.
  - kind: ka:TextPointer
    target: accessibility
    trigger: You build a control, a text style, or a color choice.
  - kind: ka:TextPointer
    target: responsive-design
    trigger: You fit a layout to a screen size.
  - kind: ka:SkillPointer
    target: design-settings-interface
    trigger: You design or change a settings screen.
  - kind: ka:SkillPointer
    target: review-screen-hierarchy
    trigger: A screen design is ready for review.
---

## Definition

The design of how people understand and operate a product. It covers how information is organized, how the interface responds, and how each screen looks.

## Directives

- Show only the content and the controls that the current task needs. ^show-what-the-task-needs
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Do not add a sentence that repeats what a heading, a label, or a value states. ^no-repeated-text
  - scope: subtree
  - status: proposed
  - origin: template
- Use one word for one meaning in each interface. ^one-word-one-meaning
  - scope: subtree
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
