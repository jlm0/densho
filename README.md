# Densho

Densho is a template for a governed knowledge architecture that humans and agents share. The name is the Japanese 伝書, the scroll of teachings that a school passes on.

Knowledge lives in a tree of Markdown files that runs from domain to discipline to practice area to concept. Each file is a node. It holds concepts, directives, and links to other nodes. A governance layer sets what a node can contain, how a directive is written, and how knowledge changes. The governance is written in its own grammar and follows its own rules, so the checks that lint a knowledge node lint the governance too.

A build generates `AGENTS.md` from the tree as its root node. Agent tools such as Claude Code load it at the start of each session and follow the tree from there.

Every layer is built. Every seed directive is still a proposal, so no directive is in force until a person [accepts it](docs/human-interface.md).

## Setup

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.14 if your machine does not have it.

```sh
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

`uv sync` installs the locked environment. `pre-commit install` adds a git hook that runs every check on each commit. The last command runs every check once.

## Structure

| Path                                                                              | Contents                                                           |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `knowledge/node.md`                                                               | The root node                                                      |
| `knowledge/nodes/`                                                                | The knowledge nodes: concepts and directives                       |
| `knowledge/skills/`                                                               | Skill sources built from the knowledge tree                        |
| `knowledge/evals/`                                                                | Eval tasks, with known good and bad outputs                        |
| `knowledge/governance/policies/`                                                  | Lifecycle, approval, and change rules, written as nodes            |
| `knowledge/governance/language/`                                                  | The directive grammar and the vocabularies                         |
| `knowledge/governance/schema/`                                                    | The metamodel: node kinds, relationship kinds, and required fields |
| `knowledge/.densho/`                                                              | The way to the engine in a project, and the change history         |
| `AGENTS.md`, `.claude/references/`, `.claude/rules/knowledge/`, `.claude/skills/` | Generated from the nodes. Do not edit them.                        |
| `engine/`                                                                         | The [Python engine](docs/README.md#where-the-code-lives)           |
| `tests/`                                                                          | Tests for the engine                                               |
| `docs/`                                                                           | The overview and a page for each layer                             |
| `build/`                                                                          | Generated output. Git ignores it.                                  |
| `copier.yml`, `*.jinja`                                                           | What a project receives, and the files only a project holds        |
| `global-skills/`                                                                  | Skills you install yourself. A project doesn't receive them.       |

You edit `knowledge/`. Agents read `AGENTS.md` and `.claude/`.

## Use the template

Install the template into a project once. From then on the project owns its copy. You need a current uv, git, and read access to this repo, which is private. A project needs no Python.

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD https://github.com/jlm0/densho.git .
uv tool install pre-commit
pre-commit install
```

The install asks which disciplines to take and whether to keep what the template accepted. `--defaults` takes every discipline, with each entity as a proposal. Run `git init` before `pre-commit install` if the folder has no repo. In a project, `knowledge/.densho/densho` takes the place of `uv run densho`. To pull a later template change, run `uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD`, then `knowledge/.densho/densho adopt`.

The template ships domain knowledge, which is universal. A project writes workspace knowledge about its own code, under the same governance. [Template packaging](docs/template-packaging.md) explains each step, and the [migration skill](docs/migration-and-reconciliation.md) converts the rules a project already has. Each project also gets three skills that turn your corrections into proposals, review them with you, and sync with the template: the [improvement loop](docs/improvement-loop.md). A fourth runs [eval tasks](docs/evaluation.md) to test whether the rules help.

## Run the checks

| Command                              | What it does                      |
| ------------------------------------ | --------------------------------- |
| `uv run pre-commit run --all-files`  | Runs every check on every file    |
| `uv run pytest`                      | Runs the tests                    |
| `uv run pyright`                     | Checks types in strict mode       |
| `uv run ruff check`                  | Lints the Python code             |
| `uv run densho build`                | Runs every check on the knowledge |
| `uv run densho governance --pending` | Lists what waits for review       |
| `uv run densho view`                 | Writes a site for people to read  |

## Read more

Start with the [overview](docs/README.md). It explains the system as a library, links to a page for each layer, and lists each command.
