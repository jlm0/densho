<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Error budget

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

From [Software operations](software-operations.md):

- Send a page only for a problem that needs human judgment at once. ^actionable-pages
- Make each alert detect a symptom that users see, not its cause, unless the cause is definite and imminent. ^alert-on-symptoms
- Monitor the latency, the traffic, the errors, and the saturation of each user-facing service. ^golden-signals
- Measure the latency of failed requests apart from the latency of successful requests. ^separate-error-latency

From [Error budget](error-budget.md):

- When a service exceeds its error budget, release only fixes for `P0` issues and security fixes. ^freeze-on-spent-budget
- If one incident uses more than `20%` of the error budget in `4` weeks, write a postmortem for it. ^postmortem-for-large-incident
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
