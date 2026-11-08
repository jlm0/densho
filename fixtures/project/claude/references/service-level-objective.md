<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Service level objective

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

From [Service level objective](service-level-objective.md):

- Measure each SLO over a rolling window of `4` weeks. ^four-week-window
- Set the internal SLO of a service tighter than its published SLO. ^internal-slo-margin
- Measure latency at a percentile, not as a mean. ^latency-percentiles
- Do not set an SLO target of `100%`. ^no-perfect-slo
- Define each SLI as the ratio of good events to all events. ^sli-as-ratio
- Choose each SLI from what users experience, not from what is easy to measure. ^user-centered-sli

## Definition

A target value or range for a service level indicator (SLI). An SLI is a measure of one aspect of the service that users get, such as latency, the error rate, or availability. A service level agreement (SLA) is a contract that adds a consequence, such as a refund, when the service misses its SLO. A target with no consequence is an SLO, not an SLA.

## Notes

A mean hides the slow tail of a latency distribution. The `99th` percentile shows a likely worst case, and the `50th` percentile shows the typical case. Start with a loose target and tighten it over time, not with a strict target that you relax later.

## Comes from

The output of each node in this list is an input of this node.

- [Tracking plan](tracking-plan.md)

## Goes to

The output of this node is an input of each node in this list.

- [Error budget](error-budget.md)
