---
id: ui-ux-design
kind: densho:Discipline
title: UI/UX design
status: proposed
origin: template
knowledge_type: domain
broader:
  - digital-product-development
pointers:
  - kind: densho:TextPointer
    target: information-architecture
    trigger: You organize or name the content of a product.
  - kind: densho:TextPointer
    target: interaction-design
    trigger: You decide how an interface responds to a person.
  - kind: densho:TextPointer
    target: visual-design
    trigger: You decide how a screen looks.
  - kind: densho:TextPointer
    target: accessibility
    trigger: You build a control, a form, a text style, a color choice, or media.
  - kind: densho:TextPointer
    target: responsive-design
    trigger: You fit a layout to a screen size.
  - kind: densho:TextPointer
    target: platform-conventions
    trigger: You design for a specific operating system or with its components.
  - kind: densho:TextPointer
    target: design-systems
    trigger: You build or use the tokens and the components of a design system.
  - kind: densho:SkillPointer
    target: design-settings-interface
    trigger: You design or change a settings screen.
  - kind: densho:SkillPointer
    target: review-screen-hierarchy
    trigger: A screen design is ready for review.
  - kind: densho:SkillPointer
    target: review-usability
    trigger: A flow is ready for a usability review.
  - kind: densho:SkillPointer
    target: audit-accessibility
    trigger: A screen, a component, or a flow needs an accessibility check.
---

## Definition

The design of how people understand and operate a product. It covers how information is organized, how the interface responds, and how each screen looks.

## Directives

- Show only the content and the controls that the current task needs. ^show-what-the-task-needs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Do not add a sentence that repeats what a heading, a label, or a value states. ^no-repeated-text
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Use one word for one meaning in each interface. ^one-word-one-meaning
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
