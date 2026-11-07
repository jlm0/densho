---
id: fitts-law
kind: densho:Concept
title: Fitts's law
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/fitts-law/
broader:
  - interaction-design
related:
  - visual-grouping
---

## Definition

A model from research on human movement: the time to move a pointer, such as a cursor or a finger, to a target grows with the distance to the target and falls as the target grows. Paul Fitts published it in 1954. The time grows with the logarithm of the distance, so a target twice as far takes longer but not twice as long. For a rectangular target, the smaller of its width and height counts.

## Directives

- Make the text label of each icon button part of its target area. ^label-in-target
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/fitts-law/
- Place the submit button of a form next to its last field. ^submit-near-last-field
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/fitts-law/
- Show the options of a menu next to the control that opens it. ^menu-near-its-control
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/fitts-law/
- Place controls that users press in sequence close to each other. ^sequence-targets-close
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/fitts-law/
- Leave visible space between each pair of adjacent targets. ^space-between-targets
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/fitts-law/
- Make the visible area of each target as large as its active area. ^visible-target-matches-active
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/fitts-law/

## Notes

The edges of a screen stop a mouse pointer, so a target on an edge acts as a target of infinite size. A touch screen gives no such advantage: a study found that touch targets at the edges take longer to hit. A padded target with an invisible active area still makes people slow down near its visible edge.
