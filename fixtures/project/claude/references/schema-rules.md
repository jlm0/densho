<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Schema rules

## Directives

From [Governance](../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit

From [Schema rules](schema-rules.md):

- Change a node kind, a field, or an edge only in `knowledge/governance/schema/metamodel.yaml` of the template. ^change-the-schema-file
- Do not edit a file in `engine/generated/` by hand. ^keep-the-generated-files

## Definition

The rules for the metamodel, which defines what a node is. The metamodel file stays outside the graph, so this node names it as a source.
