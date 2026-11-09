<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software operations

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

## Definition

The release, the monitoring, and the running of software in production. SWEBOK `v4` adds software engineering operations as a knowledge area. Reliability is one of its concerns: the ability of a service to do what its users expect, at the level that they expect, over time. Site reliability engineering, from Google, measures reliability against a target and uses the gap between the target and perfection to decide how fast the service changes.

## Notes

The four golden signals measure the time to serve a request, the demand on the service, the rate of failed requests, and how full the most constrained resource is. A problem that needs only a mechanical response gets automation, not a page.

## Comes from

The output of each node in this list is an input of this node.

- [Software quality](software-quality.md)

## Goes to

The output of this node is an input of each node in this list.

- [Product measurement](product-measurement.md)

## References

- You release or deploy a change. Read [Continuous delivery](continuous-delivery.md).
- You plan a release of a service that has an SLO. Read [Error budget](error-budget.md).
- You add logs, metrics, or traces to a service. Read [Observability](observability.md).
- You write the record of an incident. Read [Postmortem](postmortem.md).
- You set a reliability target for a service. Read [Service level objective](service-level-objective.md).
- You measure how a team delivers software. Read [Software delivery metrics](software-delivery-metrics.md).
- You add or change a product analytics event. Read [Tracking plan](tracking-plan.md).
