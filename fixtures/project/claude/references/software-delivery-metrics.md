<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software delivery metrics

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

From [Software delivery metrics](software-delivery-metrics.md):

- Measure the delivery metrics of one application or service at a time. ^measure-one-service-at-a-time
- Do not compare the delivery metrics of one team with the metrics of another team. ^no-team-comparison

## Definition

The five measures of software delivery performance from the DORA research program. Change lead time, deployment frequency, and failed deployment recovery time measure throughput. Change fail rate and deployment rework rate measure instability.

## Metrics

| Metric                          | What it measures                                                        |
| ------------------------------- | ----------------------------------------------------------------------- |
| Change lead time                | The time from a commit to the change running in production              |
| Deployment frequency            | How often a team deploys                                                |
| Failed deployment recovery time | The time to recover from a deployment that needs immediate intervention |
| Change fail rate                | The share of deployments that need a rollback or a hotfix               |
| Deployment rework rate          | The share of deployments that are unplanned and that an incident causes |

DORA warns that a metric used as a target invites gaming. A team uses the metrics together to track its own improvement over time.

## Comes from

The output of each node in this list is an input of this node.

- [Postmortem](postmortem.md)
