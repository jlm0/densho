---
id: software-configuration-management
kind: densho:PracticeArea
title: Software configuration management
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
broader:
  - software-engineering
informs:
  - software-quality
pointers:
  - kind: densho:TextPointer
    target: trunk-based-development
    trigger: You create, merge, or release a branch.
  - kind: densho:TextPointer
    target: conventional-commits
    trigger: You write a commit message.
  - kind: densho:TextPointer
    target: build-pipeline
    trigger: You set up or change the automated build of a repository.
  - kind: densho:TextPointer
    target: semantic-versioning
    trigger: You choose the version number of a release.
---

## Definition

The control of the versions of software and of each change to it, from the commit to the released version. SWEBOK `v4` makes software configuration management a knowledge area. Here, it covers the branch model, the commit messages, the build pipeline, and the version numbers.
