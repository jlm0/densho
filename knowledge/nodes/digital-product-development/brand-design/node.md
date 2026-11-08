---
id: brand-design
kind: densho:Discipline
title: Brand design
status: proposed
origin: template
knowledge_type: domain
broader:
  - digital-product-development
pointers:
  - kind: densho:TextPointer
    target: brand-strategy
    trigger: You decide what a brand stands for, which associations it builds, or how it differs from other brands.
  - kind: densho:TextPointer
    target: brand-voice
    trigger: You define the voice of a brand or set the tone of a message.
  - kind: densho:TextPointer
    target: visual-identity
    trigger: You design or apply a logo, a brand color, or a type style.
  - kind: densho:TextPointer
    target: brand-systems
    trigger: You write brand guidelines, store brand values as tokens, or relate the brands of a company.
---

## Definition

The identity that a product presents: its name, voice, logo, color, typography, and imagery. It makes the product recognizable everywhere people meet it.

## Directives

- Take each color, typeface, and logo from the brand definition of the project. ^use-brand-definition
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://marketingscience.info/news-and-insights/brands-of-distinction
- Write each message to a user in the voice of the brand definition. ^write-in-brand-voice
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://styleguide.mailchimp.com/voice-and-tone/
  - sources: https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human

## Notes

A brand definition belongs to one project. A project states its values in a workspace node that names this node in `implements`.
