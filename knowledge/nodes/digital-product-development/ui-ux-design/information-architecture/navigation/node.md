---
id: navigation
kind: densho:Concept
title: Navigation
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/ia-vs-navigation/
broader:
  - information-architecture
depends_on:
  - categorization
---

## Definition

The interface components that let people move between the parts of a product. Navigation shows the information architecture, but it is not the same thing.

## Directives

- Keep repeated navigation elements in the same relative order on each screen. ^keep-navigation-order
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html
- Show the current location of the user in the navigation. ^show-current-location
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Make each back control return to the previous screen, not to the start of the flow. ^back-one-step
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/user-control-and-freedom/
- Do not disable the back button of the browser. ^keep-browser-back
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/user-control-and-freedom/
- Make the back button close a full-screen overlay. ^back-closes-overlay
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/user-control-and-freedom/
