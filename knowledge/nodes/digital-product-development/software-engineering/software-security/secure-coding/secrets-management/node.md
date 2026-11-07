---
id: secrets-management
kind: densho:Concept
title: Secrets management
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
  - https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x22-V13-Configuration.md
broader:
  - secure-coding
---

## Definition

The control of each secret over its whole life: its creation, its storage, its access, its rotation, and its revocation. A secret is a value that gives access to a system, such as a password, an API key, a private key, or a database credential.

## Directives

- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-architecture
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x22-V13-Configuration.md
- Give each secret only the permissions that its use needs. ^least-privilege-secret
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x22-V13-Configuration.md
  - sources: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Do not write a secret, a password, or a session token to a log. ^no-secret-in-log
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
  - sources: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Run a secret scanner in the pre-commit hook of each repository. ^scan-for-secrets-before-commit
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: software-construction
  - also_attached_to: software-quality
  - sources: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## Notes

After an exposure, the cheat sheet gives this order: revoke the secret, then rotate it, then delete it from the exposed system.
