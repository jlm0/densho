---
id: access-control
kind: densho:Concept
title: Access control
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/
  - https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md
broader:
  - software-security
---

## Definition

The rules that limit each user to the functions and the data that the user has permission for. Access control is broken when a user can read, change, or delete data, or run a function, outside those permissions. OWASP Top 10:2025 ranks broken access control as the first risk.

## Directives

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md
  - sources: https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/
- Block access to each resource by default, unless the resource is public. ^deny-by-default
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md
- Check the permission of the user for each record that a request reads or changes. ^check-each-record
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md
  - sources: https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/
- Add a test for each access control rule. ^test-access-control
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/
- Log each failed access control check. ^log-access-failures
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/
  - sources: https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md
