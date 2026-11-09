---
id: injection
kind: densho:Concept
title: Injection
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://top10.owasp.org/2025/A05_2025-Injection/
  - https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x10-V1-Encoding-and-Sanitization.md
broader:
  - secure-coding
---

## Definition

A flaw that lets untrusted input reach an interpreter, such as a database, a shell, or a browser, as part of a command. The interpreter then runs the input as code. SQL injection, command injection, and cross-site scripting are kinds of injection.

## Directives

- Use parameterized queries or an ORM for each database query. ^parameterize-queries
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x10-V1-Encoding-and-Sanitization.md#v12-injection-prevention
  - sources: https://top10.owasp.org/2025/A05_2025-Injection/
- Pass each argument of an operating system command as a separate parameter, not through a shell string. ^no-shell-string
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x10-V1-Encoding-and-Sanitization.md#v12-injection-prevention
  - sources: https://top10.owasp.org/2025/A05_2025-Injection/
- Do not use `eval` or another feature that runs dynamic code. ^no-dynamic-code
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x10-V1-Encoding-and-Sanitization.md#v13-sanitization
- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-architecture
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x11-V2-Validation-and-Business-Logic.md#v22-input-validation
  - sources: https://top10.owasp.org/2025/A05_2025-Injection/
- Encode each untrusted value for the context where the output uses it. ^encode-output-for-context
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x10-V1-Encoding-and-Sanitization.md#v12-injection-prevention

## Notes

Input validation alone does not stop injection. The Top 10 calls it an incomplete defense, so the query and the encoding rules apply to validated input too.
