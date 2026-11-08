---
name: review-interface
description: "Review an interface for its hierarchy, its usability, and its accessibility. Use when a screen or a flow is ready for review."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review an interface

## Directives

No directive is in force at this node.

## Inputs

- The screens and the flows of the interface, as designs or as a running product

## Procedure

1. Run the skill `review-screen-hierarchy` on each screen.
2. Run the skill `review-usability` on each flow.
3. Run the skill `audit-accessibility` on the interface.
4. Put the findings of the 3 skills in one report, with a section for each skill.

## Output

One report with a section for each skill and its findings.

## Validation

Each screen has a hierarchy review, each flow has a usability review, and the interface has an accessibility check.

## References

- You check the interface for accessibility. Use the skill `audit-accessibility`.
- You review a screen of the interface. Use the skill `review-screen-hierarchy`.
- You review a flow of the interface. Use the skill `review-usability`.
- Read [UI/UX design](../../references/ui-ux-design.md).
