---
id: software-engineering
kind: ka:Discipline
title: Software engineering
status: proposed
origin: template
knowledge_type: domain
broader:
  - digital-product-development
---

## Definition

The design, construction, testing, and operation of software. It turns product and interface decisions into a system that keeps working as it changes.

## Directives

- Do not commit a secret to a repository. ^no-secret-in-repository
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Write a test for each change in behavior. ^test-each-behavior-change
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
