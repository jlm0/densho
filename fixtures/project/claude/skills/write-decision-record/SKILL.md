---
name: write-decision-record
description: "Write an architecture decision record for one decision. Use when you make or change a decision about the structure of a system."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Write a decision record

If compaction cuts this skill, invoke the skill again.

## Directives

From [Digital product development](../../references/digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Software engineering](../../references/software-engineering.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret
- Write a test for each change in behavior. ^test-each-behavior-change

From [Access control](../../references/access-control.md):

- Check each access control rule in server-side code, not in the client. ^check-access-on-server
- Block access to each resource by default, unless the resource is public. ^deny-by-default

From [Software security](../../references/software-security.md):

- Do not put an API key or a session token in a URL. ^no-secret-in-url
- Use TLS for each connection between a client and an external service. ^tls-for-external-connections

From [Secrets management](../../references/secrets-management.md):

- Store each backend secret in a secrets manager, such as a key vault. ^use-a-secrets-manager

From [Injection](../../references/injection.md):

- Validate each input on the server against an allow list of values, patterns, or ranges. ^validate-input-on-server

From [Architecture decision record](../../references/architecture-decision-record.md):

- Write the decision of a record in full sentences in the active voice. ^decision-in-active-voice
- Give each decision record a title, a context, a decision, a status, and its consequences. ^decision-record-sections
- Do not change the context, the decision, or the consequences of an accepted decision record. ^keep-accepted-records
- List each positive, negative, and neutral consequence in a decision record. ^list-each-consequence
- Mark a replaced decision record as superseded, with a link to its replacement. ^mark-superseded-record
- Give each decision record the next unused number. ^number-decision-records
- Record each architecturally significant decision in a decision record in the repository. ^record-each-decision

From [Write a decision record](SKILL.md):

- Set the status of a new decision record to `proposed`. ^new-record-is-proposed

## Inputs

- The decision, and each option that the person considered
- The forces on the decision: the requirements, the constraints, and the quality goals
- The decision records that the repository already holds

## Procedure

1. Read each directive that this skill lists.
2. Find the folder and the format of the decision records in the repository. If the repository has none, ask the person where to keep them.
3. Give the record the next unused number and a title that names the decision.
4. Write the context: the forces that bear on the decision, stated as facts.
5. Write the decision in full sentences in the active voice.
6. List each consequence of the decision: positive, negative, and neutral.
7. If the decision replaces an earlier decision, mark the earlier record as superseded and link it to the new record.

## Output

One decision record file. Each record that the decision replaces carries the superseded status and a link to the new record.

## Validation

Check the record against each directive from the first step of the procedure, and report each one it misses. A reader who did not take part in the decision can state the decision and its main reason from the record alone.

## References

- You choose the sections, the number, or the status of the record. Read [Architecture decision record](../../references/architecture-decision-record.md).
