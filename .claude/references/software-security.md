<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Security

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

- You set which users read or change a resource. Read [Access control](access-control.md).
- Input from outside the code reaches a query, a command, or an output. Read [Injection](injection.md).
- You store, pass, or log a secret. Read [Secrets management](secrets-management.md).
- You add, update, or remove a dependency. Read [Software supply chain](software-supply-chain.md).
