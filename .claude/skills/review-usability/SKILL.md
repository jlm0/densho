---
name: review-usability
description: "Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a person asks for a usability review of a flow."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review the usability of a flow

If compaction cuts this skill, invoke the skill again.

## Directives

No directive is in force at this node.

## Inputs

- The flow: its screens in the order of the task, as designs or a running interface
- The task, the users, and the target platform of the flow

## Procedure

1. Read each directive that this skill lists.
2. State the scope of the review: the users, the task, and the platform.
3. Go through the task once to learn the flow. Do not judge anything on this pass.
4. Go through the task a second time. On each screen, check each heuristic and each directive.
5. Check the size and the position of each target, and the number of choices at each step.
6. Write each finding with the screen, the element, the heuristic or the directive, and the change that you recommend.
7. Give each finding its severity, then sort the findings from the highest severity.

## Output

A list of findings, sorted by severity. Each finding names the screen, the element, the heuristic or the directive that it breaks, its severity, and the change that you recommend. The severity scale is `0` for no problem, `1` for a cosmetic problem, `2` for a minor problem, `3` for a major problem, and `4` for a problem that blocks a release.

## Validation

Each finding names a directive from the first step of the procedure or one of the ten heuristics. A finding with neither is an opinion, so label it as one. One reviewer gives a rough severity, so state that a second reviewer can change it.

## References

- You judge the size or the position of a target. Read [Fitts's law](../../references/fitts-law.md).
- You judge the number of choices in a menu or a step. Read [Hick's law](../../references/hicks-law.md).
- You judge how people move between the screens of the flow. Read [Navigation](../../references/navigation.md).
- The flow runs on a platform with its own conventions. Read [Platform conventions](../../references/platform-conventions.md).
- You judge the feedback, the exits, the confirmations, the error messages, or the help of the flow. Read [Usability heuristics](../../references/usability-heuristics.md).
