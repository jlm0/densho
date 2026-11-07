---
id: software-engineering
kind: densho:Discipline
title: Software engineering
status: proposed
origin: template
knowledge_type: domain
broader:
  - digital-product-development
pointers:
  - kind: densho:TextPointer
    target: software-security
    trigger: You write code that handles input, a user account, or a secret.
  - kind: densho:TextPointer
    target: software-testing
    trigger: You write a test or fix a bug.
  - kind: densho:TextPointer
    target: software-delivery
    trigger: You make a commit, a branch, or a release.
  - kind: densho:TextPointer
    target: software-architecture
    trigger: You design the structure of a system or change it.
  - kind: densho:TextPointer
    target: software-reliability
    trigger: You define, monitor, or alert on the reliability of a service.
  - kind: densho:TextPointer
    target: code-review
    trigger: You review a change or prepare a change for review.
  - kind: densho:SkillPointer
    target: write-decision-record
    trigger: You make or change a decision about the structure of a system.
  - kind: densho:SkillPointer
    target: review-code-change
    trigger: A change is ready for review.
---

## Definition

The design, construction, testing, and operation of software. It turns product and interface decisions into a system that keeps working as it changes.

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
