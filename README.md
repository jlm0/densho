# Knowledge architecture

A template for a governed knowledge architecture that humans and agents share.

Knowledge lives in a tree of Markdown files that runs from domain to discipline to practice area to concept. Each file is a node. It holds concepts, directives, and links to other nodes. A governance layer sets what a node can contain, how a directive is written, and how knowledge changes. The governance is written in its own grammar and follows its own rules, so the checks that lint a knowledge node lint the governance too.

A build generates `AGENTS.md` from the tree as its root node. Agent tools such as Claude Code load it at the start of each session and follow the tree from there.

The repo is early. The schema, the node parser, the graph checks, the language checks, the directive semantics, the governance workflow, the seed knowledge, and the compiled outputs are in place. The build that generates `AGENTS.md` and the skills is not built yet.

## Setup

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.14 if your machine does not have it.

```sh
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

`uv sync` installs the locked environment. `pre-commit install` adds a git hook that runs every check on each commit. The last command runs every check once.

## Structure

| Path                                        | Contents                                                             |
| ------------------------------------------- | -------------------------------------------------------------------- |
| `governance/schema/`                        | The metamodel: node kinds, relationship kinds, and required fields   |
| `governance/language/`                      | The directive grammar and the vocabularies                           |
| `governance/policies/`                      | Lifecycle, approval, and change rules, written as nodes              |
| `knowledge/`                                | The knowledge nodes: concepts and directives                         |
| `skills/`                                   | Skill sources built from the knowledge tree                          |
| `engine/knowledge_architecture/`            | The Python engine: validators, compiler, and packager                |
| `engine/knowledge_architecture/generated/`  | Models and shapes generated from the schema. Do not edit them.       |
| `engine/knowledge_architecture/parser/`     | Reads `node.md` files into the models, with line numbers             |
| `engine/knowledge_architecture/graph/`      | Checks the structure of the whole graph                              |
| `engine/knowledge_architecture/language/`   | Checks directives, triggers, and skill descriptions                  |
| `engine/knowledge_architecture/directives/` | Works out which directives apply at each node, and checks the result |
| `engine/knowledge_architecture/governance/` | Checks the lifecycle, and compares each change with the last commit  |
| `engine/knowledge_architecture/compiler/`   | Compiles the checked graph to JSON and RDF, with digests             |
| `engine/knowledge_architecture/vendor/`     | A third-party linter, kept unchanged with its license                |
| `tests/`                                    | Tests for the engine                                                 |
| `docs/`                                     | The overview and a page for each layer                               |
| `build/`                                    | Generated output. Git ignores it.                                    |

## Docs

Start with the [overview](docs/README.md). It explains the system as a library and links to a page for each layer, built or planned.

## Usage

### Start a project from the template

Copy the template into the project once. From then on the project owns its copy. It adds workspace knowledge about its own code and can change anything it received. Drift from the template is expected.

The template holds two kinds of knowledge under one governance:

- Domain knowledge is universal and ships with the template.
- Workspace knowledge belongs to one project and is written there.

### Run the checks

| Command                                       | What it does                         |
| --------------------------------------------- | ------------------------------------ |
| `uv run pre-commit run --all-files`           | Runs every check on every file       |
| `uv run ka parse knowledge skills governance` | Parses each node                     |
| `uv run ka graph`                             | Checks the whole graph               |
| `uv run ka language`                          | Checks the language of the text      |
| `uv run ka directives`                        | Checks which directives apply where  |
| `uv run ka governance`                        | Checks the lifecycle and each change |
| `uv run ka governance --pending`              | Lists what waits for review          |
| `uv run ka build`                             | Runs the checks, then compiles       |
| `uv run ka build --proposals`                 | Compiles what acceptance would add   |
| `uv run pytest`                               | Runs the tests                       |
| `uv run pyright`                              | Checks types in strict mode          |
| `uv run ruff check`                           | Lints the Python code                |
| `uv run ruff format`                          | Formats the Python code              |

The git hook runs these checks on each commit: file hygiene, the lock file, the schema lint, the generated models, the knowledge nodes, the graph checks, the directive checks, the governance checks, the language checks, the compiled outputs, Ruff lint and format, Markdown format, Pyright, and the tests.
