---
id: ui-contract
kind: densho:Concept
title: UI contract
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://storybook.js.org/docs/get-started/whats-a-story
  - https://storybook.js.org/docs/api/csf
broader:
  - software-design
related:
  - atomic-design
---

## Definition

The agreed states and inputs of each interface component, written down before the team builds the component. A Storybook story captures the rendered state of a UI component, and a component gets a story for each interesting state that it supports. Component Story Format is an open standard for stories, based on ES6 modules. A UI contract is not the contract of contract testing, which covers the messages between a consumer and a provider.
