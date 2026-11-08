# Fixture project

[`project/`](project/) holds the files that a project gets when it installs this template with all six disciplines. It shows what an agent in such a project would load: the root, the [runtime files](../docs/runtime-files.md), and the install answers.

Each change to a node shows up here in the same commit, so you can review its effect on a project without installing anything.

## The names differ from a project

Three names change in the fixture, and nothing else does:

| In the fixture                                           | In a project               |
| -------------------------------------------------------- | -------------------------- |
| [`project/AGENTS.fixture.md`](project/AGENTS.fixture.md) | `AGENTS.md`                |
| `project/claude/references/`                             | `.claude/references/`      |
| `project/claude/rules/knowledge/`                        | `.claude/rules/knowledge/` |
| `project/claude/skills/`                                 | `.claude/skills/`          |
| `project/copier-answers.yml`                             | `.copier-answers.yml`      |

With the real names, Claude Code would load the fixture into any session on this repo. It loads an `AGENTS.md` in a subfolder, and the skills and rules under a subfolder's `.claude/`, as soon as an agent reads a file there. Every directive here is in force, so an agent working on the template would pick up rules that aren't in force in the template, and a second copy of most skills.

Copier is the reason for the third name. It treats a file named `.copier-answers.yml` anywhere in the template as the project's answers file, so every install would get the fixture's answers.

The script rewrites each link that crosses a renamed path, so every link in the fixture still opens the right file. A test fails if the fixture holds `AGENTS.md`, `CLAUDE.md`, `.claude`, or `.copier-answers.yml` in any letter case, because a Mac file system ignores case by default.

## It shows the state at V1

Every entity in the fixture is `accepted`, so every directive is in force. That's the V1 state, where each default is accepted. Today the template has accepted nothing, so the status here is a simulation for review, not an approval.

The script that builds the fixture installs this repo's working tree into a scratch project in a temporary folder, the way `copier copy --defaults` does. It runs the same engine code as the install, then accepts every entity in the scratch project, as a person in that project would with `knowledge/.densho/densho accept --subtree root`, and copies the output here. It never sets a status in this repo's `knowledge/`, and it refuses to build its scratch project inside this repo. The scratch project's `knowledge/` isn't committed.

Two answers in `copier-answers.yml` differ from a real install. `_commit` and `started_from` hold `working-tree` instead of a commit hash, because the fixture comes from the working tree, and a hash would change with every edit to the repo, docs included. `_src_path` holds the public URL of the template, as an install from that URL records it. `keep_template_status` stays `false`, because the statuses come from the accept after the install.

## Generate it again

```sh
uv run python fixtures/generate.py
```

The script takes about 25 seconds, and the same working tree always gives the same bytes. Don't edit the files in `project/` by hand: the next run overwrites them.

A git hook runs the script with `--verify` on each commit that touches `knowledge/`, `engine/`, `fixtures/`, `copier.yml`, `uv.lock`, or the answers template `{{_copier_conf.answers_file}}.jinja`. If the fixture differs from a fresh generation, the hook writes the new files and fails, so you stage them and commit again.
