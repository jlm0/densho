---
name: review-usability
description: "Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a person asks for a usability review of a flow. Do not use it for a whole interface (`review-interface`) or an accessibility check (`audit-accessibility`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review the usability of a flow

## Run the skill

1. Check the work against each directive of the skill.
2. If you need the definition or the notes of a page, read the page.

## Review the flow

01. Collect the screens of the flow in the order of the task, as designs or a running interface.
02. State the scope of the review: the users, the task, and the platform.
03. Follow the task once from its start to its end to learn the flow.
04. Do not record a finding on this first pass.
05. Follow the task a second time.
06. On each screen, check each heuristic and each directive.
07. Check the size and the position of each target, and the number of choices at each step.
08. Write each finding with the screen, the element, the heuristic or the directive, and the change that you recommend.
09. Give each finding its severity.
10. Sort the findings from the highest severity.

Pages:

- You judge the feedback, the exits, the confirmations, the error messages, or the help of the flow. Read [Usability heuristics](../../references/usability-heuristics.md).
- You judge the size or the position of a target. Read [Fitts's law](../../references/fitts-law.md).
- You judge the number of choices in a menu or a step. Read [Hick's law](../../references/hicks-law.md).
- You judge how people move between the screens of the flow. Read [Navigation](../../references/navigation.md).
- The flow runs on a platform with its own conventions. Read [Platform conventions](../../references/platform-conventions.md).

Directives:

No directive of this step is in force.

Output: A list of findings for the flow, sorted by severity.

## Exit checklist

- [ ] Each finding names a directive of this skill or a heuristic, or a label marks it as an opinion.
- [ ] The report states that each severity comes from one reviewer and needs a second review.

## Output

A list of findings, sorted by severity. Each finding names the screen, the element, the heuristic or the directive that it breaks, its severity, and the change that you recommend. The severity scale is `0` for no problem, `1` for a cosmetic problem, `2` for a minor problem, `3` for a major problem, and `4` for a problem that blocks a release.
