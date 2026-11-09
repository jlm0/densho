<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Observability

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Observability](observability.md):

- Send a page only for a problem that needs human judgment at once. ^actionable-pages
- Make each alert detect a symptom that users see, not its cause, unless the cause is definite and imminent. ^alert-on-symptoms
- Monitor the latency, the traffic, the errors, and the saturation of each user-facing service. ^golden-signals
- Measure the latency of failed requests apart from the latency of successful requests. ^separate-error-latency

## Definition

The ability to understand a system from the outside, by asking questions about it without knowing its inner workings. OpenTelemetry makes a system observable through instrumentation: the code emits signals such as traces, metrics, and logs. A trace is the path of a request through an application, and a metric is a measurement captured at runtime.

## Comes from

The output of each node in this list is an input of this node.

- [Continuous delivery](continuous-delivery.md)

## Goes to

The output of this node is an input of each node in this list.

- [Tracking plan](tracking-plan.md)
