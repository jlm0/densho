<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Language rules

## Directives

From [Governance](../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit

From [Language rules](language-rules.md):

- Add each new opening verb to `knowledge/governance/language/vocabulary.yaml` or to the branch file of the node. ^add-the-verb
- Write each other case as an `unless` clause or as a second directive with a condition. ^define-each-other-case
- Write each directive, trigger, and skill description in the grammar of `knowledge/governance/language/grammar.yaml`. ^follow-the-grammar
- Write each directive as one sentence that gives exactly `1` action in each case. ^one-action-per-directive

## Definition

The controlled language of each directive, trigger, and skill description. The rules live in the grammar file, next to the checks that enforce them.
