<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Language rules

## Directives

From [Governance](../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Run the same checks and the same review on workspace knowledge as on domain knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each staged file before each commit. ^run-checks-before-commit

From [Language rules](language-rules.md):

- Add each new opening verb to `knowledge/governance/language/vocabulary.yaml` or to the branch file of the node. ^add-the-verb
- Set `basis` from the kind of the first source of the directive. ^basis-from-first-source
- Write each other case as an `unless` clause or as a second directive with a condition. ^define-each-other-case
- Cite as the first source of a directive a source that states the rule alone. ^first-source-states-the-rule
- Write each directive, trigger, and skill description in the grammar of `knowledge/governance/language/grammar.yaml`. ^follow-the-grammar
- If no source names the case for another behavior, give the alternative directive `basis: judgment`. ^judgment-for-an-unnamed-case
- Set `basis` to `judgment` only if you find no source that states the rule. ^judgment-only-without-a-source
- Add a section anchor or a page locator `#page=N` to each source that has one. ^locate-each-source
- Do not state a fact, a ranking, or an example that the source does not state. ^no-unsourced-fact
- Write each directive as one sentence that gives exactly `1` action in each case. ^one-action-per-directive
- In a `#page=N` locator, give the PDF page that states the rule, not the printed page number. ^pdf-page-not-printed-page
- If the source names the case for another behavior, write that case as an `unless` clause or an alternative directive. ^source-case-as-condition
- Do not write a rule whose direction the source does not support. ^source-supports-direction

## Definition

The controlled language of each directive, trigger, and skill description, and the rules for the sources of a directive. The grammar file holds the language rules, next to the checks that enforce them.
