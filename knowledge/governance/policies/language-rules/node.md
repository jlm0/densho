---
id: language-rules
kind: densho:Concept
title: Language rules
status: proposed
origin: template
knowledge_type: domain
sources:
  - knowledge/governance/language/grammar.yaml
  - knowledge/governance/language/vocabulary.yaml
broader:
  - governance
governs:
  - root
  - language-rules
---

## Definition

The controlled language of each directive, trigger, and skill description, and the rules for the sources of a directive. The grammar file holds the language rules, next to the checks that enforce them.

## Directives

- Write each directive, trigger, and skill description in the grammar of `knowledge/governance/language/grammar.yaml`. ^follow-the-grammar
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Write each directive as one sentence that gives exactly `1` action in each case. ^one-action-per-directive
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Write each other case as an `unless` clause or as a second directive with a condition. ^define-each-other-case
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Add each new opening verb to `knowledge/governance/language/vocabulary.yaml` or to the branch file of the node. ^add-the-verb
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Cite as the first source of a directive a source that states the rule alone. ^first-source-states-the-rule
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Set `basis` from the kind of the first source of the directive. ^basis-from-first-source
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Set `basis` to `judgment` only if you find no source that states the rule. ^judgment-only-without-a-source
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Add a section anchor or a page locator `#page=N` to each source that has one. ^locate-each-source
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- In a `#page=N` locator, give the PDF page that states the rule, not the printed page number. ^pdf-page-not-printed-page
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not state a fact, a ranking, or an example that the source does not state. ^no-unsourced-fact
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not write a rule whose direction the source does not support. ^source-supports-direction
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If the source names the case for another behavior, write that case as an `unless` clause or an alternative directive. ^source-case-as-condition
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If no source names the case for another behavior, give the alternative directive `basis: judgment`. ^judgment-for-an-unnamed-case
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
