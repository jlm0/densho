---
id: software-security
kind: densho:PracticeArea
title: Software security
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
  - https://top10.owasp.org/2025/
  - https://asvs.owasp.org/
  - https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md
broader:
  - software-engineering
pointers:
  - kind: densho:TextPointer
    target: threat-modeling
    trigger: You design a new system or a new feature.
  - kind: densho:TextPointer
    target: secure-coding
    trigger: You write code that handles input, access, a secret, or a dependency.
  - kind: densho:TextPointer
    target: security-review
    trigger: You review a change for security flaws.
  - kind: densho:TextPointer
    target: security-assessment
    trigger: You audit the security of a system that already runs.
  - kind: densho:TextPointer
    target: vulnerability-management
    trigger: A vulnerability is reported in a system or in a dependency.
---

## Definition

Protecting a system and its data from people who act outside their permissions. The OWASP Top 10 states a broad consensus on the most critical security risks to web applications. The OWASP Application Security Verification Standard (ASVS) gives a basis for testing the technical security controls of a web application, and lists the requirements for secure development.

## Directives

- Store each password as an `argon2id`, `scrypt`, `bcrypt`, or `PBKDF2` hash. ^hash-each-password
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x20-V11-Cryptography.md#v114-hashing-and-hash-based-functions
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x92-Appendix-C_Cryptography.md#hash-functions-for-password-storage
- Generate each token and each secret with a cryptographically secure random number generator. ^secure-random-for-secrets
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x20-V11-Cryptography.md#v115-random-values
- Replace the session token of a user at each login. ^new-session-at-login
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x16-V7-Session-Management.md#v72-fundamental-session-management-security
  - sources: https://top10.owasp.org/2025/A07_2025-Authentication_Failures/
- Do not include a default account or a default password in a release. ^no-default-credentials
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md#v63-general-authentication-security
  - sources: https://top10.owasp.org/2025/A07_2025-Authentication_Failures/
- Do not show a stack trace, a query, or a secret in an error message to a user. ^generic-error-message
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md#v165-error-handling
  - sources: https://top10.owasp.org/2025/A02_2025-Security_Misconfiguration/
- If a step of a transaction fails, revert the whole transaction. ^revert-failed-transaction
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x11-V2-Validation-and-Business-Logic.md#v23-business-logic-security
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md#v165-error-handling
  - sources: https://top10.owasp.org/2025/A10_2025-Mishandling_of_Exceptional_Conditions/
- Add a global handler that catches each exception that other code does not catch. ^global-exception-handler
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://top10.owasp.org/2025/A10_2025-Mishandling_of_Exceptional_Conditions/
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md#v165-error-handling
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-architecture
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x21-V12-Secure-Communication.md#v122-https-communication-with-external-facing-services
- Do not put an API key or a session token in a URL. ^no-secret-in-url
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-architecture
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x23-V14-Data-Protection.md#v142-general-data-protection

## Notes

The directives cite OWASP Top 10:2025 and ASVS 5.0.0. ASVS gives each requirement a level from 1 to 3. Level 1 holds the minimum requirements to secure an application.

| Level | Directives on this node                                                                                 |
| ----- | ------------------------------------------------------------------------------------------------------- |
| 1     | `new-session-at-login`, `no-default-credentials`, `tls-for-external-connections`, `no-secret-in-url`    |
| 2     | `hash-each-password`, `secure-random-for-secrets`, `generic-error-message`, `revert-failed-transaction` |
| 3     | `global-exception-handler`, which the Top 10 also names                                                 |
