# Migration and reconciliation

> **In the library:** the moving crew. It catalogs a collection that already exists into the system, and it later brings new arrivals from the original library to a branch that has gone its own way.

**Status:** Built.

This layer is one global skill with two jobs. Migration converts the knowledge of an existing project into nodes that pass the checks. Reconciliation pulls template changes into a project that has drifted. An agent does the work and proposes the result, and you decide what stands.

The source is `global-skills/migrate-and-reconcile-knowledge/SKILL.md`. It adds no check and no command. It uses the ones a project already has: the [hooks](template-packaging.md), `knowledge/.ka/ka adopt`, `knowledge/.ka/ka history --drift`, and the change history in `knowledge/.ka/history.jsonl`.

## Install the skill

The skill lives outside each project, so it works before a project has the template, and one copy serves every project. An install of the template doesn't carry it. `copier.yml` copies only the paths it names, and a test checks that `global-skills/` stays out.

Installing it is your choice. From a clone of this repo:

```sh
cp -R global-skills/migrate-and-reconcile-knowledge ~/.claude/skills/
```

Run the same command to take a newer copy. Then ask an agent to migrate the knowledge of a project, or to pull template changes.

## Migrate a project

Commit your work first, because the agent asks for a clean tree before it starts. It then takes these steps:

1. It asks which files hold project knowledge, and it searches them for secret material.
2. It moves the files that the install would collide with, then installs the template and commits.
3. It puts each item of each source file in one class, and it writes one row for the item in a ledger.
4. It writes the nodes, then runs the checks and corrects what they report.
5. It commits through the project hooks and reports what it did.

### Where each item goes

Not everything is a rule, and the skill doesn't force prose into one.

| Item                                                           | Where it goes                                      |
| -------------------------------------------------------------- | -------------------------------------------------- |
| A sentence that states a constraint or a requirement           | A directive                                        |
| Ordered steps                                                  | `## Procedures` in the node body                   |
| A table, a word list, an example, or evidence                  | `## References` in the node body                   |
| A text that explains a rule                                    | `## Rationale` in the node body                    |
| A row of a trigger table                                       | A pointer. A code location makes it a path pointer |
| A capability with its own trigger                              | A skill                                            |
| A script, a test, or a config file                             | Stays at its path                                  |
| A rule about the old rule system, such as its grammar          | Stays at its path, with the replacement noted      |
| A rule that fails the checks after two edits, or anything else | Stays at its path, and `## Not converted` shows it |

Project knowledge becomes workspace knowledge, with `knowledge_type: workspace` and `origin: project`. Each directive names its source file and line in `sources`, and `## Rule groups` in the body keeps the headings the rules sat under. Its `basis` is `judgment` unless the old rule cites a standard, a study, or a named method, because a project file is a record of a decision and not evidence for it. A skill whose source sets `disable-model-invocation: true` gets `invocation: person`, and every other skill gets `invocation: agent`.

### What you get

Everything arrives as `proposed`, so no migrated rule binds an agent until you accept it. The skill never changes a `status` to `accepted`. To read what waits, run `knowledge/.ka/ka view`, or `knowledge/.ka/ka governance --pending` in a terminal. The [human interface](human-interface.md#in-a-project) has the steps from there.

Your old rules can stay in force in the meantime. A hand-written root `AGENTS.md` has to leave its path, because the generator owns it, so the agent moves it to `knowledge-migration/source/root-agents.md` and asks whether to keep it loading with this line in `CLAUDE.md`:

```text
@knowledge-migration/source/root-agents.md
```

The skill recommends keeping it. The agent removes no source file, and other source files stay at their paths. A moved file takes a new name, because a tool loads `AGENTS.md` and `.claude/skills/` from a subfolder too.

`knowledge-migration/ledger.md` is yours to read, and it has four sections:

| Section            | What it holds                                                   |
| ------------------ | --------------------------------------------------------------- |
| `## Summary`       | The count of each class                                         |
| `## Not converted` | Each item that stayed out of the graph, with the reason         |
| `## Edited rules`  | The source text and the new text of each rule the agent changed |
| `## Items`         | One row for each source item, with its class and its target     |

After your review, remove the line from `CLAUDE.md`, the `knowledge-migration/` folder, and the converted source files.

### Words the vocabulary lacks

A real rule set opens with verbs the vocabulary doesn't approve. The agent adds them to `knowledge/governance/language/branches/<node-id>.yaml`. It doesn't remove a term from `prohibited`. No `status` covers a vocabulary file, so the agent reports each change for you to read.

## Pull template changes

Nothing forces a pull. A project can stay where it is, and the agent pulls only when you ask. Commit your work first, then ask. The agent:

1. Clones the template into a folder outside the project, from `_src_path` in `.copier-answers.yml`.
2. Reads each new line of the template's `knowledge/.ka/history.jsonl`, and matches it by `kind` and `id` to the output of `knowledge/.ka/ka history --drift`.
3. Reports what each change will do, and asks whether to pull.
4. Runs `copier update`, resolves each entity with you, and runs `knowledge/.ka/ka adopt`.
5. Reports what left force and what still differs, then commits through the hooks.

A pull doesn't promote anything. `knowledge/.ka/ka adopt` sets a changed entity to `proposed`, even if the template accepted it. If you accepted an entity and the pull changes a reviewed field, it leaves force until you accept it again, and the agent tells you so before it pulls.

### How each change sorts

| Class              | What it means                                    | What happens                                                               |
| ------------------ | ------------------------------------------------ | -------------------------------------------------------------------------- |
| `clean`            | You didn't change it                             | The update applies it                                                      |
| `moved`            | You moved the node                               | The update can't reach it, so the agent shows the change and edits by hand |
| `deleted`          | You removed the node                             | It stays removed, and the agent reports it                                 |
| `other field`      | You each changed a different field               | The update merges it, and the agent reads the result                       |
| `same field`       | You each changed one field to a different result | You choose                                                                 |
| `same result`      | You each made the same change                    | One text stays                                                             |
| `collision`        | You each added the same `id`                     | The agent asks for a new `id` and commits it before the update             |
| `template removal` | The template removed something you hold          | You choose                                                                 |
| `vocabulary`       | A vocabulary file changed                        | The update merges it, and the agent reads the words                        |

### A node that both sides changed

The history holds a digest for each field, and so does the drift report, so the agent can tell a real conflict from two changes to different fields before it touches a file.

For a `same field` entity, the agent shows you the base text, your text, and the template's text, with its recommendation. You choose, and the agent writes your choice in place of the [conflict markers](template-packaging.md#a-node-that-both-sides-changed). If you don't answer, the job stops. The markers stay, and the `conflict-markers` hook blocks the commit.

For a change you decline, the agent restores your file with `git checkout HEAD -- <path>`. The difference stays in the next drift report, so it doesn't get lost. For a `moved` node, the agent reads the template change with `git diff` in the clone and edits your node at the path in the drift report.

The agent renames a colliding entity in its own commit, before the update. A rename in the pull commit looks like a template entity changing its origin, and it fails with `origin-change`.

## Secret material

The skill tells the agent not to copy secret material from a project into a node, the ledger, a command, or a reply. It gives the agent one search, to run on the sources before it starts and on the result before it commits. The search prints only a path and a line, so the value doesn't enter the session:

```sh
git grep --untracked -n -I -i -E '<pattern>' -- <paths> | cut -d: -f1,2
```

The pattern covers common key forms, a private key header, a `password` or `token` assignment, and an email address. Each hit becomes a `secret` row in the ledger, with its path and line only, and the agent asks you to remove and replace the value.

## What stops a bad result

The project hooks read the result on each commit. These broken outputs each fail through a real `git commit`:

| What went wrong                             | What reports it             |
| ------------------------------------------- | --------------------------- |
| A new entity arrives as `accepted`          | `new-status`                |
| A rule holds a word such as `should`        | `prohibited`                |
| Prose becomes a rule                        | `sentence`                  |
| A procedure becomes one rule                | `second-directive`          |
| A value in a rule has no backticks          | `literal`                   |
| A rule repeats another rule                 | `duplicate-rule`            |
| A node has no route to it                   | `unreachable`               |
| A pointer names no node                     | `reference`                 |
| A workspace node claims the template origin | `template-workspace`        |
| The ledger sits in `knowledge/`             | `file-name`                 |
| A body hides text in an HTML block          | `markdown`                  |
| A hand-written root stays at `AGENTS.md`    | `not-generated`             |
| A conflict marker stays                     | the `conflict-markers` hook |
| A rejected hunk stays                       | the `rejected-hunks` hook   |

A test holds the skill to the [language checks](language-checks.md): the description and each rule and step pass the same rules as a skill in the graph. The same test checks that each command, problem code, and named section in the text exists, that the node example in the text parses, and that the steps fit in what compaction keeps.

## What it has run against

The skill text has been followed step by step in temporary projects, against the agent rules of an earlier project: 74 Markdown files, a skill, and the scripts beside them, which came to 4,050 items. A script wrote the mechanical rows, as the skill allows for a large source, and the `secret` rows are values planted for the test.

| Class           | Items |
| --------------- | ----- |
| `directive`     | 1,250 |
| `reference`     | 1,099 |
| `superseded`    | 673   |
| `rationale`     | 383   |
| `metadata`      | 347   |
| `procedure`     | 188   |
| `pointer`       | 48    |
| `not-converted` | 40    |
| `code`          | 11    |
| `skill`         | 8     |
| `secret`        | 3     |

That made 32 nodes under the root, and each hook passed. With the seed, 1,390 entities wait for review. It ran in both orders: into a project with the template already installed, and into a repo with history where the rules came first. A pull ran on the result, with a moved node, a deleted node, both sides changing one field, a colliding `id`, and a declined change.

## What it does not check yet

- Secret material, in a hook. A key in a rule or a body passes every hook, so the search in the skill is the only check, and it finds only the forms it names.
- The ledger. No hook confirms that each source item has a row, and the file is ordinary Markdown.
- Whether a rule kept its meaning, or whether a class is right. The ledger shows each edit and each item left out, for a person to read.
- A verb added to a vocabulary file. No `status` covers it, so only the report names it.
- A copy of a skill for another tool, such as `.agents/skills/`. It stays at its path, and its text can name an old path.
- `.pre-commit-config.yaml` and `.gitignore`. The agent compares them with the template by hand and reports each new line.
- The job itself. The test reads the skill text and doesn't run a model.

## What only a real session can show

The agent that followed the text in those runs also wrote it, and it had a conversion script. Only a real session with the installed skill can confirm these points:

- That the tool lists the skill and picks it from its description.
- That an agent with only the skill, and no knowledge of how it was written, reaches the same result.
- That the `CLAUDE.md` line loads the moved root. This rests on the Claude Code docs.
- How well the questions work with a person who answers them live.
- What compaction keeps of a long job. The steps come before the references, and the skill says to invoke it again if it goes, but only a real session shows when that happens.
