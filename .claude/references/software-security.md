<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software security

## Directives

No directive is in force at this node.

## Definition

Protecting a system and its data from people who act outside their permissions. The OWASP Top 10 states a broad consensus on the most critical security risks to web applications. The OWASP Application Security Verification Standard (ASVS) gives a basis for testing the technical security controls of a web application, and lists the requirements for secure development.

## Notes

The directives cite OWASP Top 10:2025 and ASVS 5.0.0. ASVS gives each requirement a level from 1 to 3. Level 1 holds the minimum requirements to secure an application.

| Level | Directives on this node                                                                                 |
| ----- | ------------------------------------------------------------------------------------------------------- |
| 1     | `new-session-at-login`, `no-default-credentials`, `tls-for-external-connections`, `no-secret-in-url`    |
| 2     | `hash-each-password`, `secure-random-for-secrets`, `generic-error-message`, `revert-failed-transaction` |
| 3     | `global-exception-handler`, which the Top 10 also names                                                 |

## References

- You write code that handles input, access, a secret, or a dependency. Read [Secure coding](secure-coding.md).
- You audit the security of a system that already runs. Read [Security assessment](security-assessment.md).
- You review a change for security flaws. Read [Security review](security-review.md).
- You design a new system or a new feature. Read [Threat modeling](threat-modeling.md).
- A vulnerability is reported in a system or in a dependency. Read [Vulnerability management](vulnerability-management.md).
