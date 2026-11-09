---
name: evaluate-knowledge
description: "Run the eval tasks of a discipline with and without its directives, and propose deprecations. Use when a person asks whether the directives of a discipline help."
disable-model-invocation: true
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Evaluate knowledge

## Directives

From [Governance](../../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit

From [Change rules](../../references/change-rules.md):

- Change only `status` on an entity in the commit that accepts it. ^accept-in-its-own-commit
- Set `status` to `proposed` when you change the text, the scope, the basis, or the attachments of an `accepted` directive. ^reopen-a-directive
- Set `status` to `proposed` when you change the definition, the kind, or an edge of an `accepted` node. ^reopen-a-node
- Set `status` to `proposed` when you change the invocation or a script of an `accepted` skill. ^reopen-a-skill
- Set `status` to `proposed` when you change the reason of an `accepted` exception. ^reopen-an-exception
- Keep `status` when you change only a title, a body, a pointer, a source, or a rejection reason. ^routes-need-no-review

From [Lifecycle](../../references/lifecycle.md):

- Before you remove an `accepted` node or directive, set its `status` to `deprecated`. ^deprecate-before-removing
- Do not apply a `deprecated` node or directive to new work. ^deprecated-is-for-reference
- Keep the `id` of a node or a directive when you move its file. ^keep-the-id
- Do not change the `origin` of a node or a directive. ^keep-the-origin
- Before you deprecate a node, move the nodes under it. ^move-before-deprecating
- Follow a directive while its exception stays `proposed`. ^proposed-exception-stops-nothing
- Treat a `proposed` directive as a draft, not as a rule, unless a person stated it in the current session. ^proposed-is-a-draft
- Before you reject a node, leave no `proposed` or `accepted` directive or exception in it. ^reject-the-contents
- Do not apply a `rejected` node or directive to any work. ^rejected-applies-nowhere
- Before you reject an entity, remove each reference to it from the entities that are not `rejected`. ^remove-references-before-rejecting
- Set `status` to `proposed` on each new node, directive, and exception. ^start-as-proposed
- Set `rejection_reason` on each `rejected` node, directive, and exception. ^state-the-rejection-reason
- Set `origin` to `project` on each entity in workspace knowledge. ^workspace-is-project

From [Evaluate knowledge](SKILL.md):

- Before you run an eval, ask the person for the budget in USD. ^ask-for-the-eval-budget
- Do not start a paid eval run before the dry run passes. ^dry-run-first
- Do not change a `status` when you propose a deprecation. ^no-status-change-in-an-eval
- Report the counts of each directive as raw counts, with no claim of significance. ^raw-eval-counts

## Inputs

- The discipline: the ID of a folder in `knowledge/evals/`
- The count of runs of each task in each condition, and the budget of the person in USD
- The `claude` command on the `PATH`, with a login

In a project, run the engine as `knowledge/.densho/densho`. In the template repo, use `uv run densho` in its place.

## Procedure

### Check the tasks

1. Run `knowledge/.densho/densho eval --check`. It grades the known good output and the known bad output of each task, with no model call.
2. If it reports a problem, stop. Tell the person each problem.
3. Ask the person for the discipline, the count of runs, and the budget.
4. Tell the person the count of runs: `2` canary runs, then each task once in each condition for each repeat.

### Prove the isolation

1. Run `knowledge/.densho/densho eval --discipline <id> --dry-run`. It checks the login, builds the two conditions, and probes each run folder. The check and the probes cost `0` USD.
2. If the dry run reports the code `login`, stop. Tell the person that the `claude` command has no login in the run environment.
3. If the dry run reports another problem, stop. Tell the person each problem, with its code from `### Isolation`.

### Run the eval

1. Run the command from `### Commands` with the budget of the person. The command can run for many minutes, so run it in the background.
2. The command runs the canary first. If the canary fails, the command stops. Tell the person the canary problem, and do not run the command again.
3. Read `report.md` in the work folder that the command names.

### Report the result

1. Show the person the table of directives from `report.md`: the passes and the runs in each condition.
2. State that the sample is small and that the counts show no significance.
3. Name each run with an error, and its detail. An error is not a pass or a fail.
4. State the cost of each run and the total cost.

### Propose deprecations

1. Read the lines under `## Deprecation candidates` in `report.md`.
2. For each line, find the node that holds the directive. The search in `### Directive search` finds it.
3. Copy the line to `## Signals` at the end of the body of that node. Add the heading if the node has none.
4. Do not change the `status` of the directive. The line is a body edit, so it needs no review.
5. Run `knowledge/.densho/densho runtime`. Correct each problem from the first line down.
6. Show the person `git diff`, and ask whether to commit the lines now.
7. Tell the person to read the proposals with the `review-proposals` skill.

## Output

A report with raw counts for each directive and each condition, and the cost of each run. One `eval` line in `## Signals` for each deprecation candidate. Or no change, and the reason for it.

## Validation

The diff holds only `## Signals` lines with the class `eval`. No `status` changes. The report states the cost of each run and makes no claim of significance.

## References

### Conditions

- "With": each directive of the discipline is in force. The command accepts them in a copy of `knowledge/` under the work folder.
- "Without": no directive of the discipline is in force. The command sets them to `proposed` in a second copy.
- A run folder holds only the generated runtime files of its condition and the fixture of its task. It holds no `knowledge/`.
- The command never accepts or changes an entity in the project tree.

### Isolation

| Code           | Leak                                                    |
| -------------- | ------------------------------------------------------- |
| `memory-file`  | an instruction file from outside the run folder         |
| `instructions` | no `AGENTS.md` of the run folder                        |
| `skill`        | a skill of the person or of a plugin                    |
| `plugin`       | a plugin that is not built in                           |
| `mcp`          | an MCP server                                           |
| `agent`        | a custom agent                                          |
| `output-style` | an output style other than the default                  |
| `tool`         | a tool that the task does not name                      |
| `auto-memory`  | an auto memory folder for the run folder                |
| `git-identity` | a git user other than the neutral identity of the eval  |
| `probe`        | a probe that did not finish, or a probe that cost money |

### Deprecation candidate

- A candidate has `1` or more runs in each condition, and no error.
- Its passes with the discipline in force are not above its passes without it, as a share of the runs.
- The line has this form:

```markdown
- `<id>`: <date>, eval. With the discipline in force, <a> of <n> runs passed. Without it, <b> of <n> runs passed.
```

### Commands

```sh
knowledge/.densho/densho eval --check
knowledge/.densho/densho eval --discipline <id> --dry-run
knowledge/.densho/densho eval --discipline <id> --runs <n> --budget <usd>
knowledge/.densho/densho eval --discipline <id> --task <task-id> --runs <n> --budget <usd>
```

- `--run-budget` sets `--max-budget-usd` of each run. The default is `0.5` USD.
- The command does not start a run when the spend so far plus the run budget passes `--budget`.
- `--model` names the model of each run. The default is `sonnet`.
- `--work` names the work folder. The default is `build/eval/<time>/`.

### Directive search

```sh
git grep -n -E '\^<id>$' -- knowledge/
```

## References

- Read [Change rules](../../references/change-rules.md).
- Read [Lifecycle](../../references/lifecycle.md).
