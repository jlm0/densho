---
id: software-delivery
kind: ka:PracticeArea
title: Delivery
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://dora.dev/guides/dora-metrics/
broader:
  - software-engineering
pointers:
  - kind: ka:TextPointer
    target: trunk-based-development
    trigger: You create, merge, or release a branch.
  - kind: ka:TextPointer
    target: conventional-commits
    trigger: You write a commit message.
  - kind: ka:TextPointer
    target: semantic-versioning
    trigger: You choose the version number of a release.
  - kind: ka:TextPointer
    target: software-delivery-metrics
    trigger: You measure how a team delivers software.
---

## Definition

The path of a change from a commit to software that runs in production: integration, versioning, release, and deployment. Delivery performance is how fast and how safely changes move along that path.
