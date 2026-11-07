---
id: atomic-design
kind: densho:Concept
title: Atomic design
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://atomicdesign.bradfrost.com/chapter-2/
broader:
  - design-systems
---

## Definition

A method for building a design system in five stages that Brad Frost published in 2016. The stages run at the same time, not in sequence:

1. Atoms: the basic elements, such as a label, an input, or a button.
2. Molecules: simple groups of atoms that work as one unit, such as a search form.
3. Organisms: complex components that form a section of an interface, such as a header.
4. Templates: layouts that place components and show the structure of the content.
5. Pages: templates with real, representative content, which test the system.

## Directives

- Give each molecule one job. ^one-job-per-molecule
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atomicdesign.bradfrost.com/chapter-2/
- Build each new organism from the atoms and molecules that the system holds. ^compose-from-the-system
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atomicdesign.bradfrost.com/chapter-2/
- State the image sizes and the text lengths that each template accepts. ^state-content-limits
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atomicdesign.bradfrost.com/chapter-2/
- Test each template with real, representative content. ^test-with-real-content
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atomicdesign.bradfrost.com/chapter-2/
- Test each template with its shortest and its longest real content. ^test-content-extremes
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atomicdesign.bradfrost.com/chapter-2/
