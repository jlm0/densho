# Evaluation

> **In the library:** the reader test. Two groups of visitors do the same job, one with the signs up and one with the signs down, and the librarian counts who gets it right. A sign that makes no difference becomes a candidate for removal.

**Status:** Built.

A rule can read well and still change nothing. The model may do the right thing anyway, or it may ignore the rule. The only way to tell is to run the same task with the rule and without it, and compare. This layer does that for one discipline at a time, and turns a rule that shows no gain into a proposal to deprecate it.

## The eval tasks

Each task is a folder `knowledge/evals/<discipline>/<task>/`:

| Path        | What it holds                                                                  |
| ----------- | ------------------------------------------------------------------------------ |
| `task.yaml` | The title, the prompt, the tools the run gets, and the targets                 |
| `fixture/`  | The files the run starts with. A task can do without it.                       |
| `good/`     | A known good output: the files a run writes, and `reply.md` for its last reply |
| `bad/`      | A known bad output, in the same form                                           |

```yaml
title: Write the commit message of a change that breaks callers
prompt: |
  Write the commit message for the change that `CHANGE.md` describes.
  Write only the message to the file `COMMIT_MSG`, with no code fence.
tools: [Read, Write]
targets:
  - directive: mark-breaking-change
    checks:
      - path: COMMIT_MSG
        contains: '\A[a-z]+(\([^()\n]+\))?!: \S|^BREAKING[ -]CHANGE: \S'
```

A target names one directive of the discipline and the checks that show whether a run followed it. Each check is a regular expression over the output:

- `contains` needs at least `min` matches, 1 by default, and at most `max` when you set it.
- `lacks` allows no match.
- `path` is a glob from the root of the run folder, or `@reply` for the last reply of the agent.
- A check fails when no file matches its `path`, so a run that writes nothing can't pass a `lacks` check.
- Each target needs at least one `contains` check, and it passes when every check passes.

`tools` takes `Read`, `Write`, `Edit`, `Glob`, `Grep`, and `Bash`. A run gets the tools you list and nothing else, so leave `Bash` out unless the task needs it.

The grader is code in the engine. A task holds no code, so a task can't run anything on your machine. The grader reads only regular files inside the run folder, at most 256 KiB of each, and doesn't follow a symbolic link.

The parser skips `knowledge/evals/`, so a Markdown file in a task isn't a node. The secret and email checks still read every file there. A task can't hold `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `.claude/`, `.git/`, or `.mcp.json`, because those would change what the run loads.

Each discipline has one canary task. It asks which rules of the project apply to a topic, by ID, and its target ID appears nowhere in the generated files unless the discipline is in force. So it can pass only when the rules are loaded.

The template ships four tasks for each discipline: the canary and three tasks whose rules leave a trace that a regular expression can find. A project receives the tasks of the disciplines it takes.

## Check the tasks

```sh
uv run densho eval --check
```

It loads each task, checks that each target names a `proposed` or `accepted` directive under the discipline, and grades `good/` and `bad/`. Each target must pass on the good output and fail on the bad one, so a grader that passes everything, or nothing, fails the check. It makes no model call. The `eval-tasks` hook runs it on each commit, in the template and in each project.

## Run an eval

An eval spends money, so only a person starts one. In a project, run `/evaluate-knowledge`. The skill asks for the discipline, the runs, and your budget, runs the dry run first, and reports the result. By hand:

```sh
uv run densho eval --discipline software-engineering --dry-run
uv run densho eval --discipline software-engineering --runs 3 --budget 5
```

| Option         | What it sets                                                         | Default              |
| -------------- | -------------------------------------------------------------------- | -------------------- |
| `--runs`       | The runs of each task in each condition. The canary runs once.       | `1`                  |
| `--budget`     | The most the batch spends, in USD. No run starts past it.            | `5`                  |
| `--run-budget` | The `--max-budget-usd` of each run                                   | `0.5`                |
| `--model`      | The model of each run                                                | `sonnet`             |
| `--task`       | Runs only this task, with the canary. Repeat it for more tasks.      | every task           |
| `--timeout`    | The seconds before a run stops                                       | `900`                |
| `--work`       | A new or empty folder for the copies, the runs, and the report       | `build/eval/<time>/` |
| `--dry-run`    | Builds the conditions and probes each run folder, with no model call | off                  |

The command needs the `claude` command on your `PATH`, signed in.

### The two conditions

The command copies `knowledge/`, without the tasks, twice into the work folder. In the "with" copy it accepts the subtree of the discipline, as `densho accept --subtree` would. In the "without" copy it sets each accepted directive of the discipline to `proposed`. Nothing else differs, and a skill's own directives keep their status in both. It never accepts or changes anything in your own tree, and it refuses a work folder inside `knowledge/`.

Each run gets a fresh folder with the generated files of its condition and the fixture of its task, committed as its own git repo. The folder holds no `knowledge/`, because a node file names each directive with its status, and the "without" agent could read it there.

### Isolation

Each run is `claude -p` with `--setting-sources project`, `--strict-mcp-config`, `--no-session-persistence`, `--max-budget-usd`, the tools of the task, and settings that turn off auto memory and exclude every `CLAUDE.md`, `AGENTS.md`, and `.claude/rules/` above the run folder. It gets only `HOME`, `USER`, `PATH`, `LANG`, `TERM`, and the variables that turn off auto memory and point git at an empty global config. No other variable of your session reaches it. Claude Code needs `USER` to find your login in the macOS keychain.

Before it builds the conditions, the command runs `claude auth status` with the same environment. This check is free. The command keeps only the exit code, because the output holds your account email. If you aren't signed in, the eval stops with `login` before any probe.

Before each run, a free probe runs `/context all` with the same flags and reads what the session would load. The run starts only when the probe finds none of these:

| Code           | Leak                                                         |
| -------------- | ------------------------------------------------------------ |
| `memory-file`  | An instruction file from outside the run folder              |
| `instructions` | No `AGENTS.md` of the run folder                             |
| `skill`        | A skill of yours or of a plugin, or one the run folder lacks |
| `plugin`       | A plugin that isn't built in                                 |
| `mcp`          | An MCP server                                                |
| `agent`        | A custom agent                                               |
| `output-style` | An output style other than the default                       |
| `tool`         | A tool other than the ones the task names and `Skill`        |
| `auto-memory`  | An auto memory folder for the run folder                     |
| `git-identity` | A git user other than the neutral one                        |
| `probe`        | A probe that didn't finish, or one that cost money           |

Each throwaway repo commits as `eval` with an `example.invalid` address, and git reads an empty global config, so your name and email never reach a run. The work folder sits inside your project, though, so its path holds your account name, and Claude Code sends the working folder to the model. `USER` holds the account name too.

### Order and budget

The canary runs first, once with and once without. It must pass with the discipline and fail without it, or the batch stops there. Then each task runs in both conditions for each repeat, taking turns: with, without, with, without. A run that could push the spend past `--budget` doesn't start.

## Read the report

The command writes `report.md` and `report.json` to the work folder. For each directive it gives the passes and the runs in each condition as raw counts, and for each run its status, its cost from `total_cost_usd`, and why it failed. A run that ends with an error, a time-out, or the end of its budget counts as an error, apart from the passes and fails.

The report makes no claim of significance. With a few runs, a gap of one or two passes can be chance.

## Propose a deprecation

A directive is a candidate when it ran in both conditions with no error, and its share of passes with the discipline is no higher than without it. The report gives a line for each candidate:

```markdown
- `mark-breaking-change`: 2026-11-06, eval. With the discipline in force, 3 of 3 runs passed. Without it, 3 of 3 runs passed.
```

`/evaluate-knowledge` copies the line to `## Signals` of the node that holds the directive. It changes no status. For an accepted directive, `/review-proposals` lists the line as a proposal to deprecate it, and you decide: deprecate it and remove its eval targets, or keep it and drop the line. `propose-knowledge` keeps the line while the directive stays accepted.

## The smoke run

The first live run was a smoke test of the harness, not a baseline. It ran software engineering on Sonnet: the canary and 2 tasks, once in each condition. The 6 runs cost 0.24 USD in total, about 0.04 USD each. The canary passed with the discipline and failed without it, so the conditions differ as they should. One run per task says nothing about the rules.

## Problem codes

| Code             | What it means                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------- |
| `eval-task`      | A task breaks the format, names a wrong target, or has a good output that fails or a bad one that passes |
| `eval-condition` | A throwaway copy can't be committed, or a status line can't be changed in it                             |
| `eval-canary`    | A condition holds the wrong rules in force, or the canary ended the wrong way                            |
| `eval-run`       | The options, the work folder, or the choice of tasks stop the eval                                       |
| `login`          | `claude auth status` failed with the run environment, so a run can't sign in                             |

The leak codes of the probe are in [Isolation](#isolation). A task file that isn't UTF-8 fails with `encoding`, a file that can't be read fails with `read`, and a symbolic link in a task fails with `symlink`.

## What it does not check yet

- Rules without a visible trace in a file. Tone, clarity, and judgment calls need a grader that can read, and the template ships none.
- Significance. The report gives counts, and you judge them.
- One rule at a time. A condition switches the whole discipline, so a rule that helps only with another rule in force looks the same as one that helps alone.
- Other agent tools. The harness runs Claude Code only.
- A change in `/context all`. The probe reads its text, so a new Claude Code version can break it. The probe then fails, and the run doesn't start.
- The name of the auto memory folder. The check derives it the way Claude Code does today.
