---
id: audit-accessibility
kind: densho:Skill
title: Audit the accessibility of an interface
status: proposed
origin: template
knowledge_type: domain
description: Check an interface against the WCAG `2.2` success criteria of level A and AA. Use when a screen, a component, or a flow needs an accessibility check.
invocation: agent
uses:
  - accessibility
applies:
  - keep-navigation-order
pointers:
  - kind: densho:TextPointer
    target: accessibility
    trigger: You check the interface against a success criterion or its exception.
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

## Inputs

- The interface, as a design or as running code
- The conformance level, which is AA if the person names no other level
- The browsers, the devices, and the assistive technologies that the product supports

## Procedure

1. Read each directive that this skill lists.
2. State the scope: the screens, the complete processes, the conformance level, and the supported technologies.
3. List the common screens, the essential functions, and each complete process of the interface.
4. Check each screen against each directive. For the checks that need them, use a keyboard alone, a screen reader, text at `200` percent, and a width of `320` CSS pixels.
5. Check each step of each complete process in the same way.
6. Write each failure with the screen, the element, the directive, and the change that you recommend.
7. List each directive that the interface gives no content for, such as the caption rules on a screen with no video.

## Output

A list of failures, and a list of the directives with no content to check. Each failure names the screen, the element, the directive that it breaks, and the change that you recommend.

## Validation

Each failure names a directive from the first step of the procedure. A design file cannot show the code checks, such as names, roles, and the language of the page, so state each check that needs the running code.
