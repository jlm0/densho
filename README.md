# Knowledge architecture

A template for a governed knowledge architecture that humans and agents share.

Knowledge lives in a tree of Markdown files that runs from domain to discipline to practice area to concept. Each file is a node. It holds concepts, directives, and links to other nodes. A governance layer sets what a node can contain, how a directive is written, and how knowledge changes. The governance is written in its own grammar and follows its own rules, so the checks that lint a knowledge node lint the governance too.

A build generates `AGENTS.md` from the tree as its root node. Agent tools such as Claude Code load it at the start of each session and follow the tree from there.

The repo is early. The schema, the node parser, the graph checks, the language checks, the directive semantics, the governance workflow, the seed knowledge, the compiled outputs, the runtime files, the template packaging, and the migration and reconciliation skill are in place. Every seed directive is still a proposal, so no directive is in force yet.

## Setup

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.14 if your machine does not have it.

```sh
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

`uv sync` installs the locked environment. `pre-commit install` adds a git hook that runs every check on each commit. The last command runs every check once.

## Structure

| Path                                          | Contents                                                             |
| --------------------------------------------- | -------------------------------------------------------------------- |
| `governance/schema/`                          | The metamodel: node kinds, relationship kinds, and required fields   |
| `governance/language/`                        | The directive grammar and the vocabularies                           |
| `governance/policies/`                        | Lifecycle, approval, and change rules, written as nodes              |
| `knowledge/`                                  | The knowledge nodes: concepts and directives                         |
| `skills/`                                     | Skill sources built from the knowledge tree                          |
| `engine/knowledge_architecture/`              | The Python engine: validators, compiler, and packager                |
| `engine/knowledge_architecture/generated/`    | Models and shapes generated from the schema. Do not edit them.       |
| `engine/knowledge_architecture/parser/`       | Reads `node.md` files into the models, with line numbers             |
| `engine/knowledge_architecture/graph/`        | Checks the structure of the whole graph                              |
| `engine/knowledge_architecture/language/`     | Checks directives, triggers, and skill descriptions                  |
| `engine/knowledge_architecture/directives/`   | Works out which directives apply at each node, and checks the result |
| `engine/knowledge_architecture/governance/`   | Checks the lifecycle, and compares each change with the last commit  |
| `engine/knowledge_architecture/compiler/`     | Compiles the checked graph to JSON and RDF, with digests             |
| `engine/knowledge_architecture/runtime/`      | Generates the files that an agent tool loads                         |
| `engine/knowledge_architecture/template/`     | Takes in template knowledge, and records the history                 |
| `engine/knowledge_architecture/vendor/`       | A third-party linter, kept unchanged with its license                |
| `tests/`                                      | Tests for the engine                                                 |
| `docs/`                                       | The overview and a page for each layer                               |
| `build/`                                      | Generated output. Git ignores it.                                    |
| `AGENTS.md`                                   | Generated from the root node. Do not edit it.                        |
| `.claude/rules/knowledge/`, `.claude/skills/` | Generated path rules and skills. Do not edit them.                   |
| `copier.yml`, `*.jinja`                       | What a project receives, and the files only a project holds          |
| `.ka/`                                        | The way to the engine in a project, and the change history           |
| `company-skills/`                             | A skill you install yourself. A project doesn't receive it.          |

## Docs

Start with the [overview](docs/README.md). It explains the system as a library and links to a page for each layer, built or planned.

## Usage

### Start a project from the template

Install the template into the project once. From then on the project owns its copy. It adds workspace knowledge about its own code and can change anything it received. Drift from the template is expected.

You need a current uv, git, and read access to this repo, which is private. A project needs no Python.

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD https://github.com/jlm0/knowledge-architecture.git .
uv tool install pre-commit
pre-commit install
```

Run `git init` before `pre-commit install` if the folder has no repo. In a project, `.ka/ka` takes the place of `uv run ka`. To pull a later template change, run `uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD`, then `.ka/ka adopt`.

[Template packaging](docs/template-packaging.md) explains each step, what a project receives, and what happens to a node that both sides changed. To convert the rules a project already has, or to get help with a pull, install the [migration and reconciliation skill](docs/migration-and-reconciliation.md).

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
| `uv run ka runtime`                           | Writes the files an agent tool loads |
| `uv run ka runtime --proposals`               | Writes a review copy of those files  |
| `uv run ka adopt`                             | Takes in template knowledge          |
| `uv run ka history`                           | Records template changes for agents  |
| `uv run ka history --drift`                   | Lists differences from the history   |
| `uv run pytest`                               | Runs the tests                       |
| `uv run pyright`                              | Checks types in strict mode          |
| `uv run ruff check`                           | Lints the Python code                |
| `uv run ruff format`                          | Formats the Python code              |

The git hook runs these checks on each commit: file hygiene, the lock file, the engine constraints, the schema lint, the generated models, the knowledge nodes, the graph checks, the directive checks, the governance checks, the language checks, the compiled outputs, the runtime files, the template history, Ruff lint and format, Markdown format, Pyright, and the tests.
