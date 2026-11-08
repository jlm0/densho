<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Postmortem

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

From [Postmortem](postmortem.md):

- Do not name a person or a team as the cause of an incident in a postmortem. ^blameless-postmortem
- Record the impact, the actions, the root causes, and the follow-up actions in each postmortem. ^postmortem-contents
- Define the criteria for a postmortem before an incident occurs. ^postmortem-criteria
- Write a postmortem for each incident that loses data. ^postmortem-for-data-loss

## Definition

A written record of an incident: its impact, the actions that mitigated or resolved it, its root causes, and the follow-up actions that stop it from recurring. A blameless postmortem looks for the causes in the system and the process, and assumes that each person acted in good faith on the information that the person had.

## Notes

Other common triggers are downtime that users see beyond a threshold, an on-call action such as a rollback, a resolution time beyond a threshold, and an incident that monitoring did not detect.

## Comes from

The output of each node in this list is an input of this node.

- [Error budget](error-budget.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software delivery metrics](software-delivery-metrics.md)
