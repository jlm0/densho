<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Architecture decision record

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

From [Access control](access-control.md):

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
- Block access to each resource by default, unless the resource is public. ^deny-by-default

From [Software security](software-security.md):

- Do not put an API key or a session token in a URL. ^no-secret-in-url
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections

From [Injection](injection.md):

- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server

From [Architecture decision record](architecture-decision-record.md):

- Write the decision of a record in full sentences in the active voice. ^decision-in-active-voice
- Give each decision record a title, a context, a decision, a status, and its consequences. ^decision-record-sections
- Do not change the context, the decision, or the consequences of an accepted decision record. ^keep-accepted-records
- List each positive, negative, and neutral consequence in a decision record. ^list-each-consequence
- Mark a replaced decision record as superseded, with a link to its replacement. ^mark-superseded-record
- Set the status of a new decision record to `proposed`. ^new-record-is-proposed
- Give each decision record the next unused number. ^number-decision-records
- Record each decision that affects structure, non-functional characteristics, dependencies, interfaces, or construction techniques in a decision record in the repository. ^record-each-decision

## Definition

A short text file in the repository that records one architecturally significant decision with the forces behind it. Michael Nygard gave the format in 2011: a title, the context, the decision, the status, and the consequences. A later reader can then judge whether the decision still holds, and does not have to accept it blindly or reverse it blindly.

## Sections

| Section      | What it holds                                                                       |
| ------------ | ----------------------------------------------------------------------------------- |
| Title        | A short noun phrase that names the decision                                         |
| Context      | The forces at play, technical, political, social, and local, stated as facts        |
| Decision     | The response to those forces, in full sentences that start with "We will"           |
| Status       | `proposed`, `accepted`, `deprecated`, or `superseded`, with a link to a replacement |
| Consequences | Each result of the decision, positive, negative, and neutral                        |

A record is one or two pages long.

## Comes from

The output of each node in this list is an input of this node.

- [C4 model](c4-model.md)
