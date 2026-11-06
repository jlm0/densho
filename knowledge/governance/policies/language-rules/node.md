---
id: language-rules
kind: ka:Concept
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

The controlled language of each directive, trigger, and skill description. The rules live in the grammar file, next to the checks that enforce them.

## Directives

- Write each directive, trigger, and skill description in the grammar of `knowledge/governance/language/grammar.yaml`. ^follow-the-grammar
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Add each new opening verb to `knowledge/governance/language/vocabulary.yaml` or to the branch file of the node. ^add-the-verb
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
