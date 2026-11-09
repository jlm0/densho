---
id: audit-accessibility
kind: densho:Skill
title: Audit the accessibility of an interface
status: proposed
origin: template
knowledge_type: domain
description: "Check an interface against the WCAG `2.2` success criteria of level A and AA. Use when a person asks for an accessibility check of an interface. Do not use it for a whole interface review (`review-interface`) or a code change (`review-code-change`)."
invocation: agent
skill_type: lens
uses:
  - accessibility
steps:
  - audit-the-interface
---

## Directives

- State the conformance level and the screens that the audit covers. ^state-the-audit-scope
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/TR/wcag-em-2/
- Check each screen of a complete process, not only its first screen. ^audit-complete-processes
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.w3.org/TR/wcag-em-2/

## Exit checklist

- [ ] Each failure names a directive of this skill.
- [ ] If the audit reads a design file, the report names each check that needs the running code.

## Output

A list of failures, and a list of the directives with no content to check. Each failure names the screen, the element, the directive that it breaks, and the change that you recommend. A design file does not show the checks of the code, such as names, roles, and the language of the page.
