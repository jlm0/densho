# Template packaging

> **In the library:** the library in a box. A new town gets a full copy, runs it as its own from then on, and can read what changed at the original.

**Status:** Built.

This layer installs the template into a project, records which template commit the project started from, and keeps a change history that agents can read. [Copier](https://copier.readthedocs.io/) does the copy and the later merge.

A project receives one copy, and from then on it owns that copy. It can change and grow anything it received, so drift from the template is expected. Nothing pins a project's knowledge to a template version, and nothing forces it to pull a change.

## Install

You need a current [uv](https://docs.astral.sh/uv/), git, and read access to the template repo. You don't need Python, because uv fetches it.

Run this in the project folder. The folder can be empty, or it can hold a repo with history.

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD https://github.com/jlm0/knowledge-architecture.git .
uv tool install pre-commit
git init
pre-commit install
git add -A
git commit -m "feat: add the knowledge architecture"
```

Leave out `git init` if the folder already holds a repo. Each new clone of the project needs `pre-commit install` again.

The flags each have a reason:

- `--trust` lets Copier run the one command that the template asks for after the copy, `.ka/ka adopt`.
- `--defaults` accepts the only question, which records the start commit.
- `--vcs-ref=HEAD` takes the latest commit. The template has no tags yet, and Copier picks the latest tag once one exists.
- `--python 3.14` keeps uvx away from an old system Python, which resolves a Copier too old for this template.

Install from the URL, not from a local checkout. A checkout with uncommitted changes passes them on to the project, inside the paths that a project receives, and `.ka/ka` then points at a commit that exists only in a temporary clone.

Don't install over your own `knowledge/`, `skills/`, or `governance/`. Copier overwrites a file at the same path: in a terminal it asks about each file and the default answer is yes, and without a terminal it stops with an error and leaves a partial copy. Rename those folders first, then bring their content back as nodes.

## What a project receives

| Path                                                       | What it is                                      |
| ---------------------------------------------------------- | ----------------------------------------------- |
| `knowledge/`, `skills/`                                    | The nodes                                       |
| `governance/language/`, `governance/policies/`             | The grammar, the vocabularies, and the policies |
| `governance/schema/metamodel.yaml`                         | The schema, as a reference for an author        |
| `AGENTS.md`, `.claude/rules/knowledge/`, `.claude/skills/` | The [runtime files](runtime-files.md)           |
| `.ka/ka`, `.ka/engine-constraints.txt`                     | The way to the engine                           |
| `.ka/history.jsonl`                                        | The change history                              |
| `.pre-commit-config.yaml`, `.gitignore`                    | The git hook and the ignore rule for `build/`   |
| `.copier-answers.yml`                                      | The record of the template commit               |

That's the whole list. A project receives no engine source, tests, docs, or lock file. `copier.yml` names each path that a project receives and excludes everything else, so a file that no one listed can't reach a project, even a file that git ignores on the machine that runs the install.

## The template commit

`.copier-answers.yml` records where a project came from. Don't edit it.

| Key            | What it holds                                                      |
| -------------- | ------------------------------------------------------------------ |
| `started_from` | The full hash of the first template commit. It never changes.      |
| `_commit`      | The template commit that the project last pulled. A pull moves it. |
| `_src_path`    | The source of the install                                          |

## Which status knowledge arrives with

The [governance workflow](governance-workflow.md#knowledge-from-the-template) sets the rule, and `ka adopt` applies it. The install runs the command for you.

- In a folder with no commit yet, each entity keeps its status. There's no history to compare with, so a person reviews the whole copy in the first commit.
- In a repo with history, each entity that the last commit doesn't hold arrives as `proposed`, and the command lists it. `.ka/ka governance --pending` lists it again later, and a person accepts it in one commit.

A pull follows the same rule. Anything new or changed in a reviewed field arrives as `proposed`. The template can't promote an entity in your project either: a status that becomes `accepted` in a pull goes back to `proposed`, even when nothing else changed.

If an entity was `deprecated` in the template, it loses that mark when it arrives as `proposed`. The command prints a note, so you can set it back.

## Your own files

An install never overwrites these files:

- `CLAUDE.md` is what Claude Code reads instead of `AGENTS.md`, so `ka adopt` adds the line `@AGENTS.md` at the end and changes nothing else. A `.claude/CLAUDE.md` receives `@../AGENTS.md` when it's the only one. If you already import the root, the command adds nothing.
- `CLAUDE.local.md` is your private file, so the command doesn't touch it. It prints a note with the line to add.
- An `AGENTS.md` that you wrote stays, and the install ends with `not-generated`, because the generator won't overwrite a file without its marker. Move your text to `CLAUDE.md` or to a node, delete the file, and run `.ka/ka adopt`.
- A `.pre-commit-config.yaml` of your own stays, so the checks don't run until you add the hooks from [the git hook](#the-git-hook).
- A `.gitignore` of your own stays. Add `build/` to it, or the compiled output and the [site](human-interface.md) show up as untracked files.

A rule directly in `.claude/rules/` and a skill folder of your own stay as well, as they do in [runtime files](runtime-files.md#hand-written-files).

## The engine in a project

Use `.ka/ka` wherever another page says `uv run ka`. It takes the same commands.

```sh
.ka/ka runtime
.ka/ka governance --pending
.ka/ka view
.ka/ka accept --subtree <node-id>
```

The file runs `uvx --from git+<source>@<commit> ka`. The commit is the template commit that the project last pulled, so a pull moves the engine with no separate step. The pin covers the engine and not your knowledge. `.ka/engine-constraints.txt` holds the locked version of each dependency, because `uvx` doesn't read a lock file.

A project needs uv and git, and nothing else. Without uv, the file names uv and exits with 127. Use a current uv: uv 0.8.4 fetches a release candidate of Python 3.14 that the engine crashes on, and uv 0.13.7 works. `uv self update` fixes this.

The first run on a machine downloads the engine and takes about 30 seconds. A later run takes about 2 seconds and needs no network.

The template repo is private today, and that reaches every project. `copier copy`, `copier update`, and the first `.ka/ka` on a machine all read the repo with that machine's git credentials. A person without read access can't install, and a clone of the project on their machine fails at its first hook. A public repo would remove this limit with no change to a file.

## The git hook

A project runs three hooks. None of them needs Python in the project.

| Hook               | What it does                                   |
| ------------------ | ---------------------------------------------- |
| `conflict-markers` | Stops a commit that still holds a merge marker |
| `rejected-hunks`   | Stops a commit that holds a `.rej` file        |
| `knowledge-checks` | Runs `.ka/ka runtime --verify` on each commit  |

`.ka/ka runtime --verify` runs every check, then compares the generated files, as [the git hook](runtime-files.md#the-git-hook) explains. The template's Markdown, Python, and type hooks stay in the template, because they'd rewrite or check files that belong to the project.

## Pull a template change

Pulling is optional. Commit your work first, because Copier needs a clean tree.

```sh
uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD
```

Copier replays your changes on a new copy of the template. It asks for `--trust` because the template holds a task, although the task runs only on an install.

Resolve any conflict, then run `.ka/ka adopt`, read the result, and commit. The hook stops the commit if you skip a step.

Your `started_from` stays. `_commit`, the engine pin, and `.ka/history.jsonl` move. Copier doesn't merge the generated files, so they never conflict, and `.ka/ka adopt` writes them again. It also removes a generated file that a pull brought back for a node you moved or deleted.

`.pre-commit-config.yaml` and `.gitignore` stay as they are too, so a hook that the template adds later doesn't reach you. Compare the two files by hand when you pull.

### A node that both sides changed

The result depends on which lines changed:

- If you and the template changed different lines of a node, the pull keeps both changes with no conflict.

- If you changed the same lines, Copier writes both versions into the node file:

  ```text
  <<<<<<< before updating
  - Limit each view to `2` primary colors and `2` secondary colors. ^limit-color-palette
  =======
  - Limit each screen to `2` primary colors and `2` secondary colors. ^limit-color-palette
  >>>>>>> after updating
  ```

`before updating` holds your text, and `after updating` holds the template's. Nothing decides for you. The `conflict-markers` hook stops the commit while a marker stays in any file, and a marker in a definition or a directive also stops `.ka/ka adopt`, because the parser can't read that section. Keep what you want, run `.ka/ka adopt`, and commit. If you keep the template's text of a directive, it differs from your last commit, so it arrives as `proposed`.

### A node that you moved or deleted

Copier compares paths and doesn't know about IDs. If you moved a node, a template change to it doesn't reach the new path, and no conflict tells you. If you deleted a node, it stays deleted, and the template's change to it is dropped.

The change history finds what a move lost. This command prints each entity that differs from the template by ID, with the fields that differ:

```sh
.ka/ka history --drift
```

For a moved node that the template also changed, the line names both `path` and the changed field. To take the change, read the template's version and edit your node.

## The change history

`.ka/history.jsonl` lists each change to the template, one entity on each line, for an agent to read. A search for an ID finds every change to that entity, wherever its file sits now. The [migration and reconciliation skill](migration-and-reconciliation.md) reads this file.

```json
{"change":3,"kind":"directive","id":"limit-color-palette","action":"changed","fields":["text"],"path":"knowledge/digital-product-development/ui-ux-design/visual-design/node.md","status":"proposed","content":{"holder":"83a83f3fa4a73c2e","scope":"f1d3984b3638714f","sources":"7ca2a8e719470e72","text":"9f9068e089663fe3"}}
```

| Key       | What it holds                                                                                  |
| --------- | ---------------------------------------------------------------------------------------------- |
| `change`  | The number of this change. All lines from one run share it, and the number grows by one a run. |
| `kind`    | `node`, `directive`, `exception`, or `file`                                                    |
| `id`      | The stable ID. An exception uses `<node>/<directive>`, and a file uses its path.               |
| `action`  | `added`, `changed`, or `removed`                                                               |
| `fields`  | The fields that changed, including `path` and `status`. An `added` or `removed` line has none. |
| `path`    | The path in the template at this change                                                        |
| `status`  | The status in the template at this change. A file has `null`.                                  |
| `content` | A digest of each field after this change. A `removed` line has none.                           |

A digest is a short hash of one field, and it leaves out formatting, so a Markdown formatter adds no line. It lets a reader see which field differs without the template's text. For the text itself, read the template. `git log` on the file names the commit of each line.

A `file` line covers each YAML file under `governance/language/`, so a reader sees a new word that a template directive needs. A `status` isn't in `content`, because a project changes it on arrival.

A project's copy is the template's file as of its last pull, and the project doesn't write to it. Lines with a higher `change` than a project's copy are new.

### Keep it correct in the template

In the template, the `template-history` hook runs `uv run ka history --verify` on each commit. Replaying every line must give the same state as the tree. If it doesn't, the command appends one new change and fails with `changed`, so you stage the file and commit again.

The file only grows. To undo a template commit, use `git revert --no-commit`, restore the file with `git checkout HEAD -- .ka/history.jsonl`, run `uv run ka history`, stage the result, and commit, so the undo appears as a new change.

The `engine-constraints` hook writes `.ka/engine-constraints.txt` from `uv.lock` in the same way, and fails when the file changes.

## What you can delete from governance

Most of what you received is yours to delete. Three folders behave differently.

- `governance/schema/` can go. The engine reads its own copy, so the checks pass without it, and editing your copy changes no check. To change the schema, change the template.
- `governance/policies/` can go, as long as the root drops its pointer to `governance` in the same commit.
- `governance/language/` can't go. The language checks need a grammar and vocabularies from your repo, and the engine has no copy to fall back on, because then the template would still control your language. Edit these files to change the rules.

## Use it from code

```python
from pathlib import Path

from knowledge_architecture.template import adopt_template, history_drift, record_history

adopted = adopt_template(Path())
adopted.proposed  # the entities that this run set to proposed
adopted.imported  # the file that received the import of the root

drift = history_drift(Path())
drift.entries  # each difference, in the form of a history line

recorded = record_history(Path(), verify=False)
recorded.problems  # the same problems that ka history prints
```

## Codes

These codes come from `ka adopt` and `ka history`. Each other code comes from a check that the command runs.

| Code           | What it reports                                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------- |
| `adopt`        | The command can't set a status, because a file blocks it or the status line has another form              |
| `import`       | The command can't add the import, because the file is a symbolic link to another file or can't be written |
| `history`      | A line doesn't parse, a change number leaves a gap, or an action doesn't fit the replay                   |
| `rewritten`    | The file doesn't start with its text at `HEAD`                                                            |
| `not-template` | `ka history` ran in a folder with no `copier.yml`. `--drift` runs anywhere.                               |
| `changed`      | With `--verify`, the command appended a change                                                            |
| `not-staged`   | With `--verify`, the git index doesn't hold the history file                                              |
| `write`        | The command can't change the history file                                                                 |

## What it does not check yet

- Whether a merged node says what either side meant. The checks read the result, and a person reads the meaning.
- Whether a project's copy of the history matches the template's. A project can edit its copy, and no check there reads the file except `--drift`.
- A commit that skips the hook. A plain `git revert` commits with no hook, so it removes history lines and nothing fails.
- Whether the commit in `.ka/ka` still exists in the template. A rewritten template history stops a project at its next cold cache.
- Whether a pull lost a change to a moved node. `--drift` shows the difference, and nothing makes you read it.
- Whether a project keeps `.ka/`, the hooks, or the import. A project owns those files too.

## What hasn't been tested

The install, the hooks, and a pull have run from a local clone of the template on macOS, with a clean home folder and a cold cache. The install, the hooks, and a pull have also run from the private URL, on a machine with read access. Three things are still untested:

- A machine with no read access to the private repo.
- Linux and Windows. `.ka/ka` is a POSIX shell script, so Windows needs a shell that runs it.
- A real Claude Code session loading `AGENTS.md` through the import. This rests on the Claude Code docs, as [the runtime page](runtime-files.md#what-only-a-real-session-can-show) explains.
