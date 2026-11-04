# Knowledge architecture

A template for a governed knowledge architecture that humans and agents share.

Knowledge lives in a tree of Markdown files that runs from domain to discipline to practice area to concept. Each file is a node. It holds concepts, directives, and links to other nodes. A governance layer sets what a node can contain, how a directive is written, and how knowledge changes. The governance is written in its own grammar and follows its own rules, so the checks that lint a knowledge node lint the governance too.

A build generates `AGENTS.md` from the tree as its root node. Agent tools such as Claude Code load it at the start of each session and follow the tree from there.

The repo is early. The schema and the node parser are in place. The directive grammar, the governance checks, and the build that generates `AGENTS.md` and the skills are not built yet.

## Setup

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.14 if your machine does not have it.

```sh
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

`uv sync` installs the locked environment. `pre-commit install` adds a git hook that runs every check on each commit. The last command runs every check once.

## Structure

| Path                                       | Contents                                                           |
| ------------------------------------------ | ------------------------------------------------------------------ |
| `governance/schema/`                       | The metamodel: node kinds, relationship kinds, and required fields |
| `governance/language/`                     | The directive grammar and the vocabularies                         |
| `governance/policies/`                     | Lifecycle, approval, and change rules                              |
| `knowledge/`                               | The knowledge nodes: concepts and directives                       |
| `skills/`                                  | Skill sources built from the knowledge tree                        |
| `engine/knowledge_architecture/`           | The Python engine: validators, compiler, resolver, and packager    |
| `engine/knowledge_architecture/generated/` | Python models generated from the schema. Do not edit them.         |
| `engine/knowledge_architecture/parser/`    | Reads `node.md` files into the models, with line numbers           |
| `tests/`                                   | Tests for the engine                                               |
| `build/`                                   | Generated output. Git ignores it.                                  |

## Usage

### Start a project from the template

Copy the template into the project once. From then on the project owns its copy. It adds workspace knowledge about its own code and can change anything it received. Drift from the template is expected.

The template holds two kinds of knowledge under one governance:

- Domain knowledge is universal and ships with the template.
- Workspace knowledge belongs to one project and is written there.

### Write a node

Each node is one file with the name `node.md`, in its own folder. The root node is `knowledge/node.md`. Other knowledge nodes go under `knowledge/`, and skills go under `skills/`. The folder path is only for navigation. Identity and relationships come from `id` and the edges, so a file can move without changing what it means. Any other Markdown file, and any symbolic link, in these folders is an error.

```markdown
---
id: test-driven-development
kind: ka:Concept
title: Test-driven development
status: accepted
origin: template
knowledge_type: domain
broader: [software-testing]
pointers:
  - kind: ka:PathPointer
    target: pytest-usage
    trigger: You edit a test file.
    paths: ["tests/**"]
---

## Definition

Write a failing test first, then the code that passes it.

## Directives

- Write a failing test before you change behavior. ^write-test-first
  - scope: subtree
  - status: accepted
  - origin: template
  - sources: https://example.com/testing

## References

Any other text is the body of the node.
```

The front matter holds every field except the definition, the directives, and the body, which live in the Markdown. It accepts plain YAML only: no tags, anchors, aliases, or merge keys.

The sections come in this order: `## Definition`, `## Directives`, then any other text. A line that looks like a section name but is not that exact top-level heading is an error, so a directive cannot turn into prose by accident. For the same reason, the parser rejects an unclosed code fence, a code fence that holds a section name the file does not otherwise have, raw HTML blocks, HTML comments, and control characters.

Each directive is one bullet of one line that ends with a space and `^id`. The directive text is Markdown. Its other fields are sub-bullets, one `key: value` each. Repeat a key to add another value to a list field such as `sources`. A value is plain text, so put one that holds Markdown syntax in backticks, for example `` sources: `tests/**/x*` ``.

To check every node:

```sh
uv run python -m knowledge_architecture.parser knowledge skills
```

Each problem prints as `path:line: code: message`. The parser checks each file on its own. It does not yet check that a reference such as `broader` names a node that exists. An unknown `kind` stops the field checks for that file, because the kind sets which fields apply.

### Change the schema

`governance/schema/metamodel.yaml` is the one source for what can exist in the graph: node kinds, edges, pointers, directives, and their required fields. After you edit it, regenerate the Python models:

```sh
uv run pre-commit run schema-models --all-files
```

The command rewrites the models and reports a failure when they changed. Stage the new models and run it again. The git hook runs the same step on each commit, so a schema change cannot land without its models, and a hand edit to the models does not survive.

### Run the checks

| Command                             | What it does                   |
| ----------------------------------- | ------------------------------ |
| `uv run pre-commit run --all-files` | Runs every check on every file |
| `uv run pytest`                     | Runs the tests                 |
| `uv run pyright`                    | Checks types in strict mode    |
| `uv run ruff check`                 | Lints the Python code          |
| `uv run ruff format`                | Formats the Python code        |

The git hook runs these checks on each commit: file hygiene, the lock file, the schema lint, the generated models, the knowledge nodes, Ruff lint and format, Markdown format, Pyright, and the tests.
