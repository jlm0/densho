---
name: audit-accessibility
description: "Check an interface against the WCAG `2.2` success criteria of level A and AA. Use when a person asks for an accessibility check of an interface. Do not use it for a whole interface review (`review-interface`) or a code change (`review-code-change`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Audit the accessibility of an interface

## Run the skill

1. Check the work against each directive of the skill.
2. If you need the definition or the notes of a page, read the page.

## Audit the interface

01. Collect the interface, as a design or as running code.
02. If the person names no conformance level, use level AA.
03. Collect the browsers, the devices, and the assistive technologies that the product supports.
04. State the scope: the screens, the complete processes, the conformance level, and the supported technologies.
05. List the common screens, the essential functions, and each complete process of the interface.
06. Check each screen against each directive.
07. Use a keyboard alone, a screen reader, text at `200` percent, and a width of `320` CSS pixels.
08. Check each step of each complete process in the same way.
09. Write each failure with the screen, the element, the directive, and the change that you recommend.
10. List each directive with no content to check, such as the caption rules on a screen with no video.

Pages:

- You check the interface against a success criterion or its exception. Read [Accessibility](../../references/accessibility.md).

Directives:

No directive of this step is in force.

Output: A list of failures, and a list of the directives with no content to check.

## Exit checklist

- [ ] Each failure names a directive of this skill.
- [ ] If the audit reads a design file, the report names each check that needs the running code.

## Output

A list of failures, and a list of the directives with no content to check. Each failure names the screen, the element, the directive that it breaks, and the change that you recommend. A design file does not show the checks of the code, such as names, roles, and the language of the page.
