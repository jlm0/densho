# Template packaging

> **In the library:** the library in a box. A new town gets a full copy, runs it as its own from then on, and can read what changed at the original.

**Status:** Built.

This layer installs the template into a project, lets the project choose its disciplines, records which template commit the project started from, and keeps a change history that agents can read. [Copier](https://copier.readthedocs.io/) does the copy and the later merge.

A project receives one copy, and from then on it owns that copy. It can change and grow anything it received, so drift from the template is expected. Nothing pins a project's knowledge to a template version, and nothing forces it to pull a change.

## Install

You need a current [uv](https://docs.astral.sh/uv/), git, and read access to the template repo. You don't need Python, because uv fetches it.

Run this in the project folder. The folder can be empty, or it can hold a repo with history.

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD https://github.com/jlm0/densho.git .
uv tool install pre-commit
git init
pre-commit install
git add -A
git commit -m "feat: add Densho"
```

Leave out `git init` if the folder already holds a repo. Each new clone of the project needs `pre-commit install` again.

The flags each have a reason:

- `--trust` lets Copier run the template's commands: `knowledge/.densho/densho adopt` after the copy, and `knowledge/.densho/densho select` during a pull.
- `--defaults` accepts the default answer to [each question](#the-questions): every discipline, and each entity as `proposed`.
- `--vcs-ref=HEAD` takes the latest commit. The template has no tags yet, and Copier picks the latest tag once one exists.
- `--python 3.14` keeps uvx away from an old system Python, which resolves a Copier too old for this template.

Install from the URL, not from a local checkout. A checkout with uncommitted changes passes them on to the project, inside the paths that a project receives, and `knowledge/.densho/densho` then points at a commit that exists only in a temporary clone.

Don't install over your own `knowledge/`. Copier overwrites a file at the same path: in a terminal it asks about each file and the default answer is yes, and without a terminal it stops with an error and leaves a partial copy. Rename that folder first, then bring its content back as nodes.

## The questions

Two questions decide what you get, and `--defaults` takes the default answer to both. Leave out `--defaults` to answer in a terminal, or pass an answer with `--data`:

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD \
  --data 'disciplines=[ui-ux-design, brand-design]' \
  --data keep_template_status=true \
  https://github.com/jlm0/densho.git .
```

| Question               | Default | What it decides                                                                                                                                           |
| ---------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `disciplines`          | All six | Which disciplines the project receives: `product-strategy`, `user-research`, `brand-design`, `content-design`, `ui-ux-design`, and `software-engineering` |
| `keep_template_status` | `false` | Whether what the template accepted stays `accepted`. See [which status knowledge arrives with](#which-status-knowledge-arrives-with).                     |

A third question, `started_from`, records the start commit, so keep its default. Copier records each answer in `.copier-answers.yml`, and a pull reuses them.

### Choose the disciplines

A discipline brings its practice areas and concepts, with their directives. A node belongs to each discipline that its `broader` chain reaches. Everything that belongs to no discipline always arrives: the root, the domain node, the governance policies, and the language files.

Leaving a discipline out removes:

- Each of its nodes, its branch vocabulary in `knowledge/governance/language/branches/`, and its eval tasks in `knowledge/evals/`.
- Each skill that uses or applies something you left out. A skill that draws only on what you keep, or only on the governance, arrives. The four preset skills, three of the [improvement loop](improvement-loop.md) and the [eval](evaluation.md) skill, draw only on the governance, so every install has them.
- Each `informs`, `related`, `also_attached_to`, or `refines` entry, and each pointer, that names something you left out. The node or directive that held it stays.

If a node you keep `depends_on` a node in another discipline, the install adds that discipline and prints a note. The template has no such link: a handoff from one discipline to the next is an `informs` edge, so `[brand-design]` arrives without product strategy, and the edge from product positioning to brand strategy goes with it.

A link of any other kind to something you left out, such as `broader`, `uses`, or `conflicts_with`, stops the command with `select`, and no file changes. The template has no such link, and its tests install each discipline on its own to keep it that way.

`knowledge/.densho/densho select` applies the answer, and `knowledge/.densho/densho adopt` runs it first. It reads `disciplines` from `.copier-answers.yml`, and without that key it keeps everything. During a pull, Copier runs it on each copy that it renders, so a discipline you left out doesn't come back, and a link it removed doesn't show up as a template change.

## What a project receives

| Path                                                                              | What it is                                         |
| --------------------------------------------------------------------------------- | -------------------------------------------------- |
| `knowledge/node.md`, `knowledge/nodes/`, `knowledge/skills/`                      | The nodes                                          |
| `knowledge/governance/language/`, `knowledge/governance/policies/`                | The grammar, the vocabularies, and the policies    |
| `knowledge/governance/schema/metamodel.yaml`                                      | The schema, as a reference for an author           |
| `knowledge/.densho/densho`, `knowledge/.densho/engine-constraints.txt`            | The way to the engine                              |
| `knowledge/.densho/history.jsonl`                                                 | The change history                                 |
| `AGENTS.md`, `.claude/references/`, `.claude/rules/knowledge/`, `.claude/skills/` | The [runtime files](runtime-files.md)              |
| `.pre-commit-config.yaml`, `.gitignore`                                           | The git hook and the ignore rule for `build/`      |
| `.copier-answers.yml`                                                             | The record of the template commit and your answers |

A [selection](#choose-the-disciplines) narrows `knowledge/nodes/`, `knowledge/skills/`, `knowledge/evals/`, the branch vocabularies, and the runtime files.

That's the whole list. A project receives no engine source, tests, docs, or lock file. `copier.yml` names each path that a project receives and excludes everything else, so a file that no one listed can't reach a project, even a file that git ignores on the machine that runs the install. Everything under `knowledge/` ships, so the template keeps its own tool files elsewhere: the schema lint settings and the model template sit in `engine/schema/`.

## The template commit

`.copier-answers.yml` records where a project came from. Don't edit it.

| Key                    | What it holds                                                            |
| ---------------------- | ------------------------------------------------------------------------ |
| `started_from`         | The full hash of the first template commit. It never changes.            |
| `_commit`              | The template commit that the project last pulled. A pull moves it.       |
| `_src_path`            | The source of the install                                                |
| `disciplines`          | Your choice of [disciplines](#choose-the-disciplines). A pull reuses it. |
| `keep_template_status` | Your answer at the install. A pull doesn't read it.                      |

## Which status knowledge arrives with

The [governance workflow](governance-workflow.md#knowledge-from-the-template) sets the rule, and `densho adopt` applies it. The install runs the command for you.

By default each entity arrives as `proposed`, in an empty folder and in a repo with history alike, and the command lists it. `knowledge/.densho/densho governance --pending` lists it again later, and a person accepts it.

If you answer yes to `keep_template_status`, an entity that the template accepted keeps `accepted`, as long as you receive the same content that the template accepted. The template's `knowledge/.densho/history.jsonl` decides: its last line for the entity must say `accepted`, and each field digest must match. `knowledge/.densho/densho adopt --keep-accepted` applies this answer. Everything else still arrives as `proposed`, and the git hook runs the same test, so the install commit passes.

Answer yes only if you accept that content for your project, because each accepted directive is in force from the first commit. Today the template has accepted nothing, so the answer changes nothing yet.

A selection changes some entities: removing a link changes the node or directive that held it. Such an entity no longer matches the template's history, so it arrives as `proposed` with either answer. With only `ui-ux-design`, that's four nodes and 67 directives, if the template had accepted them. Most of the directives are accessibility and responsive design rules that lose an attachment to software testing or frontend engineering.

A pull follows the stricter rule, whatever you answered at the install. Anything new or changed in a reviewed field arrives as `proposed`. The template can't promote an entity in your project either: a status that becomes `accepted` in a pull goes back to `proposed`, even when nothing else changed. Once the last commit holds `knowledge/.densho/history.jsonl` or a node file, `--keep-accepted` keeps nothing and prints a note. The hook stops a new `accepted` entity, and `pull-promotion` stops one that the pull moves to `accepted`.

If an entity was `deprecated` or `rejected` in the template, it loses that mark when it arrives as `proposed`, with either answer. The command prints a note, so you can set it back. A rejected entity keeps its `rejection_reason`, so you can read why the template turned it down.

## Your own files

An install never overwrites these files:

- `CLAUDE.md` is what Claude Code reads instead of `AGENTS.md`, so `densho adopt` adds the line `@AGENTS.md` at the end and changes nothing else. A `.claude/CLAUDE.md` receives `@../AGENTS.md` when it's the only one. If you already import the root, the command adds nothing.
- `CLAUDE.local.md` is your private file, so the command doesn't touch it. It prints a note with the line to add.
- An `AGENTS.md` that you wrote stays, and the install ends with `not-generated`, because the generator won't overwrite a file without its marker. Move your text to `CLAUDE.md` or to a node, delete the file, and run `knowledge/.densho/densho adopt`.
- A `.pre-commit-config.yaml` of your own stays, so the checks don't run until you add the hooks from [the git hook](#the-git-hook). A later pull applies the template's changes to it, as [pull a template change](#pull-a-template-change) describes.
- A `.gitignore` of your own stays. Add `build/` to it, or the compiled output and the [site](human-interface.md) show up as untracked files.

A rule directly in `.claude/rules/` and a skill folder of your own stay as well, as they do in [runtime files](runtime-files.md#hand-written-files).

## The engine in a project

Use `knowledge/.densho/densho` wherever another page says `uv run densho`. It takes the same commands.

```sh
knowledge/.densho/densho runtime
knowledge/.densho/densho governance --pending
knowledge/.densho/densho view
knowledge/.densho/densho accept --subtree <node-id>
```

The file runs `uvx --from git+<source>@<commit> densho`. The commit is the template commit that the project last pulled, so a pull moves the engine with no separate step. The pin covers the engine and not your knowledge. `knowledge/.densho/engine-constraints.txt` holds the locked version of each dependency, because `uvx` doesn't read a lock file.

A project needs uv and git, and nothing else. Without uv, the file names uv and exits with 127. Use a current uv: uv 0.8.4 fetches a release candidate of Python 3.14 that the engine crashes on, and uv 0.13.7 works. `uv self update` fixes this.

The first run on a machine downloads the engine and takes about 30 seconds. A later run takes about 2 seconds and needs no network.

The template repo is private today, and that reaches every project. `copier copy`, `copier update`, and the first `knowledge/.densho/densho` on a machine all read the repo with that machine's git credentials. A person without read access can't install, and a clone of the project on their machine fails at its first hook. A public repo would remove this limit with no change to a file.

## The git hook

A project runs four hooks. None of them needs Python in the project.

| Hook               | What it does                                                                        |
| ------------------ | ----------------------------------------------------------------------------------- |
| `conflict-markers` | Stops a commit that still holds a merge marker                                      |
| `rejected-hunks`   | Stops a commit that holds a `.rej` file                                             |
| `knowledge-checks` | Runs `knowledge/.densho/densho runtime --verify` on each commit                     |
| `eval-tasks`       | Runs `knowledge/.densho/densho eval --check` when a file under `knowledge/` changes |

`knowledge/.densho/densho runtime --verify` runs every check, then compares the generated files, as [the git hook](runtime-files.md#the-git-hook) explains. The template's Markdown, Python, and type hooks stay in the template, because they'd rewrite or check files that belong to the project.

## Pull a template change

Pulling is optional. Commit your work first, because Copier needs a clean tree.

```sh
uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD
```

Copier replays your changes on a new copy of the template. It asks for `--trust` because it runs `knowledge/.densho/densho select` on each copy that it renders, which keeps your choice of disciplines.

Resolve any conflict, then run `knowledge/.densho/densho adopt`, read the result, and commit. The hook stops the commit if you skip a step. The preset skill `sync-template` walks a pull with you, from reading what changed to the commit, as [migration and reconciliation](migration-and-reconciliation.md#pull-template-changes) explains.

Your `started_from` stays. `_commit`, the engine pin, and `knowledge/.densho/history.jsonl` move. Copier doesn't merge the generated files, so they never conflict, and `knowledge/.densho/densho adopt` writes them again. It also removes a generated file that a pull brought back for a node you deleted.

A pull merges the template's change to `.pre-commit-config.yaml` into yours, so a hook that the template adds later reaches you. If you edited the same lines, the pull leaves a `.pre-commit-config.yaml.rej` file, and the hook that stops a commit on a `.rej` file holds the commit until you apply it by hand. Your `.gitignore` stays as it is, so compare it with the template by hand when you pull.

### Change the disciplines

A pull can change your answer. Pass the whole new list:

```sh
uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD --data 'disciplines=[ui-ux-design, software-engineering]'
```

A discipline you add arrives as `proposed`, like anything new in a pull, and the links to it come back. A discipline you drop leaves the tree. If it holds `accepted` entities, `knowledge/.densho/densho adopt` and the hook stop with `removed-accepted` on each one, as for any removal of accepted knowledge.

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

`before updating` holds your text, and `after updating` holds the template's. Nothing decides for you. The `conflict-markers` hook stops the commit while a marker stays in any file, and a marker in a definition or a directive also stops `knowledge/.densho/densho adopt`, because the parser can't read that section. Keep what you want, run `knowledge/.densho/densho adopt`, and commit. If you keep the template's text of a directive, it differs from your last commit, so it arrives as `proposed`.

### A node that you moved or deleted

Copier compares paths and doesn't know about IDs. If you moved a node, a template change to it doesn't reach the new path, and no conflict tells you. If you deleted a node, it stays deleted, and the template's change to it is dropped.

The change history finds what a move lost. This command prints each entity that differs from the template by ID, with the fields that differ:

```sh
knowledge/.densho/densho history --drift
```

For a moved node that the template also changed, the line names both `path` and the changed field. To take the change, read the template's version and edit your node.

The disciplines you left out at the install aren't listed one entity at a time. Each one gets a single `note:` line with a count, such as `note: 217 entities of ui-ux-design are not in this tree, because disciplines leaves the discipline out.` The count covers each entity that the history places under the folder of that discipline, and its vocabulary branch. A skill that only the left-out discipline used still gets its own line, because the history can't tell which discipline a skill served.

## The change history

`knowledge/.densho/history.jsonl` lists each change to the template, one entity on each line, for an agent to read. A search for an ID finds every change to that entity, wherever its file sits now. The [`sync-template` skill](migration-and-reconciliation.md#pull-template-changes) reads this file.

```json
{"change":3,"kind":"directive","id":"limit-color-palette","action":"changed","fields":["text"],"path":"knowledge/nodes/digital-product-development/ui-ux-design/visual-design/node.md","status":"proposed","content":{"holder":"83a83f3fa4a73c2e","scope":"f1d3984b3638714f","sources":"7ca2a8e719470e72","text":"9f9068e089663fe3"}}
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

A `file` line covers each YAML file under `knowledge/governance/language/`, so a reader sees a new word that a template directive needs. A `status` isn't in `content`, because a project changes it on arrival.

A project's copy is the template's file as of its last pull, and the project doesn't write to it. Lines with a higher `change` than a project's copy are new.

### Keep it correct in the template

In the template, the `template-history` hook runs `uv run densho history --verify` on each commit. Replaying every line must give the same state as the tree. If it doesn't, the command appends one new change and fails with `changed`, so you stage the file and commit again.

The file only grows. To undo a template commit, use `git revert --no-commit`, restore the file with `git checkout HEAD -- knowledge/.densho/history.jsonl`, run `uv run densho history`, stage the result, and commit, so the undo appears as a new change.

A plain `git revert` commits without the hook and takes the history lines of the reverted commit with it. The next `uv run densho history --verify` then fails with `rewritten`, because the last commit lost lines that its parent holds. Run `git checkout HEAD~1 -- knowledge/.densho/history.jsonl` and `uv run densho history`, then commit the result.

The `engine-constraints` hook writes `knowledge/.densho/engine-constraints.txt` from `uv.lock` in the same way, and fails when the file changes.

## What you can delete from governance

Most of what you received is yours to delete. Three folders behave differently.

- `knowledge/governance/schema/` can go. The engine reads its own copy, so the checks pass without it, and editing your copy changes no check. To change the schema, change the template.
- `knowledge/governance/policies/` can go, as long as the root drops its pointer to `governance` in the same commit.
- `knowledge/governance/language/` can't go. The language checks need a grammar and vocabularies from your repo, and the engine has no copy to fall back on, because then the template would still control your language. Edit these files to change the rules.

## Use it from code

```python
from pathlib import Path

from engine.template import adopt_template, history_drift, record_history, select_disciplines

selected = select_disciplines(Path())
selected.disciplines  # the disciplines that stay, or None without an answer
selected.removed  # each path that the selection removed
selected.pruned  # each link that the selection removed

adopted = adopt_template(Path(), keep_accepted=True)
adopted.proposed  # the entities that this run set to proposed
adopted.imported  # the file that received the import of the root
adopted.selection  # the selection that ran first

drift = history_drift(Path())
drift.entries  # each difference, in the form of a history line
drift.notes  # the count for each discipline that the answer leaves out

recorded = record_history(Path(), verify=False)
recorded.problems  # the same problems that densho history prints
```

## Codes

These codes come from `densho adopt`, `densho select`, and `densho history`. Each other code comes from a check that the command runs.

| Code           | What it reports                                                                                                                    |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `adopt`        | The command can't set a status, because a file blocks it or the status line has another form                                       |
| `import`       | The command can't add the import, because the file is a symbolic link to another file or can't be written                          |
| `select`       | The answer can't be read, a kept entity links to a removed one in a field that the command can't remove, or a file can't be edited |
| `history`      | A line doesn't parse, a change number leaves a gap, or an action doesn't fit the replay                                            |
| `rewritten`    | The file doesn't start with its text at `HEAD`, or the last commit lost lines that its parent holds                                |
| `not-template` | `densho history` ran in a folder with no `copier.yml`. `--drift` runs anywhere.                                                    |
| `changed`      | With `--verify`, the command appended a change                                                                                     |
| `not-staged`   | With `--verify`, the git index doesn't hold the history file                                                                       |
| `write`        | The command can't change the history file                                                                                          |

## What it does not check yet

- Whether a merged node says what either side meant. The checks read the result, and a person reads the meaning.
- Whether a project's copy of the history matches the template's. A project can edit its copy. Only `--drift` and the [narrow pass](governance-workflow.md#knowledge-from-the-template) at the install read it, and neither can tell an edited copy, so an edited file can keep a status that the template never accepted.
- A commit that skips the hook. A plain `git revert` commits with no hook, so it removes history lines and nothing fails.
- Whether the commit in `knowledge/.densho/densho` still exists in the template. A rewritten template history stops a project at its next cold cache.
- Whether a pull lost a change to a moved node. `--drift` shows the difference, and nothing makes you read it.
- Whether a project keeps `knowledge/.densho/`, the hooks, or the import. A project owns those files too.

## What hasn't been tested

The install, the hooks, and a pull have run from a local clone of the template on macOS, with a clean home folder and a cold cache. The install, the hooks, and a pull have also run from the private URL, on a machine with read access. Each answer to each question has run in an empty folder and in a repo with history, from a copy of the template with accepted entities, and so has a pull that adds a discipline. These things are still untested:

- A machine with no read access to the private repo.
- Linux and Windows. `knowledge/.densho/densho` is a POSIX shell script, so Windows needs a shell that runs it.
- A pull that drops a discipline after you deprecate its accepted entities.
- A real Claude Code session loading `AGENTS.md` through the import. This rests on the Claude Code docs, as [the runtime page](runtime-files.md#what-only-a-real-session-can-show) explains.
