---
paths:
  - "knowledge/**/*"
  - "knowledge/governance/policies/node.md"
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Governance

## Directives

From [Governance](governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit

## Definition

The rules that set how knowledge enters the graph and how it changes. They cover domain knowledge and workspace knowledge alike, and they cover themselves.

## References

- You accept a change. Read [Approval](../../references/approval.md).
- You change an accepted entity. Read [Change rules](../../references/change-rules.md).
- You write a directive, a trigger, or a skill description. Read [Language rules](../../references/language-rules.md).
- You set the `status` of an entity. Read [Lifecycle](../../references/lifecycle.md).
- You change a node kind, a field, or an edge. Read [Schema rules](../../references/schema-rules.md).
