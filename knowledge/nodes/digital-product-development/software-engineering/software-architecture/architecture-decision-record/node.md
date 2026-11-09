---
id: architecture-decision-record
kind: densho:Concept
title: Architecture decision record
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
broader:
  - software-architecture
---

## Definition

A short text file in the repository that records one architecturally significant decision with the forces behind it. Michael Nygard gave the format in 2011: a title, the context, the decision, the status, and the consequences. A later reader can then judge whether the decision still holds, and does not have to accept it blindly or reverse it blindly.

## Directives

- Record each decision that affects structure, non-functional characteristics, dependencies, interfaces, or construction techniques in a decision record in the repository. ^record-each-decision
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions#decision
- Give each decision record the next unused number. ^number-decision-records
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Give each decision record a title, a context, a decision, a status, and its consequences. ^decision-record-sections
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- List each positive, negative, and neutral consequence in a decision record. ^list-each-consequence
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Write the decision of a record in full sentences in the active voice. ^decision-in-active-voice
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Do not change the context, the decision, or the consequences of an accepted decision record. ^keep-accepted-records
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Mark a replaced decision record as superseded, with a link to its replacement. ^mark-superseded-record
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Set the status of a new decision record to `proposed`. ^new-record-is-proposed
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions

## Sections

| Section      | What it holds                                                                       |
| ------------ | ----------------------------------------------------------------------------------- |
| Title        | A short noun phrase that names the decision                                         |
| Context      | The forces at play, technical, political, social, and local, stated as facts        |
| Decision     | The response to those forces, in full sentences that start with "We will"           |
| Status       | `proposed`, `accepted`, `deprecated`, or `superseded`, with a link to a replacement |
| Consequences | Each result of the decision, positive, negative, and neutral                        |

A record is one or two pages long.
