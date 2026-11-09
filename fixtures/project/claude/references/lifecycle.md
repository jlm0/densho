<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Lifecycle

## Directives

From [Governance](../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Run the same checks and the same review on workspace knowledge as on domain knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each staged file before each commit. ^run-checks-before-commit

From [Lifecycle](lifecycle.md):

- Before you remove an `accepted` node or directive, set its `status` to `deprecated`. ^deprecate-before-removing
- Do not apply a `deprecated` node or directive to new work. ^deprecated-is-for-reference
- Keep the `id` of a node or a directive when you move its file. ^keep-the-id
- Do not change the `origin` of a node or a directive. ^keep-the-origin
- Before you deprecate a node, move the nodes under it. ^move-before-deprecating
- Follow a directive while its exception stays `proposed`. ^proposed-exception-stops-nothing
- Treat a `proposed` directive as a draft, not as a rule, unless a person stated it in the current session. ^proposed-is-a-draft
- Before you reject a node, leave no `proposed` or `accepted` directive or exception in it. ^reject-the-contents
- Do not apply a `rejected` node or directive to any work. ^rejected-applies-nowhere
- Before you reject an entity, remove each reference to it from the entities that are not `rejected`. ^remove-references-before-rejecting
- Set `status` to `proposed` on each new node, directive, and exception. ^start-as-proposed
- Set `rejection_reason` on each `rejected` node, directive, and exception. ^state-the-rejection-reason
- Set `origin` to `project` on each entity in workspace knowledge. ^workspace-is-project

## Definition

The states of a node, a directive, or an exception. `proposed` means that an author recommends it and no reviewer approved it. `accepted` means that a reviewer approved this content. `deprecated` means that it stays only for reference. `rejected` means that a person rejected the proposal. A rejected entity is not in force, and no generated file holds it.
