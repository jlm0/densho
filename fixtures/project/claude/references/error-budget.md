<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Error budget

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Error budget](error-budget.md):

- When a service exceeds its error budget, release only `P0` and security fixes, unless its error budget policy differs. ^freeze-on-spent-budget
- Write a postmortem when an incident uses over `20%` of a `4`-week error budget, unless the error budget policy differs. ^postmortem-for-large-incident
- Write an error budget policy for each service with an SLO. ^write-error-budget-policy

## Definition

The amount of unreliability that a service can have in a period and still meet its SLO. The budget is `100%` minus the SLO. An SLO of `99.9%` gives a budget of `0.1%` of requests in the window. While budget remains, a team releases changes. When the budget is spent, the team stops releases and puts its work into reliability.

## Notes

The policy names the actions when the budget is spent, who takes them, and the escalation path for a disagreement. Product, development, and the team that runs production approve it. The freeze ends when the service is back within its SLO.

## Comes from

The output of each node in this list is an input of this node.

- [Service level objective](service-level-objective.md)

## Goes to

The output of this node is an input of each node in this list.

- [Continuous delivery](continuous-delivery.md)
- [Postmortem](postmortem.md)
