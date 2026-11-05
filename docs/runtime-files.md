# Runtime files

> **In the library:** the signs that lead a visitor to the right shelf. This is the first layer an agent feels, because the signs are what it reads.

**Status:** Planned. Nothing on this page exists yet. The repo has no `AGENTS.md` until this layer generates it.

## What it does

This layer will generate the files an agent tool loads: the root `AGENTS.md`, folder `AGENTS.md` files, path rules, and skills. These files are output, so a change goes in the graph and the build writes them again.

## How it works

The agent tool loads these files with its own mechanisms, and no hook injects context. The graph itself does not depend on any one tool, and Claude Code is the first target. In Claude Code, the files load like this:

| What loads                      | When it loads                                                                | Who decides |
| ------------------------------- | ---------------------------------------------------------------------------- | ----------- |
| The root `AGENTS.md`            | At session start, if no `CLAUDE.md` or `CLAUDE.local.md` takes its place     | The tool    |
| Each skill name and description | At session start, in a listing with a size budget                            | The tool    |
| A folder `AGENTS.md`            | When the agent reads a file in that folder, if the folder has no `CLAUDE.md` | The tool    |
| A path rule                     | When the agent reads, writes, or edits a matching file                       | The tool    |
| A skill body                    | When the agent uses the skill                                                | The agent   |
| A node behind a text pointer    | When the agent opens it                                                      | The agent   |

The root `AGENTS.md` is the root node of the graph. It holds only what an agent cannot work out from the files, and it names each preset skill so an agent can still find one if the tool drops its description. Setup, paths, and commands stay in the README.

Each file puts its directives first, then its procedures, then its references.

## How it fits

The agent still chooses which pointers to follow, so the [graph checks](graph-checks.md) prove that every node can be found, not that it gets read. The system does not pick the knowledge for a task on the agent's behalf.

A skill is an entry point in the middle of the tree, so the build has to give it the directives it inherits from [directive semantics](directive-semantics.md).

## Not settled yet

- Whether a skill gets a copy of its inherited directives or a list of required reads
