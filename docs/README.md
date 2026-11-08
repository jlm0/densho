# Overview

Agent instructions usually live in long prose files that repeat themselves, are hard to apply consistently, and get no automated checks. Governed knowledge treats that material like code. Each piece of knowledge is a small file with a stable ID and a declared place in a graph, and each rule is one short sentence in a restricted grammar. Automated checks refuse anything that breaks the structure, language, or change rules, and the rules for writing rules pass those same checks.

The goal is one source of truth that people can read and review, that agents load piece by piece as a task needs it, and that any project can copy and make its own. It can't make a model obey, but it does control what the agent can find and how it finds it.

## The library

Think of the system as a library, where each node is a book. The first two layers define and read one book. The next four make the library trustworthy, one stocks it, the next five deliver it to agents, projects, and people, and the last two bring back what they learn and test whether it helps.

| Layer                                                           | In the library                                | Status |
| --------------------------------------------------------------- | --------------------------------------------- | ------ |
| [Schema](schema.md)                                             | The design of the catalog card                | Built  |
| [Node format](node-format.md)                                   | The scanner that rejects a badly filled card  | Built  |
| [Graph checks](graph-checks.md)                                 | The walk through the whole building           | Built  |
| [Language checks](language-checks.md)                           | The copy editor                               | Built  |
| [Directive semantics](directive-semantics.md)                   | The rules about which signs cover which rooms | Built  |
| [Governance workflow](governance-workflow.md)                   | The acquisitions policy                       | Built  |
| [Seed knowledge](seed-knowledge.md)                             | The first real books                          | Built  |
| [Compiled outputs](compiled-outputs.md)                         | The printed catalog                           | Built  |
| [Runtime files](runtime-files.md)                               | The signs that lead visitors to the shelf     | Built  |
| [Template packaging](template-packaging.md)                     | The library in a box                          | Built  |
| [Migration and reconciliation](migration-and-reconciliation.md) | The moving crew                               | Built  |
| [Human interface](human-interface.md)                           | The reading room                              | Built  |
| [Improvement loop](improvement-loop.md)                         | The suggestion box                            | Built  |
| [Evaluation](evaluation.md)                                     | The reader test                               | Built  |

Each page explains how to use what exists today, and ends with what it does not check yet.

## Terms

| Term      | In the library                                  | What it is                                                     |
| --------- | ----------------------------------------------- | -------------------------------------------------------------- |
| Node      | A book                                          | One Markdown file of knowledge                                 |
| Pointer   | A "see also" note that says when to go there    | A route to another node, with the trigger for following it     |
| Directive | A sign with one house rule                      | One short instruction with its own ID                          |
| Skill     | A reading list for one job                      | A reusable workflow that loads the directives of its knowledge |
| Step      | One stop on the reading list                    | One practice area of a flow skill, in its own file             |
| Agent     | A visitor who goes only where the signs lead it | The AI tool that does the work                                 |

## Commands

| Command                                | What it does                               | Page                                          |
| -------------------------------------- | ------------------------------------------ | --------------------------------------------- |
| `uv run pre-commit run --all-files`    | Runs every check on every file             |                                               |
| `uv run densho parse knowledge`        | Parses each node                           | [Node format](node-format.md)                 |
| `uv run densho graph`                  | Checks the whole graph                     | [Graph checks](graph-checks.md)               |
| `uv run densho language`               | Checks the language of the text            | [Language checks](language-checks.md)         |
| `uv run densho directives`             | Checks which directives apply where        | [Directive semantics](directive-semantics.md) |
| `uv run densho governance`             | Checks the lifecycle and each change       | [Governance workflow](governance-workflow.md) |
| `uv run densho governance --pending`   | Lists what waits for review                | [Governance workflow](governance-workflow.md) |
| `uv run densho build`                  | Runs the checks, then compiles             | [Compiled outputs](compiled-outputs.md)       |
| `uv run densho build --proposals`      | Compiles what acceptance would add         | [Compiled outputs](compiled-outputs.md)       |
| `uv run densho runtime`                | Writes the files an agent tool loads       | [Runtime files](runtime-files.md)             |
| `uv run densho runtime --proposals`    | Writes a review copy of those files        | [Runtime files](runtime-files.md)             |
| `uv run densho view`                   | Writes a site for people to read           | [Human interface](human-interface.md)         |
| `uv run densho accept`                 | Sets what a person approves to `accepted`  | [Human interface](human-interface.md)         |
| `uv run densho adopt`                  | Takes in template knowledge                | [Template packaging](template-packaging.md)   |
| `uv run densho select`                 | Removes the disciplines a project left out | [Template packaging](template-packaging.md)   |
| `uv run densho history`                | Records template changes for agents        | [Template packaging](template-packaging.md)   |
| `uv run densho history --drift`        | Lists differences from the history         | [Template packaging](template-packaging.md)   |
| `uv run python fixtures/generate.py`   | Writes the fixture project                 | [Template packaging](template-packaging.md)   |
| `uv run densho eval --check`           | Grades the known outputs of the eval tasks | [Evaluation](evaluation.md)                   |
| `uv run densho eval --discipline <id>` | Runs the eval tasks with and without it    | [Evaluation](evaluation.md)                   |
| `uv run pytest`                        | Runs the tests                             |                                               |
| `uv run pyright`                       | Checks types in strict mode                |                                               |
| `uv run ruff check`                    | Lints the Python code                      |                                               |
| `uv run ruff format`                   | Formats the Python code                    |                                               |

In a project, `knowledge/.densho/densho` takes the place of `uv run densho`.

In this repo, the git hook runs these checks on each commit: file hygiene, the lock file, the engine constraints, the schema lint, the generated models, the knowledge nodes, the graph checks, the directive checks, the governance checks, the language checks, the compiled outputs, the runtime files, the template history, the fixture project, the eval tasks, Ruff lint and format, Markdown format, Pyright, and the tests. [A project runs fewer](template-packaging.md#the-git-hook).

## Where the code lives

| Path under `engine/` | What it does                                                                            |
| -------------------- | --------------------------------------------------------------------------------------- |
| `layout.py`          | Names the path of each source folder under `knowledge/`                                 |
| `schema/`            | The schema lint settings and the model template. A project doesn't receive them.        |
| `generated/`         | Models and shapes generated from the schema. Do not edit them.                          |
| `parser/`            | Reads `node.md` files into the models, with line numbers                                |
| `graph/`             | Checks the structure of the whole graph                                                 |
| `language/`          | Checks directives, triggers, and skill descriptions                                     |
| `directives/`        | Works out which directives apply at each node, and checks the result                    |
| `governance/`        | Checks the lifecycle, and compares each change with the last commit                     |
| `compiler/`          | Compiles the checked graph to JSON and RDF, with digests                                |
| `runtime/`           | Generates the files that an agent tool loads                                            |
| `template/`          | Takes in template knowledge, applies the choice of disciplines, and records the history |
| `interface/`         | Writes the site for people, and accepts what a person approves                          |
| `evaluation/`        | Grades the eval tasks, and runs them with and without the knowledge of a discipline     |
| `vendor/`            | A third-party linter, kept unchanged with its license                                   |
