# Runtime files

> **In the library:** the signs that lead a visitor to the right shelf. This is the first layer an agent feels, because the signs are what it reads.

**Status:** Built.

This layer generates the files an agent tool loads: the root `AGENTS.md`, a reference page for most nodes, path rules, and skills. Claude Code is the first target, and no hook injects context, because the tool loads these files with its own mechanisms. The code is in `engine/runtime/`.

The generated files sit in `AGENTS.md` and `.claude/`, and none of them sits in `knowledge/`. They are output, and the repo still commits them, because an agent tool reads them straight from a clone. A node file stays the source, so a change goes in the node and the command writes the file again. A hand edit doesn't survive.

## Generate

```sh
uv run ka runtime
```

```text
wrote AGENTS.md
wrote .claude/skills/design-settings-interface/SKILL.md
406 entities wait for review. Run uv run ka governance --pending to list them.
in_force: 59 files, 2 written, 0 removed, 0 problems
```

The command compiles the graph with the same code as `ka build`, so it runs every check on one reading of the tree. It writes each file that differs and removes each file of its own that no node generates any more. A second run changes nothing.

The count of entities that wait for review is a reminder. It never fails the run, and it doesn't print when the tree fails a check.

A tree that fails a check leaves the committed files alone, so an agent keeps its entry point while you repair a node. An empty tree removes every generated file and passes, so a project can still remove what it received.

## What each node becomes

| Node                               | Generated file                                  | How it loads                              |
| ---------------------------------- | ----------------------------------------------- | ----------------------------------------- |
| The root                           | `AGENTS.md`                                     | At session start                          |
| A skill                            | `.claude/skills/<id>/SKILL.md`                  | The agent picks it from the skill listing |
| The target of a `ka:PathPointer`   | `.claude/rules/knowledge/<id>.md` with `paths`  | When the agent touches a matching file    |
| The target of a `ka:AlwaysPointer` | `.claude/rules/knowledge/<id>.md` without paths | At session start                          |
| Any other node                     | `.claude/references/<id>.md`                    | When the agent follows a link to it       |

A `ka:TextPointer` adds no file. It becomes a line that holds the trigger and a link, such as `You decide how a screen looks. Read [Visual design](visual-design.md).`, and following that link opens the reference page of the node.

A node file names its pointer targets by ID. The generated files turn each ID into the path of its generated file, so each link in a generated file goes to another generated file, and no link goes to a node file. The root links each domain and the governance, and names each skill with no link. A skill also links the page of each node in `uses`.

A skill behind a path or always pointer gets both a skill file and a rule, and a link to it goes to the rule. A path rule also matches its own node file.

A skill with `invocation: person` gets `disable-model-invocation: true` in its front matter, so the agent doesn't start it by itself. A person starts it with `/<id>`. The root adds `Only a person can start this skill.` to its line.

## What a file holds

Each file puts its directives first, then its procedures, then its references.

| File           | Holds                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------- |
| Root           | The state of the graph, its directives, the body of `knowledge/node.md`, the domains, the governance, and the skills |
| Skill          | Its directives and exceptions, its body, its pointers, and a link to each node in `uses`                             |
| Path rule      | Its directives and exceptions, the definition, the body, and its pointers                                            |
| Reference page | Its directives and exceptions, the definition, the body, and its pointers                                            |

The root holds only what an agent can't work out from the files. It names each domain, the governance node and its policies, and each skill with its description, so an agent can still find a skill if the tool drops its description. Setup, paths, and commands stay in the README and in these pages. The architecture facts come from the body of `knowledge/node.md`. A body change needs no review, so a reviewer reads it in the diff.

A directive list holds what applies at that node and nothing else: inherited directives, attached ones, and `applies`, minus each one an [exception](directive-semantics.md#stepping-out) stops. Each directive keeps its `^id`, and each group links to the generated file of the node that holds it. A list is complete for its own node, so the files for a node and its parent can repeat a line.

## Nothing is in force yet

The default result holds only what the [governance workflow](governance-workflow.md) puts in force. Every seed entity is still `proposed`, so today the committed files hold the nodes and the pointers but no directive. The root says so plainly, so an agent doesn't assume a rule:

```text
No directive is in force. The graph holds 487 directives and 1 exception that are not in force.

Treat a directive as a rule only when its `status` is `accepted`. A generated file lists only the directives that apply at its own node.
```

A node file still shows each proposal, with its `status`. That is the reason for the second sentence.

After you [accept something](human-interface.md#accept-what-you-approve), run `uv run ka runtime` and stage the result in the same commit.

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
| `.claude/references/<id>.md`      | `build/runtime-proposals/claude/references/<id>.proposals.md`      |

Each link in the copy goes to another file of the copy. A link in the body of a node keeps its text, so it fails with `link` in the copy even when it passes in the committed files. No node body holds a link today. A tree that fails a check removes the copy.

The [review queue](human-interface.md#read-the-knowledge) lists the same effect for each entity, and names the generated files it reaches.

## Why a skill holds a copy

A skill is an entry point in the middle of the tree, so it has to carry the directives that reach it. The build copies them into the skill file. It links the page of each node in `uses` too, but the skill doesn't depend on a read.

Compaction decides this. After compaction, Claude Code re-attaches each invoked skill and keeps the first 5,000 tokens, while it restores only a few of the files an agent read. A required read also leaves the choice to the agent, and a node file holds proposals and rules that an exception stops. `design-settings-interface` draws 63 directives from 11 nodes, so a list of reads would be the weaker answer.

The directives sit directly after the title, so they are the part that compaction keeps. The build fails with `size` if the title and the directives of a skill take more than 15,000 characters. That is 3 characters for each of the 5,000 tokens, a low estimate on purpose, because the repo has no tokenizer. The procedure comes after the directives, so a long one can still be cut. A skill says near its top that the agent can invoke it again, and the root says the same, because the oldest skill can drop out entirely. A person skill tells the agent to ask the person instead.

Two line budgets also fail with `size`: 200 lines for the root `AGENTS.md`, from the Claude Code memory docs, and 500 lines for a `SKILL.md`, from the Agent Skills specification. A reference page has no line budget, only its 40,000 characters. A file over a budget means the node holds too much, so the message asks you to move knowledge out of it or attach fewer directives. The review copy follows the same budgets.

The copy can't go stale, because the hook compares it with a fresh generation on each commit.

## Skill scripts

A skill can ship scripts. Put them in `scripts/` in the skill's node folder, and the command copies the folder byte for byte to `.claude/skills/<id>/scripts/`, next to `SKILL.md`. Each copy keeps the executable bit of its source. A link in the skill body to `scripts/check.py` resolves, because the copy is a file the generator writes.

The generator owns the copied folder while the `SKILL.md` beside it holds the marker. It removes each file there that the source doesn't have, including one you put there by hand, so keep your scripts in the source folder. It leaves alone a file that git ignores, such as `__pycache__/`, and the `scripts/` folder of a skill you wrote yourself. A hand-written file at a path that the copy needs fails with `not-generated`.

A script change reopens the review of the skill. See [governance workflow](governance-workflow.md#change-something-accepted). The checks never read a script, so a reviewer reads each one. The review copy holds the scripts too, under `build/runtime-proposals/claude/skills/<id>/scripts/`.

## Hand-written files

A generated file holds one marker line: the first line, or the first line after the front matter. The generator changes or removes a file only if it holds that marker, so your own files are safe:

- A rule directly in `.claude/rules/`, a skill folder of your own, a page of your own in `.claude/references/`, and an `AGENTS.md` in a subfolder outside `knowledge/` all stay as they are.
- A file without the marker at a generated path fails with `not-generated`, and the run writes nothing. Move the file, then run again.
- A symbolic link in a generated path fails the same way, so the generator can't write through a link to another file.

No generated file sits in `knowledge/`. A Markdown file there must be `node.md`, so the parser fails any other one with `file-name`, with the marker or without it.

If a `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` sits in the repo root, Claude Code reads it and skips `AGENTS.md`. The command prints a note that names the import line to add to that file, and the note stops once a file imports the root. In a project, [`ka adopt`](template-packaging.md#your-own-files) adds the line for you.

## The git hook

The hook runs `uv run ka runtime --verify` on every commit, including a commit that only touches a generated file or only deletes a node.

- A file that differs from a fresh generation is rewritten and fails with `changed`, so a hand edit is gone and you stage the result.
- A file no node generates any more is removed and fails with `changed`.
- A generated file that the git index doesn't hold fails with `not-staged`. Otherwise a new node could land without its file.

`--verify` can't run with `--proposals`. The generated files are excluded from every other pre-commit hook, because `mdformat` and the whitespace hooks would rewrite node text in them and the two hooks would never agree.

## How Claude Code loads the files

From the Claude Code docs on 2026-11-05:

| What loads                      | When it loads                                                                                                                                                                                       | Who decides |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| The root `AGENTS.md`            | At session start, if no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` takes its place. Needs v2.1.277 or later.                                                                            | The tool    |
| Each skill name and description | At session start, in a listing with a budget of 1% of the context window. On overflow the least-used descriptions go first. A skill with `disable-model-invocation: true` stays out of the listing. | The tool    |
| A rule with `paths`             | When the agent uses the Read, Write, or Edit tool on a matching file, or reads one file with a shell command                                                                                        | The tool    |
| A rule without `paths`          | At session start                                                                                                                                                                                    | The tool    |
| A skill body                    | When the agent uses the skill                                                                                                                                                                       | The agent   |
| A reference page behind a link  | When the agent opens it                                                                                                                                                                             | The agent   |

And after compaction:

| What                                          | What happens                                                                            |
| --------------------------------------------- | --------------------------------------------------------------------------------------- |
| A root `CLAUDE.md` and a rule without `paths` | Injected again from disk                                                                |
| The skill listing                             | Rebuilt and injected again                                                              |
| A skill body                                  | Injected again, up to 5,000 tokens for each skill and 25,000 in total, oldest out first |
| A rule with `paths`                           | Gone from the context until a matching file loads it again                              |
| A reference page                              | Gone from the context unless the tool restores it with the few files it keeps           |

Patterns in `paths` start from the folder that holds `.claude`. The docs show `src/**/*`, so write that form rather than `src/**`.

The **Project instructions** setting in Claude Code can turn off `AGENTS.md`, and some subagents start without project instructions. Neither shows up in the generated files.

## Use it from code

```python
from pathlib import Path

from engine.runtime import generate_runtime

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
| `link`          | A generated file links to a path where the generator writes no file                   |
| `size`          | A file goes over its character limit, or the root or a skill over its line budget     |
| `changed`       | With `--verify`, a file differed from a fresh generation, or no node generates it now |
| `not-staged`    | With `--verify`, the git index doesn't hold a generated file                          |
| `write`         | The command can't change a path, because a file or a permission blocks it             |

A link in the body of a node resolves from the generated file, not from the node file, and it has to go to another generated file. A link to a node file, a doc, or a source file fails with `link`. To reach another node, add a pointer. To name a file, write its path in a code span.

## What it does not check yet

- Whether a pattern in `paths` matches any file, or matches what the author meant.
- What a script does, or whether a script that git ignores in the source should ship.
- Whether a token estimate holds. The 15,000 characters are an estimate, and a text with many long links can use more tokens for each character.
- Whether a stale file that you deleted but didn't stage is gone from the commit, in `pre-commit run --all-files`. A real commit restores the file first, so the hook then removes it and fails.

## What only a real session can show

This layer has been tested by reading the generated bytes, not by running a model. These points rest on the Claude Code docs, and only a real session can confirm them:

- That the tool loads the root and lists each skill.
- That `knowledge/**/*` loads the governance rule.
- That a root `AGENTS.md` is injected again after compaction. The docs state this for a root `CLAUDE.md`.
- That an agent follows a pointer when its trigger holds. The [graph checks](graph-checks.md) prove that every node can be found, not that it gets read.
