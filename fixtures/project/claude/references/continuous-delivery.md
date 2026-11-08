<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Continuous delivery

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

## Definition

A discipline in which a team builds software so that it can be released to production at any time. Martin Fowler names the signs: the software is deployable throughout its life, the team keeps it deployable before it works on new features, each change gets fast automated feedback on its readiness for production, and a push-button deployment sends any version to any environment. A deployment pipeline carries each change toward production.

## Comes from

The output of each node in this list is an input of this node.

- [Error budget](error-budget.md)

## Goes to

The output of this node is an input of each node in this list.

- [Observability](observability.md)
