---
id: review-usability
kind: ka:Skill
title: Review the usability of a flow
status: proposed
origin: template
knowledge_type: domain
description: Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a flow is ready for a usability review.
invocation: agent
uses:
  - usability-heuristics
  - fitts-law
  - hicks-law
  - navigation
  - platform-conventions
pointers:
  - kind: ka:TextPointer
    target: usability-heuristics
    trigger: You judge the feedback, the exits, the confirmations, the error messages, or the help of the flow.
  - kind: ka:TextPointer
    target: fitts-law
    trigger: You judge the size or the position of a target.
  - kind: ka:TextPointer
    target: hicks-law
    trigger: You judge the number of choices in a menu or a step.
  - kind: ka:TextPointer
    target: navigation
    trigger: You judge how people move between the screens of the flow.
  - kind: ka:TextPointer
    target: platform-conventions
    trigger: The flow runs on a platform with its own conventions.
---

## Directives

- Give each finding a severity from `0` to `4`. ^rate-finding-severity
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/

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
