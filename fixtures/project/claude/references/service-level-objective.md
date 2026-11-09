<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Service level objective

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

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

## Goes to

The output of this node is an input of each node in this list.

- [Error budget](error-budget.md)
