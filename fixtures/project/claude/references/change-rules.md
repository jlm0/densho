<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Change rules

## Directives

From [Governance](../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Run the same checks and the same review on workspace knowledge as on domain knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each staged file before each commit. ^run-checks-before-commit

From [Change rules](change-rules.md):

- Change only `status` on an entity in the commit that accepts it. ^accept-in-its-own-commit
- Set `status` to `proposed` when you change the text, the scope, the basis, or the attachments of an `accepted` directive. ^reopen-a-directive
- Set `status` to `proposed` when you change the definition, the kind, or an edge of an `accepted` node. ^reopen-a-node
- Set `status` to `proposed` when you change the invocation or a script of an `accepted` skill. ^reopen-a-skill
- Set `status` to `proposed` when you change the reason of an `accepted` exception. ^reopen-an-exception
- Keep `status` when you change only a title, a body, a pointer, a source, or a rejection reason. ^routes-need-no-review

## Definition

The rules that say which changes reopen a review. A change to what an agent is told, or to what a node means, reopens it. A change to a route or to supporting text does not.
