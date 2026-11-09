---
id: secure-coding
kind: densho:Concept
title: Secure coding
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://owasp.org/www-project-application-security-verification-standard/
  - https://top10.owasp.org/2025/
broader:
  - software-security
informs:
  - security-review
pointers:
  - kind: densho:TextPointer
    target: access-control
    trigger: You set which users read or change a resource.
  - kind: densho:TextPointer
    target: injection
    trigger: Input from outside the code reaches a query, a command, or an output.
  - kind: densho:TextPointer
    target: secrets-management
    trigger: You store, pass, or log a secret.
  - kind: densho:TextPointer
    target: software-supply-chain
    trigger: You add, update, or remove a dependency.
---

## Definition

The writing of code that resists attack. The OWASP Application Security Verification Standard gives the security requirements for the design, the development, and the testing of web applications and web services.

## Notes

This area holds four concepts: access control, injection, secrets management, and the software supply chain.
