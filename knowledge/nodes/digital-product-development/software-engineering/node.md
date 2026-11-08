---
id: software-engineering
kind: densho:Discipline
title: Software engineering
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
broader:
  - digital-product-development
pointers:
  - kind: densho:TextPointer
    target: software-requirements
    trigger: You define the requirements of a change.
  - kind: densho:TextPointer
    target: software-architecture
    trigger: You design the structure of a system or change it.
  - kind: densho:TextPointer
    target: software-design
    trigger: You define the interface of an API or a component.
  - kind: densho:TextPointer
    target: software-testing
    trigger: You write a test or fix a bug.
  - kind: densho:TextPointer
    target: software-construction
    trigger: You write the code of a service, a client, or its infrastructure.
  - kind: densho:TextPointer
    target: software-configuration-management
    trigger: You make a commit, a branch, or a build.
  - kind: densho:TextPointer
    target: software-quality
    trigger: You review, verify, or accept a change.
  - kind: densho:TextPointer
    target: software-operations
    trigger: You deploy or monitor a service.
  - kind: densho:TextPointer
    target: software-security
    trigger: You write code that handles input, a user account, or a secret.
---

## Definition

The design, construction, testing, and operation of software. It turns product and interface decisions into a system that keeps working as it changes. Its practice areas follow the knowledge areas of the Guide to the Software Engineering Body of Knowledge (SWEBOK) `v4`, in the order of the work: requirements, architecture, design, testing, construction, configuration management, quality, and operations. Security runs across each step.

## Directives

- Do not commit a secret to a repository. ^no-secret-in-repository
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x22-V13-Configuration.md
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Write a test for each change in behavior. ^test-each-behavior-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/developer/small-cls.html
  - sources: https://abseil.io/resources/swe-book/html/ch11.html
