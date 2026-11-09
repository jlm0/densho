---
id: review-usability
kind: densho:Skill
title: Review the usability of a flow
status: proposed
origin: template
knowledge_type: domain
description: "Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a person asks for a usability review of a flow. Do not use it for a whole interface (`review-interface`) or an accessibility check (`audit-accessibility`)."
invocation: agent
skill_type: lens
uses:
  - usability-heuristics
  - fitts-law
  - hicks-law
  - navigation
  - platform-conventions
steps:
  - review-the-flow
---

## Directives

- Give each finding a severity from `0` to `4`. ^rate-finding-severity
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/

## Exit checklist

- [ ] Each finding names a directive of this skill or a heuristic, or a label marks it as an opinion.
- [ ] The report states that each severity comes from one reviewer and needs a second review.

## Output

A list of findings, sorted by severity. Each finding names the screen, the element, the heuristic or the directive that it breaks, its severity, and the change that you recommend. The severity scale is `0` for no problem, `1` for a cosmetic problem, `2` for a minor problem, `3` for a major problem, and `4` for a problem that blocks a release.
