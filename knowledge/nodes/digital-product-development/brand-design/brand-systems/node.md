---
id: brand-systems
kind: densho:PracticeArea
title: Brand systems
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://catalogimages.wiley.com/images/db/pdf/9781118980828.excerpt.pdf
  - https://www.designtokens.org/glossary/
broader:
  - brand-design
related:
  - design-systems
pointers:
  - kind: densho:TextPointer
    target: brand-guidelines
    trigger: You write, structure, or publish the brand guidelines.
  - kind: densho:TextPointer
    target: brand-architecture
    trigger: You name a new product, a sub-brand, or an acquired company.
---

## Definition

The structures that keep a brand the same across products, teams, and channels. Brand guidelines record the rules and hold the assets. Design tokens carry the brand values into design tools and code. The brand architecture relates the brands of one company to each other.

## Directives

- Store the brand colors, typefaces, and type scale in design token files. ^brand-values-as-tokens
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.designtokens.org/glossary/

## Notes

The design tokens node holds the rules for the token file and for each alias. The design systems practice area holds the rule that a component uses a token, not a raw value. A brand that stores its values as tokens gives the design system and the brand guidelines one source for each value.

Wheeler quotes Hampton Bridwell of Tenet Partners, who describes brand governance as the managed work of behavior, communication, design, legal compliance, process, and measurement that drives the performance of a brand across a company. In Wheeler's account, governance has moved from central approval at the last step to education, self-service, and a role early in the work.
