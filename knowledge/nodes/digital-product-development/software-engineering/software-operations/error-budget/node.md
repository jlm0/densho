---
id: error-budget
kind: densho:Concept
title: Error budget
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://sre.google/sre-book/embracing-risk/
  - https://sre.google/workbook/error-budget-policy/
  - https://sre.google/workbook/implementing-slos/
broader:
  - software-operations
depends_on:
  - service-level-objective
informs:
  - postmortem
  - continuous-delivery
---

## Definition

The amount of unreliability that a service can have in a period and still meet its SLO. The budget is `100%` minus the SLO. An SLO of `99.9%` gives a budget of `0.1%` of requests in the window. While budget remains, a team releases changes. When the budget is spent, the team stops releases and puts its work into reliability.

## Directives

- Write an error budget policy for each service with an SLO. ^write-error-budget-policy
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/workbook/implementing-slos/
  - sources: https://sre.google/workbook/error-budget-policy/
- When a service exceeds its error budget, release only `P0` and security fixes, unless its error budget policy differs. ^freeze-on-spent-budget
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/workbook/error-budget-policy/#slo-miss-policy
- Write a postmortem when an incident uses over `20%` of a `4`-week error budget, unless the error budget policy differs. ^postmortem-for-large-incident
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://sre.google/workbook/error-budget-policy/#outage-policy

## Notes

The policy names the actions when the budget is spent, who takes them, and the escalation path for a disagreement. Product, development, and the team that runs production approve it. The freeze ends when the service is back within its SLO.
