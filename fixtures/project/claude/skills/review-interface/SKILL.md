---
name: review-interface
description: "Review an interface for its hierarchy, its usability, and its accessibility. Use when a screen or a flow is ready for review. Do not use it for a design (`design-interface`) or a code change (`review-code-change`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review an interface

## Run the review lenses

1. Collect the screens and the flows of the interface, as designs or as a running product.
2. Run the skill `review-screen-hierarchy` on each screen.
3. Run the skill `review-usability` on each flow.
4. Run the skill `audit-accessibility` on the interface.
5. Put the findings of the `3` skills in one report, with a section for each skill.

Output: The findings of the `3` skills.

## Exit checklist

- [ ] Each screen has a hierarchy review.
- [ ] Each flow has a usability review.
- [ ] The interface has an accessibility check.

## Output

One report with a section for each skill and its findings.

## References

- You check the interface for accessibility. Use the skill `audit-accessibility`.
- You review a screen of the interface. Use the skill `review-screen-hierarchy`.
- You review a flow of the interface. Use the skill `review-usability`.
