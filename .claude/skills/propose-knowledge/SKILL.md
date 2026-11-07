---
name: propose-knowledge
description: "Convert a correction or a repeated note into one small knowledge proposal. Use when a person corrects your work."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Propose knowledge

If compaction cuts this skill, invoke the skill again.

## Directives

No directive is in force at this node.

## Inputs

- The signal: a correction in this session, or a note in auto memory
- The auto memory folder of the project, as `### Auto memory` describes it
- The node files under `knowledge/`

In a project, run the engine as `knowledge/.densho/densho`. In the template repo, use `uv run densho` in its place.

## Procedure

### Remove the notes of decided proposals

1. Find each note in the auto memory folder that holds a line that starts with `Proposal:`.
2. Find the entity of each ID on that line in `knowledge/`.
3. If no ID on the line is still `proposed`, remove the note file and its line in `MEMORY.md`.
4. Run the search from `### Signal search` to find each node with a `## Signals` section.
5. Remove each citation line whose ID is not `proposed`. Keep a line of the class `eval` while its directive is `accepted`.
6. Remove the heading when no line stays.
7. Tell the person which notes and which citation lines you removed.

### Classify the signal

1. State the signal in one sentence, in your own words, with no name and no email.
2. Put the signal in one class from `### Signal classes`.
3. If the class is `preference`, stop. Auto memory keeps the note.
4. Run the search from `### Rejected entities`. Read the text and the `rejection_reason` of each hit.
5. If a `rejected` entity states the same change, stop. Tell the person its ID and its `rejection_reason`.
6. Run `knowledge/.densho/densho governance --pending`. If a proposal states the same change, add this signal to its line in `## Signals`, and stop.
7. If an `accepted` directive states the same change, stop. Tell the person its ID.

### Find the place

1. Find the workspace node whose definition covers the subject of the signal.
2. For a rule that covers each task in the project, use the root `knowledge/node.md` with `scope: node`.
3. If no workspace node covers the subject, add one `densho:PracticeArea` node under the domain of the project.
4. If the project has no domain node, add one in the form of `### Domain node`, with a pointer from the root.
5. Set `knowledge_type: workspace` and `origin: project` on each node that you add.

### Write the proposal

1. Make the change that `### Signal classes` gives for the class. Change only the lines that the change needs.
2. Give each new entity an `id` that no node or directive holds. The search in `### IDs` finds a collision.
3. Set `status: proposed` and `origin: project` on each new entity.
4. Set `basis: judgment` on a new directive, and leave out `sources`, unless you open a source that states the rule.
5. If the change touches a field of an `accepted` entity that needs review, set its `status` to `proposed`.
6. Add the citation to `## Signals` at the end of the body of the node, in the form of `### Citation`.
7. If auto memory holds the note of this signal, add the line `Proposal: <id>` to the note.

### Check the proposal

1. Run `knowledge/.densho/densho runtime`. It runs each check.
2. Correct each problem from the first line down. Keep the meaning of the signal.
3. If a directive fails with `opening`, add its verb to `knowledge/governance/language/branches/<node-id>.yaml`.
4. If `2` edits of a directive fail, remove the proposal. Tell the person the problem.
5. Run `git diff` and read each changed line.

### Report the proposal

1. Tell the person the class, the change, and the node.
2. Tell the person that the proposal is not in force until a person accepts it.
3. If you reopened an `accepted` entity, tell the person that it is out of force until a person accepts it again.
4. If the change is a body edit or a step in a skill, tell the person that the commit puts it in force with no review.
5. Report each verb that you added to a vocabulary file. No `status` covers that file.
6. Ask the person whether to commit the proposal now. `knowledge/.densho/densho accept` reads the proposal from the last commit.
7. Tell the person to read the queue with the `review-proposals` skill.

## Output

One proposal in the working tree that passes each check, with one citation line for its signal. Or no change, and the reason for it.

## Validation

The diff holds only the lines of one proposal and its citation. A rewrite of a whole node, a citation with a name or an email, or a repeat of a `rejected` entity fails the job.

## References

### Signal classes

| Class        | Signal                                                      | Change                                                                       |
| ------------ | ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `preference` | a choice for one task, or a habit of one person             | No change. Auto memory keeps the note.                                       |
| `fact`       | a statement about the project that stays true               | An edit of the definition, or a line under `## References` in the body       |
| `procedure`  | the same ordered steps a second time                        | A step in a skill, or a new `densho:Skill` node                              |
| `rule`       | an "always" or a "never", or the same mistake a second time | A directive                                                                  |
| `exception`  | a "not here" for a directive that applies at a node         | An entry in `exceptions` of the node, with the reason that the person states |

- A new skill uses a part of the listing budget. Prefer a step in a skill that exists.
- A new skill gets `invocation: person` when its job changes something outside the repo. Each other skill gets `invocation: agent`.
- A body edit and a step in a skill need no review. Show the diff to the person before the commit.

### Citation

```markdown
## Signals

- `use-pnpm`: 2026-11-06, rule. The agent ran `npm install`. The person said that the project always uses `pnpm`.
```

- Write one line for each proposal: the ID, the date, the class, and the signal in your own words.
- Do not write a name, an email, a handle, or a link to a session.
- `## Signals` is the last section of the body. A body edit needs no review, so the line does not reopen the node.

### Signal search

```sh
git grep -l -E '^## Signals$' -- knowledge/
```

Read the `## Signals` section of each file that the search lists. Each citation line starts with the ID in backticks. Skip a hit inside a code block of a skill.

### Rejected entities

```sh
git grep -n 'status: rejected' -- knowledge/
```

Each hit is the status line of a node, a directive, or an exception. Its `rejection_reason` is on the next lines. A hit inside a code block of a skill is an example. Skip it.

### IDs

An `id` is a lowercase slug with hyphens. Replace `<id>` with the new ID. The search prints nothing when the ID is free. A hit inside a code block of a skill is an example, not a collision.

```sh
git grep -n -E -e '\^<id>$' -e '^id: <id>$' -- knowledge/
```

### Domain node

Add `knowledge/nodes/<project-id>/node.md` with this front matter. Then add `## Definition` with one sentence about the project.

```yaml
id: my-project
kind: densho:Domain
title: My project
status: proposed
origin: project
knowledge_type: workspace
```

Add this pointer to `pointers` in `knowledge/node.md`:

```yaml
- kind: densho:TextPointer
  target: my-project
  trigger: You change the code of this project.
```

### Auto memory

- Claude Code writes notes in `~/.claude/projects/<project>/memory/`. The setting `autoMemoryDirectory` can name another folder.
- `MEMORY.md` is the index. It holds one line for each note.
- Each note is one Markdown file with a `type` in its front matter: `user`, `feedback`, `project`, or `reference`. A `feedback` note holds a correction.
- A note belongs to one person on one machine. Write the signal in your own words. Do not copy the note into a node.

## References

- Read [Change rules](../../references/change-rules.md).
- Read [Language rules](../../references/language-rules.md).
- Read [Lifecycle](../../references/lifecycle.md).
