<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software architecture

This file is step 2 of 8 of the skill `engineer-software`.

## Directives

From [Architecture decision record](../../../references/architecture-decision-record.md):

- Write the decision of a record in full sentences in the active voice. ^decision-in-active-voice
- Give each decision record a title, a context, a decision, a status, and its consequences. ^decision-record-sections
- Do not change the context, the decision, or the consequences of an accepted decision record. ^keep-accepted-records
- List each positive, negative, and neutral consequence in a decision record. ^list-each-consequence
- Mark a replaced decision record as superseded, with a link to its replacement. ^mark-superseded-record
- Set the status of a new decision record to `proposed`. ^new-record-is-proposed
- Give each decision record the next unused number. ^number-decision-records
- Record each architecturally significant decision in a decision record in the repository. ^record-each-decision

From [C4 model](../../../references/c4-model.md):

- Give each architecture diagram a key for its shapes, colors, borders, and lines. ^diagram-key
- Give each architecture diagram a title that states its type and its scope. ^diagram-title
- Label each element of an architecture diagram with its type and a short description. ^label-diagram-elements
- Label each line in an architecture diagram with the purpose of its relationship. ^label-diagram-lines
- Name the technology of each container and each component in an architecture diagram. ^name-diagram-technology

## Inputs

- The requirements of the change
- The decisions about the structure of the system, and each option that the person considered
- The forces on each decision: the requirements, the constraints, and the quality goals
- The decision records that the repository already holds

The output of each node in this list is an input of this step:

- [Software requirements](software-requirements.md)

## Procedure

1. For each decision about the structure of the system, write a decision record with procedure steps 2 to 7.
2. Find the folder and the format of the decision records in the repository. If the repository has none, ask the person where to keep them.
3. Give the record the next unused number and a title that names the decision.
4. Write the context: the forces that bear on the decision, stated as facts.
5. Write the decision in full sentences in the active voice.
6. List each consequence of the decision: positive, negative, and neutral.
7. If the decision replaces an earlier decision, mark the earlier record as superseded and link it to the new record.

The rest of the procedure of this step is missing.

## Output

The structure of the system: its parts, the responsibilities of each part, and the relationships between them. One decision record for each decision that sets the structure. Each record that a decision replaces carries the superseded status and a link to the new record.

The output of this step is an input of each node in this list:

- [Software design](software-design.md)

## Exit gate

Check the output against each directive of this step and of the skill, and report each one that it misses. A reader who did not take part in a decision can state the decision and its main reason from its record alone.

## Next step

Read [Software design](software-design.md).

## References

- You make or change a decision about the structure of a system. Read [Architecture decision record](../../../references/architecture-decision-record.md).
- You choose between one deployable unit and a set of services. Read [Architecture style](../../../references/architecture-style.md).
- You draw or update a diagram of the structure of a system. Read [C4 model](../../../references/c4-model.md).
- You connect two applications or two services. Read [Integration style](../../../references/integration-style.md).
