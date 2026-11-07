---
id: software-supply-chain
kind: densho:Concept
title: Software supply chain
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures/
broader:
  - software-security
---

## Definition

The third-party code, tools, and services that build, distribute, and update a system: its direct and transitive dependencies, its build pipeline, and its package registries. A supply chain failure is a vulnerable or malicious part of that chain that reaches the system.

## Directives

- Remove each dependency that the code does not use. ^remove-unused-dependency
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures/
- Before you add a dependency, check its version for known vulnerabilities. ^check-new-dependency
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures/
- Download each dependency from a trusted registry over a secure connection. ^trusted-registry
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures/
- Replace each dependency that no longer receives security fixes. ^replace-unmaintained-dependency
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A03_2025-Software_Supply_Chain_Failures/
