---
id: software-security
kind: ka:PracticeArea
title: Security
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://top10.owasp.org/2025/
  - https://asvs.owasp.org/
  - https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md
broader:
  - software-engineering
pointers:
  - kind: ka:TextPointer
    target: access-control
    trigger: You set which users read or change a resource.
  - kind: ka:TextPointer
    target: injection
    trigger: Input from outside the code reaches a query, a command, or an output.
  - kind: ka:TextPointer
    target: secrets-management
    trigger: You store, pass, or log a secret.
  - kind: ka:TextPointer
    target: software-supply-chain
    trigger: You add, update, or remove a dependency.
---

## Definition

Protecting a system and its data from people who act outside their permissions. The OWASP Top 10 states a broad consensus on the most critical security risks to web applications. The OWASP Application Security Verification Standard (ASVS) gives a basis for testing the technical security controls of a web application, and lists the requirements for secure development.

## Directives

- Store each password as an `argon2id`, `scrypt`, `bcrypt`, or `PBKDF2` hash. ^hash-each-password
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x20-V11-Cryptography.md
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x92-Appendix-C_Cryptography.md
- Generate each token and each secret with a cryptographically secure random number generator. ^secure-random-for-secrets
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x20-V11-Cryptography.md
- Replace the session token of a user at each login. ^new-session-at-login
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x16-V7-Session-Management.md
  - sources: https://top10.owasp.org/2025/A07_2025-Authentication_Failures/
- Do not include a default account or a default password in a release. ^no-default-credentials
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md
  - sources: https://top10.owasp.org/2025/A07_2025-Authentication_Failures/
- Do not show a stack trace, a query, or a secret in an error message to a user. ^generic-error-message
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
  - sources: https://top10.owasp.org/2025/A02_2025-Security_Misconfiguration/
- If a step of a transaction fails, revert the whole transaction. ^revert-failed-transaction
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
  - sources: https://top10.owasp.org/2025/A10_2025-Mishandling_of_Exceptional_Conditions/
- Add a global handler that catches each exception that other code does not catch. ^global-exception-handler
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A10_2025-Mishandling_of_Exceptional_Conditions/
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x21-V12-Secure-Communication.md
- Do not put an API key or a session token in a URL. ^no-secret-in-url
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x23-V14-Data-Protection.md

## Notes

The directives cite OWASP Top 10:2025 and ASVS 5.0.0. ASVS gives each requirement a level from 1 to 3. Level 1 holds the minimum requirements to secure an application.

| Level | Directives on this node                                                                                 |
| ----- | ------------------------------------------------------------------------------------------------------- |
| 1     | `new-session-at-login`, `no-default-credentials`, `tls-for-external-connections`, `no-secret-in-url`    |
| 2     | `hash-each-password`, `secure-random-for-secrets`, `generic-error-message`, `revert-failed-transaction` |
| 3     | `global-exception-handler`, which the Top 10 also names                                                 |
