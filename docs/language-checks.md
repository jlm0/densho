# Language checks

> **In the library:** the copy editor. A book can sit on the right shelf and still have rules that nobody can apply the same way twice, so the editor checks how each sentence is written.

**Status:** Planned. Nothing on this page exists yet.

## What it does

This layer will check the text that agents act on:

- **Directives:** each one is a short, atomic rule in a fixed grammar.
- **Pointer triggers:** a trigger tells an agent when to follow a pointer, and it follows its own grammar.
- **Skill descriptions:** an agent reads a description to choose a skill, and each one has a length limit.

## How it works

The grammar and the vocabularies will live in `governance/language/`. The grammar starts from these rules:

- Write each rule as one sentence that ends with a period, in 20 words or fewer.
- Start each rule with a verb, `Do not`, `Prefer`, a condition, or a scope.
- Write one directive in each rule, with at most one condition and one `unless`.
- Do not use a modal, a hedge, or a vague qualifier such as `should`, `usually`, or `as needed`.
- Do not put a reason or an explanation in a rule. Supporting prose goes in the body of the node.
- Put each command, path, and literal value in backticks.

The grammar draws on ASD-STE100, a controlled language for technical writing. The checks will use part-of-speech tagging to read sentence structure, and each failure will point to its file and line.

## How it fits

Governance rules are directives too, so this layer will lint them the same way. That is what makes the system recursive: the rules for writing rules follow their own rules.

The checks judge form only. A rule can pass the grammar and still be a bad rule, so meaning stays a matter for review.

## Not settled yet

- The exact trigger grammar and the description limit
- How much of ASD-STE100 to adopt
- How vocabularies extend from a domain down to its branches
