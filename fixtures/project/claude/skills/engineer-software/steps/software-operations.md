<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software operations

This file is step 8 of 8 of the skill `engineer-software`.

## Directives

From [Error budget](../../../references/error-budget.md):

- When a service exceeds its error budget, release only `P0` and security fixes, unless its error budget policy differs. ^freeze-on-spent-budget
- Write a postmortem when an incident uses over `20%` of a `4`-week error budget, unless the error budget policy differs. ^postmortem-for-large-incident
- Write an error budget policy for each service with an SLO. ^write-error-budget-policy

From [Observability](../../../references/observability.md):

- Send a page only for a problem that needs human judgment at once. ^actionable-pages
- Make each alert detect a symptom that users see, not its cause, unless the cause is definite and imminent. ^alert-on-symptoms
- Monitor the latency, the traffic, the errors, and the saturation of each user-facing service. ^golden-signals
- Measure the latency of failed requests apart from the latency of successful requests. ^separate-error-latency

From [Postmortem](../../../references/postmortem.md):

- Do not name a person or a team as the cause of an incident in a postmortem. ^blameless-postmortem
- Record the impact, the actions, the root causes, and the follow-up actions in each postmortem. ^postmortem-contents
- Define the criteria for a postmortem before an incident occurs. ^postmortem-criteria
- Write a postmortem for each incident that loses data. ^postmortem-for-data-loss

From [Service level objective](../../../references/service-level-objective.md):

- Measure each SLO over a rolling window of `4` weeks. ^four-week-window
- Set the internal SLO of a service tighter than its published SLO. ^internal-slo-margin
- Measure latency at a percentile, not as a mean. ^latency-percentiles
- Do not set an SLO target of `100%`. ^no-perfect-slo
- Define each SLI as the ratio of good events to all events. ^sli-as-ratio
- Choose each SLI from what users experience, not from what is easy to measure. ^user-centered-sli

From [Software delivery metrics](../../../references/software-delivery-metrics.md):

- Measure the delivery metrics of one application or service at a time. ^measure-one-service-at-a-time
- Do not compare the delivery metrics of one team with the metrics of another team. ^no-team-comparison

## Inputs

- The accepted change and its version number

The output of each node in this list is an input of this step:

- [Software quality](software-quality.md)

## Procedure

The procedure of this step is missing.

## Output

The release of the change, and the monitoring and the running of the software in production.

The output of this step is an input of each node in this list:

- [Product measurement](../../../references/product-measurement.md)

## Exit gate

Check the release and the monitoring against each directive of this step and of the skill, and report each one that it misses.

## Next step

This step is the last step of the skill.

## References

- You release or deploy a change. Read [Continuous delivery](../../../references/continuous-delivery.md).
- You plan a release of a service that has an SLO. Read [Error budget](../../../references/error-budget.md).
- You add logs, metrics, or traces to a service. Read [Observability](../../../references/observability.md).
- You write the record of an incident. Read [Postmortem](../../../references/postmortem.md).
- You set a reliability target for a service. Read [Service level objective](../../../references/service-level-objective.md).
- You measure how a team delivers software. Read [Software delivery metrics](../../../references/software-delivery-metrics.md).
- You add or change a product analytics event. Read [Tracking plan](../../../references/tracking-plan.md).
