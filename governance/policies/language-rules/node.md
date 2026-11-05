---
id: language-rules
kind: ka:Concept
title: Language rules
status: proposed
origin: template
knowledge_type: domain
sources:
  - governance/language/grammar.yaml
  - governance/language/vocabulary.yaml
broader:
  - governance
governs:
  - root
  - language-rules
---

## Definition

The controlled language of each directive, trigger, and skill description. The rules live in the grammar file, next to the checks that enforce them.

## Directives

- Write each directive, trigger, and skill description in the grammar of `governance/language/grammar.yaml`. ^follow-the-grammar
  - scope: node
  - status: proposed
  - origin: template
- Add each new opening verb to `governance/language/vocabulary.yaml` or to the branch file of the node. ^add-the-verb
  - scope: node
  - status: proposed
  - origin: template
