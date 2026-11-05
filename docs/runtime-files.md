# Runtime files

> **In the library:** the signs that lead a visitor to the right shelf. This is the first layer an agent feels, because the signs are what it reads.

**Status:** Built.

This layer generates the files an agent tool loads: the root `AGENTS.md`, a folder `AGENTS.md` beside most nodes, path rules, and skills. Claude Code is the first target, and no hook injects context, because the tool loads these files with its own mechanisms. The code is in `engine/knowledge_architecture/runtime/`.

The generated files are output, and the repo still commits them, because an agent tool reads them straight from a clone. A node file stays the source, so a change goes in the node and the command writes the file again. A hand edit doesn't survive.

## Generate

```sh
uv run ka runtime
```

```text
wrote AGENTS.md
wrote .claude/skills/design-settings-interface/SKILL.md
in_force: 25 files, 2 written, 0 removed, 0 problems
```

The command compiles the graph with the same code as `ka build`, so it runs every check on one reading of the tree. It writes each file that differs and removes each file of its own that no node generates any more. A second run changes nothing.

A rejected tree leaves the committed files alone, so an agent keeps its entry point while you repair a node. An empty tree removes every generated file and passes, so a project can still remove what it received.

## What each node becomes

| Node                               | Generated file                                  | How it loads                               |
| ---------------------------------- | ----------------------------------------------- | ------------------------------------------ |
| The root                           | `AGENTS.md`                                     | At session start                           |
| A skill                            | `.claude/skills/<id>/SKILL.md`                  | The agent picks it from the skill listing  |
| The target of a `ka:PathPointer`   | `.claude/rules/knowledge/<id>.md` with `paths`  | When the agent touches a matching file     |
| The target of a `ka:AlwaysPointer` | `.claude/rules/knowledge/<id>.md` without paths | At session start                           |
| Any other node                     | `AGENTS.md` beside its `node.md`                | When the agent opens a file in that folder |

A `ka:TextPointer` adds no file. It becomes a line that holds the trigger and a link, such as `You decide how a screen looks. Read [Visual design](visual-design/node.md).`, and following that link loads the folder `AGENTS.md` beside the node.

A node file names its pointer targets by ID. The generated files turn each ID into a real path, and that is a large part of what a folder file adds.

A skill behind a path or always pointer gets both a skill file and a rule. A path rule also matches its own node file, so a text pointer that opens the node still loads the rule.

## What a file holds

Each file puts its directives first, then its procedures, then its references.

| File        | Holds                                                                                                                |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| Root        | The state of the graph, its directives, the body of `knowledge/node.md`, the domains, the governance, and the skills |
| Skill       | Its directives and exceptions, its body, and its pointers                                                            |
| Path rule   | Its directives and exceptions, the definition, the body, and its pointers                                            |
| Folder file | Its directives and exceptions, and its pointers. The definition and the body are in the node                         |

The root holds only what an agent can't work out from the files. It names each domain, the governance node and its policies, and each skill with its description, so an agent can still find a skill if the tool drops its description. Setup, paths, and commands stay in the README. The architecture facts come from the body of `knowledge/node.md`, so they go through review like any other node.

A directive list holds what applies at that node and nothing else: inherited directives, attached ones, and `applies`, minus each one an [exception](directive-semantics.md#stepping-out) stops. Each directive keeps its `^id`, and each group links to the node that holds it. A list is complete for its own node, so the files for a node and its parent can repeat a line.

## Nothing is in force yet

The default result holds only what the [governance workflow](governance-workflow.md) puts in force. Every seed entity is still `proposed`, so today the committed files hold the nodes and the pointers but no directive. The root says so plainly, so an agent doesn't assume a rule:

```text
No directive is in force. The graph holds 81 directives and 1 exception that are not in force.

Treat a directive as a rule only when its `status` is `accepted`. A generated file lists only the directives that apply at its own node.
```

A node file still shows each proposal, with its `status`. That is the reason for the second sentence.

After you accept something, run `uv run ka runtime` and stage the result in the same commit.

## See what acceptance would change

```sh
uv run ka runtime --proposals
```

This writes a review copy to `build/runtime-proposals/`, which git ignores, and it leaves the committed files alone. The copy holds what the files would hold if a person accepted every proposal. Each file opens with a notice that starts `NOT IN FORCE`, and each directive and exception that isn't `accepted` carries its status:

```text
- Group the related fields of each form. ^group-related-fields (proposed)
```

Claude Code also loads `AGENTS.md`, `.claude/rules/`, and `.claude/skills/` from a subfolder when an agent works there, so a copy under those names could load as if it were real. The review copy therefore renames each file, and an agent that reads it can't trigger a load:

| Committed file                    | Review copy                                                        |
| --------------------------------- | ------------------------------------------------------------------ |
| `AGENTS.md`                       | `build/runtime-proposals/AGENTS.proposals.md`                      |
| `.claude/skills/<id>/SKILL.md`    | `build/runtime-proposals/claude/skills/<id>/SKILL.proposals.md`    |
| `.claude/rules/knowledge/<id>.md` | `build/runtime-proposals/claude/rules/knowledge/<id>.proposals.md` |

Each link in the copy resolves from where the copy sits, so a line in the copy can hold more `../` than the committed line. A rejected tree removes the copy.

## Why a skill holds a copy

A skill is an entry point in the middle of the tree, so it has to carry the directives that reach it. The build copies them into the skill file, and doesn't list the nodes as required reads.

Compaction decides this. After compaction, Claude Code re-attaches each invoked skill and keeps the first 5,000 tokens, while it restores only a few of the files an agent read. A required read also leaves the choice to the agent, and a node file holds proposals and rules that an exception stops. `design-settings-interface` draws 39 directives from 11 nodes, so a list of reads would be the weaker answer.

The directives sit directly after the title, so they are the part that compaction keeps. The build fails with `size` if the title and the directives of a skill take more than 15,000 characters. That is 3 characters for each of the 5,000 tokens, a low estimate on purpose, because the repo has no tokenizer. The procedure comes after the directives, so a long one can still be cut. A skill says near its top that the agent can invoke it again, and the root says the same, because the oldest skill can drop out entirely.

The copy can't go stale, because the hook compares it with a fresh generation on each commit.

## Hand-written files

A generated file holds one marker line: the first line, or the first line after the front matter. The generator changes or removes a file only if it holds that marker, so your own files are safe:

- A rule directly in `.claude/rules/`, a skill folder of your own, and an `AGENTS.md` outside `knowledge/`, `skills/`, and `governance/` all stay as they are.
- A file without the marker at a generated path fails with `not-generated`, and the run writes nothing. Move the file, then run again.
- A symbolic link in a generated path fails the same way, so the generator can't write through a link to another file.

The parser reads the same marker. A Markdown file in a node folder must be `node.md` or a generated file, so a hand-written `AGENTS.md` there fails with `file-name`. So does a generated one after someone removes its marker.

If a `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` sits in the repo root, Claude Code reads it and skips `AGENTS.md`. The command prints a note that names the import line to add to that file.

## The git hook

The hook runs `uv run ka runtime --verify` on every commit, including a commit that only touches a generated file or only deletes a node.

- A file that differs from a fresh generation is rewritten and fails with `changed`, so a hand edit is gone and you stage the result.
- A file no node generates any more is removed and fails with `changed`.
- A generated file that the git index doesn't hold fails with `not-staged`. Otherwise a new node could land without its file.

`--verify` can't run with `--proposals`. The generated files are excluded from every other pre-commit hook, because `mdformat` and the whitespace hooks would rewrite node text in them and the two hooks would never agree.

## How Claude Code loads the files

From the Claude Code docs on 2026-11-05:

| What loads                      | When it loads                                                                                                               | Who decides |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------- |
| The root `AGENTS.md`            | At session start, if no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` takes its place. Needs v2.1.277 or later.    | The tool    |
| Each skill name and description | At session start, in a listing with a budget of 1% of the context window. On overflow the least-used descriptions go first. | The tool    |
| A folder `AGENTS.md`            | When the agent opens a file in that folder with the Read tool, if the folder has no `CLAUDE.md`                             | The tool    |
| A rule with `paths`             | When the agent uses the Read, Write, or Edit tool on a matching file, or reads one file with a shell command                | The tool    |
| A rule without `paths`          | At session start                                                                                                            | The tool    |
| A skill body                    | When the agent uses the skill                                                                                               | The agent   |
| A node behind a text pointer    | When the agent opens it                                                                                                     | The agent   |

And after compaction:

| What                                          | What happens                                                                            |
| --------------------------------------------- | --------------------------------------------------------------------------------------- |
| A root `CLAUDE.md` and a rule without `paths` | Injected again from disk                                                                |
| The skill listing                             | Rebuilt and injected again                                                              |
| A skill body                                  | Injected again, up to 5,000 tokens for each skill and 25,000 in total, oldest out first |
| A rule with `paths` and a folder file         | Gone from the context until a matching file loads it again                              |

Patterns in `paths` start from the folder that holds `.claude`. The docs show `src/**/*`, so write that form rather than `src/**`.

The **Project instructions** setting in Claude Code can turn off `AGENTS.md`, and some subagents start without project instructions. Neither shows up in the generated files.

## Use it from code

```python
from pathlib import Path

from knowledge_architecture.runtime import generate_runtime

report = generate_runtime(Path(), proposals=False, verify=False)
report.problems  # the same problems that ka runtime prints
report.written   # the files this run changed
report.removed   # the stale files this run removed
```

`build_view` in `runtime/view.py` holds the graph logic and names no file of any tool. `runtime/claude_code.py` and `runtime/templates/claude_code/` hold the Claude Code target, so another tool needs a new target and no change to the graph.

## Codes

These codes come from this command. Each other code comes from a check that the command runs.

| Code            | What it reports                                                                       |
| --------------- | ------------------------------------------------------------------------------------- |
| `not-generated` | A generated path holds a file without the marker, a folder, or a symbolic link        |
| `link`          | A generated file links to a path that doesn't exist in the repository                 |
| `size`          | The directives of a skill, or a whole rule or folder file, go over the limit          |
| `changed`       | With `--verify`, a file differed from a fresh generation, or no node generates it now |
| `not-staged`    | With `--verify`, the git index doesn't hold a generated file                          |
| `write`         | The command can't change a path, because a file or a permission blocks it             |

A link in the body of a node resolves from the generated file, not from the node file, so it usually fails with `link`. To reach another node, add a pointer.

## What it does not check yet

- Whether a pattern in `paths` matches any file, or matches what the author meant.
- Whether a skill ID is one that Claude Code reserves. It skips a skill named `synced` or `anthropic-skills`.
- The size of the root. The Claude Code docs suggest under 200 lines, and they name no limit that cuts this file.
- Whether a token estimate holds. The 15,000 characters are an estimate, and a text with many long links can use more tokens for each character.
- Whether a stale file that you deleted but didn't stage is gone from the commit, in `pre-commit run --all-files`. A real commit restores the file first, so the hook then removes it and fails.

## What only a real session can show

This layer has been tested by reading the generated bytes, not by running a model. These points rest on the Claude Code docs, and only a real session can confirm them:

- That the tool loads the root and lists both skills.
- That a read in a deep node loads the folder files above it as well as its own. The file lists are complete for each node, so the result is correct either way, and the cost differs.
- That `governance/**/*` loads the governance rule.
- That a root `AGENTS.md` is injected again after compaction. The docs state this for a root `CLAUDE.md`.
- That an agent follows a pointer when its trigger holds. The [graph checks](graph-checks.md) prove that every node can be found, not that it gets read.
