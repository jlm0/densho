---
id: postmortem
kind: densho:Concept
title: Postmortem
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://sre.google/sre-book/postmortem-culture/
broader:
  - software-reliability
---

## Definition

A written record of an incident: its impact, the actions that mitigated or resolved it, its root causes, and the follow-up actions that stop it from recurring. A blameless postmortem looks for the causes in the system and the process, and assumes that each person acted in good faith on the information that the person had.

## Directives

- Define the criteria for a postmortem before an incident occurs. ^postmortem-criteria
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/postmortem-culture/
- Write a postmortem for each incident that loses data. ^postmortem-for-data-loss
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/postmortem-culture/
- Record the impact, the actions, the root causes, and the follow-up actions in each postmortem. ^postmortem-contents
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/postmortem-culture/
- Do not name a person or a team as the cause of an incident in a postmortem. ^blameless-postmortem
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/sre-book/postmortem-culture/

## Notes

Other common triggers are downtime that users see beyond a threshold, an on-call action such as a rollback, a resolution time beyond a threshold, and an incident that monitoring did not detect.
