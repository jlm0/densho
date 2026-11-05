# Governance workflow

> **In the library:** the acquisitions policy, which says who can add or change a book and how. Without it the library is tidy, but anyone can change anything.

**Status:** Planned. The `status` and `origin` fields exist in the [schema](schema.md#field-values). Nothing else on this page exists yet.

## What it does

This layer will set the lifecycle, approval, and change rules for knowledge, and it will add checks that enforce them.

## How it works

The policies will live in `governance/policies/`. They build on two fields that every node and directive already has:

| Field    | Values                               | Meaning                                                                        |
| -------- | ------------------------------------ | ------------------------------------------------------------------------------ |
| `status` | `proposed`, `accepted`, `deprecated` | Whether a reviewer approved the entity, or whether it stays only for reference |
| `origin` | `template`, `project`                | Whether the template or the project added the entity                           |

Domain knowledge and workspace knowledge share this one workflow, so a project governs its own knowledge the same way the template governs what it ships.

## How it fits

The other checks prove that knowledge is well formed. This layer decides whether it is allowed in. The policies are nodes and directives themselves, so they pass the same checks as everything they govern.

## Not settled yet

- Which changes need review, and who approves them
- How policy nodes in `governance/policies/` join the graph, because the parser reads only `knowledge/` and `skills/` today
- Whether agents can propose concepts or directives
- How experimental knowledge stays apart from authoritative knowledge
- How a change gets promoted from `proposed` to `accepted`
