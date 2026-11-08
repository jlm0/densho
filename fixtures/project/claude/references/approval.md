<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Approval

## Directives

From [Governance](../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit

From [Approval](approval.md):

- Run the engine with `governance --pending` to list each proposal. ^list-the-proposals
- Do not set `status` to `accepted` unless a person approves the change. ^person-accepts
- Do not set `status` to `deprecated` unless a person approves the change. ^person-deprecates
- Do not set `status` to `rejected` unless a person rejects the proposal. ^person-rejects
- Read the reason of each exception before you accept it. ^read-the-reason
- Run the engine with `directives --at` on the node before you accept a directive. ^read-what-applies

## Definition

The step that takes knowledge from a proposal to a rule. An agent can propose a concept, a directive, or an exception. A person approves it or rejects it.
