---
name: migrate-and-reconcile-knowledge
description: Convert the knowledge of a project into governed nodes, or pull template changes into a project. Use when a person asks for a knowledge migration or a template pull.
---

# Migrate and reconcile knowledge

This skill has two jobs. Migration converts the knowledge of an existing project into nodes of the knowledge architecture. Reconciliation pulls template changes into a project. Do one job in each session. If compaction removes this skill, invoke it again.

A project owns its copy of the template, and the project decides what it takes. An agent proposes an entity, and a person accepts it.

## Directives

- Do not change a `status` to `accepted`.
- Set the `status` of each entity that you add to `proposed`.
- Do not copy secret material from a project into a node, the ledger, a command, or a reply.
- Do not write the name or the email of a person in a node.
- Do not add a rule that the source does not state.
- Do not change the meaning of a rule to pass a check.
- Do not convert a procedure or a reference into a directive.
- Keep each item that you do not convert in `knowledge-migration/ledger.md`.
- Do not remove a source file.
- Do not use `--no-verify`.
- Do not edit `knowledge/.ka/history.jsonl` in a project.
- Do not pull a template change until a person asks for the pull.
- Find each entity by its `id`, not by its path.
- If a person does not answer a question, stop the job.

## Migration

### Prepare the project

1. If `git status --short` prints a line, ask a person to commit the change.
2. Ask a person which files hold project knowledge.
3. Name each file that `### Where knowledge lives` lists.
4. Run the search from `### Secret search` on each source file.
5. For each hit with a value, add a `secret` row to the ledger with its path and line only.
6. If the ledger holds a `secret` row, tell a person to remove and replace the value.

### Install the template

01. Move a hand-written `AGENTS.md` to `knowledge-migration/source/root-agents.md`.
02. Move each `.claude/skills/<id>/SKILL.md` that you convert to `knowledge-migration/source/skills/<id>.md`.
03. Move a `knowledge/` or `.claude/references/` folder of the project to `knowledge-migration/source/`.
04. If `knowledge/.ka/ka` does not exist, run the install command from `### Commands`.
05. If the project keeps its own `.pre-commit-config.yaml`, add the `3` local hooks from `### Commands`.
06. Ask a person whether the old root stays in force during the review.
07. Tell a person that you recommend that the old root stays.
08. If the old root stays, add the line `@knowledge-migration/source/root-agents.md` to `CLAUDE.md`.
09. Run `knowledge/.ka/ka adopt`.
10. If `pre-commit` does not exist, run `uv tool install pre-commit`.
11. Run `pre-commit install`.
12. Commit the install before you add a node.

### Classify the source

1. Read each source file from start to end.
2. Put each item in one class from `### Classes`.
3. Add one ledger row for each item.
4. If the source holds more than `200` items, write a script outside the project for the mechanical rows.
5. Read each script row with the class `superseded` or `not-converted`.

### Write the nodes

01. Add one `ka:Domain` node for the project at `knowledge/nodes/<project-id>/node.md`, in the form of `### Node skeleton`.
02. Add a `ka:TextPointer` from `knowledge/node.md` to that domain.
03. Add one `ka:PracticeArea` node for each source document.
04. Set `broader` of each node to its parent.
05. Set `knowledge_type: workspace` and `origin: project` on each node that you add.
06. If a node gives project values for a template node, name the template node in `implements`.
07. Write the `## Definition` of each node in `1` or `2` sentences from the source.
08. Convert each row of a trigger table into one pointer on the parent node.
09. If a trigger names a code location, use a `ka:PathPointer` with `paths` in the form `src/**/*`.
10. If a trigger holds a second condition, split it into `2` pointers.
11. Put each rule in the `## Directives` section of the node for its source document.
12. Set `sources` of each directive to the path and the line of its source.
13. If a rule covers each task in the project, put it in `knowledge/node.md` with `scope: subtree`.
14. If a rule also covers the child documents of its document, set `scope: subtree`.
15. Set `scope: node` on each other rule.
16. In a rule, replace each path of a converted document with the node ID.
17. Add a pointer from the node of that rule to the named node.
18. Copy each procedure under `## Procedures` in the node body, in the order of its steps.
19. Copy each table, list, and example under `## References` in the node body.
20. Copy each rationale document under `## Rationale` in the body of its node.
21. List each heading of a rule group under `## Rule groups` in the node body, with the IDs of its rules.
22. If a skill in the source has its own trigger, add a `ka:Skill` node under `knowledge/skills/<id>/node.md`.
23. Leave a copy of a skill for another agent tool at its path.
24. If an item stays out of the graph, add it to the `## Not converted` table of the ledger.

### Check the result

01. Run `knowledge/.ka/ka runtime`.
02. Correct each problem from the first line down, with `### Problem codes`.
03. Do not remove a term from `prohibited` in a vocabulary file.
04. Add the source text and the new text of each edited rule to the `## Edited rules` table.
05. If `2` edits of a rule fail, copy the rule under `## Not converted` in the node body.
06. If an edit changes the meaning of a rule, copy the source rule under `## Not converted` in the node body.
07. Run `knowledge/.ka/ka runtime --proposals` to check the size of each file after acceptance.
08. Run the search from `### Secret search` on `knowledge/` and the ledger.
09. Check that each item of each source file has a row in the ledger.
10. Run `git add -A` for the result.
11. Run `pre-commit run --all-files`.
12. Commit the result.

### Report the migration

1. Report the count of each class in the ledger.
2. Report each item under `## Not converted`, and the reason for each one.
3. Report each change to `knowledge/governance/language/`, which no `status` covers.
4. Report each `secret` row, with its path and its line only.
5. Tell a person that no migrated directive applies until a person accepts it.
6. Give a person the command `knowledge/.ka/ka governance --pending` to read the list for review.
7. Tell a person to remove the old root line from `CLAUDE.md` after the review.
8. Tell a person to remove `knowledge-migration/` and the converted source files after the review.

## Reconciliation

### Read what changed

01. If `git status --short` prints a line, ask a person to commit the work first.
02. If `.copier-answers.yml` does not exist, report that the project has no template record.
03. Read `_src_path` and `_commit` from `.copier-answers.yml`.
04. Run `git clone --quiet <_src_path> <clone>` with a new folder outside the project as `<clone>`.
05. Run `git -C <clone> log --oneline <_commit>..HEAD` to list the template commits.
06. Save the output of `knowledge/.ka/ka history --drift` to a file outside the project.
07. List each line of `<clone>/knowledge/.ka/history.jsonl` with a higher `change` than the last line of `knowledge/.ka/history.jsonl`.
08. Match each listed line to a drift line by `kind` and `id`.
09. Put each listed line in one class from `### Pull classes`.
10. Mark each match with a drift `status` of `accepted`, which leaves force if a reviewed field changes.
11. Report the classes and the marks to a person.
12. Ask a person whether to pull.
13. If a person declines the pull, remove `<clone>`.
14. For each `collision`, ask a person for a new `id` of the project entity.
15. Commit each new `id` before you run the update.

### Pull the changes

1. Run the update command from `### Commands`.
2. Run `git grep -n -E '^(<{7} |>{7} )'` to list each conflict.
3. Run `git status --short` to list each `.rej` file.

### Resolve each entity

01. For each `same field` entity, read the base text with `git -C <clone> show <_commit>:<path>`.
02. Show a person the base text, the project text, and the template text, with your recommendation.
03. Write the text that a person chooses in place of the conflict markers.
04. For each `moved` entity, read the template change with `git -C <clone> diff <_commit> HEAD -- <path>`.
05. Ask a person whether to take the template change.
06. Edit the node at the `path` of its drift line.
07. For each `deleted` entity, keep it out of the project unless a person asks for it.
08. If a person declines a change to a file, run `git checkout HEAD -- <path>` on that file.
09. Compare `.pre-commit-config.yaml` with `<clone>/.pre-commit-config.yaml.jinja`.
10. Compare `.gitignore` with `<clone>/.gitignore.jinja`.
11. Report each line that the template file adds.

### Finish the pull

1. Run `knowledge/.ka/ka adopt` after you resolve each entity.
2. Read each entity that the command sets to `proposed`.
3. Tell a person that each entity that goes back to `proposed` leaves force until a person accepts it.
4. Run `knowledge/.ka/ka history --drift` again.
5. Report each new drift line with the `action` `changed` or `removed`.
6. Report the count of drift lines with the `action` `added`.
7. Remove `<clone>`.
8. Run `git add -A` for the pull.
9. Commit the pull.

## References

### Where knowledge lives

- `AGENTS.md`, `CLAUDE.md`, and `.claude/CLAUDE.md`
- `.claude/rules/` and `.cursor/rules/`
- `.claude/skills/` and `.agents/skills/`
- a folder of rule documents, such as `rules/` or `docs/agents/`
- a rationale document, a glossary, or a runbook that a rule names

The moved files take new names. The agent tool loads `AGENTS.md` and `.claude/skills/` from a subfolder, so the old names could load as rules.

### Classes

An item is a list item, a numbered step, a table row, a paragraph line, or a code block. A heading is not an item.

| Class           | What it is                                                                        | Where it goes                                         |
| --------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `directive`     | a sentence that states a constraint or a requirement                              | a directive                                           |
| `procedure`     | ordered steps                                                                     | `## Procedures` in the node body                      |
| `reference`     | a table, a word list, an example, or evidence                                     | `## References` in the node body                      |
| `rationale`     | a text that explains a rule                                                       | `## Rationale` in the node body                       |
| `definition`    | a text that says what a document covers                                           | `## Definition`                                       |
| `pointer`       | a row of a trigger table                                                          | a pointer on the parent node                          |
| `skill`         | a capability with its own trigger                                                 | a `ka:Skill` node                                     |
| `code`          | a script, a test, or a config file                                                | stays at its path                                     |
| `superseded`    | a rule or a document about the old rule system, such as its grammar or its linter | stays at its path, with the replacement in the ledger |
| `not-converted` | any other item                                                                    | stays at its path, with the reason in the ledger      |
| `secret`        | a value from `### Secret search`                                                  | stays at its path, with no text in the ledger         |
| `metadata`      | a front matter field of the source, such as `created`                             | stays at its path                                     |

A `status` in the source does not carry over. An `active` rule arrives as `proposed`.

### Ledger

Write `knowledge-migration/ledger.md` with these `4` sections. A person reads this file.

| Section            | Columns                                               |
| ------------------ | ----------------------------------------------------- |
| `## Summary`       | class, count                                          |
| `## Not converted` | source path and line, class, reason, text             |
| `## Edited rules`  | directive ID, source text, new text                   |
| `## Items`         | source path and line, class, target ID, edited or not |

Each Markdown file in `knowledge/` other than `node.md` fails `file-name`, so keep the ledger and the moved files in `knowledge-migration/`.

### Node skeleton

```markdown
---
id: coding
kind: ka:PracticeArea
title: Coding
status: proposed
origin: project
knowledge_type: workspace
broader:
  - my-project
pointers:
  - kind: ka:TextPointer
    target: testing
    trigger: You write a test.
---

## Definition

How this project writes and changes code.

## Directives

- Use whole words in each name. ^use-whole-words
  - scope: node
  - status: proposed
  - origin: project
  - sources: `rules/coding.md:14`

## Rule groups

### Naming

`use-whole-words`

## Procedures

### Name a function

1. Read the names in the file.

## References

### Naming examples

| Name | Instead of |
| --- | --- |
| `userAccount` | `usrAcct` |
```

- An `id` is a lowercase hyphenated slug. Each `id` is unique across nodes and directives.
- A trigger is one present-tense clause that starts with its subject, in `20` words or fewer.
- A directive is one sentence of `20` words or fewer. A code span counts as one word.
- A number, a path, and a command go in backticks.
- A `###` heading in `## Directives` fails `directive`.
- The docs of the template give each rule. Read `docs/node-format.md` and `docs/language-checks.md` in a clone of the template.

### Problem codes

| Code               | What you do                                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `opening`          | Add the verb to `knowledge/governance/language/branches/<domain-id>.yaml`. For a rule on the root, use `branches/root.yaml`. |
| `second-directive` | Split the rule. A comma list of nouns can read as a second action, so remove the commas or split the list.                   |
| `condition-count`  | Keep one condition. Write `Before you run X, do Y` with no other `if` or `when`.                                             |
| `prohibited`       | Remove the word. If the word sets the limit of the rule, keep the rule under `## Not converted`.                             |
| `literal`          | Put the value in backticks.                                                                                                  |
| `word-count`       | Cut a list, or split the rule.                                                                                               |
| `duplicate-rule`   | Keep one rule, and name the other node in `also_attached_to`.                                                                |
| `trigger-form`     | Start with the subject, such as `You`, then a verb in the present tense.                                                     |
| `not-generated`    | Move the hand-written file out of the generated path.                                                                        |
| `file-name`        | Move the Markdown file out of `knowledge/`.                                                                                  |
| `link`             | Write a path in a code span, or add a pointer. A link in a body must go to a generated file.                                 |
| `section`          | Rename a body heading with the name `Definition` or `Directives`. Write `Group: Definition`.                                 |
| `markdown`         | Remove the HTML block or the HTML comment. Rename a `## Directives` line in a code block.                                    |
| `unreachable`      | Add a pointer to the node.                                                                                                   |
| `origin-change`    | Commit the new `id` before the update.                                                                                       |
| `duplicate-id`     | Give the project entity a new `id`.                                                                                          |

### Secret search

This search prints the path and the line only. Read each hit, and do not repeat its value. Replace `<paths>` with the folders or the files to search.

```sh
git grep --untracked -n -I -i -E '(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|xox[abprs]-|BEGIN [A-Z ]*PRIVATE KEY|(password|passwd|secret|token|api[_-]?key).?[[:space:]]*[:=][[:space:]]*[^[:space:]]|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,})' -- <paths> | cut -d: -f1,2
```

Secret material also covers each credential, session header, one-time code, and personal identity list that the search does not match. No hook searches for secret material.

### Pull classes

Leave `status` out when you compare `fields`. A template `status` does not carry over, because `knowledge/.ka/ka adopt` sets it back.

The last line of `knowledge/.ka/ka history --drift` is a count. Each other line is a JSON object.

| Class              | Template line | Drift line                             | What the update does                           | What you do             |
| ------------------ | ------------- | -------------------------------------- | ---------------------------------------------- | ----------------------- |
| `clean`            | any           | none                                   | applies it                                     | read the result         |
| `moved`            | `changed`     | `fields` holds `path` or `holder`      | does not reach the new path, with no conflict  | take the change by hand |
| `deleted`          | `changed`     | `action` is `removed`                  | keeps it out                                   | report it               |
| `other field`      | `changed`     | no shared field                        | merges it when the lines differ                | read the result         |
| `same field`       | `changed`     | a shared field with a different digest | writes conflict markers when the lines overlap | ask a person            |
| `same result`      | `changed`     | a shared field with the same digest    | keeps one text                                 | read the result         |
| `collision`        | `added`       | `added` with the same `id`             | ends with `duplicate-id`                       | commit a new `id` first |
| `template removal` | `removed`     | any                                    | removes the file, or writes conflict markers   | ask a person            |
| `vocabulary`       | `file`        | any                                    | merges the file                                | read the words          |

- The drift line and the template line each hold a digest for each field in `content`.
- A pointer conflict in front matter can split one pointer. Keep each pointer whole, with its `kind`, `target`, and `trigger`.
- The update can bring back the generated file of a removed node in `.claude/`. `knowledge/.ka/ka adopt` removes it.
- A rename fails `removed-accepted` when the entity is `accepted`. Set it to `deprecated` in one commit, and remove it in a later commit.

### Commands

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD https://github.com/jlm0/knowledge-architecture.git .
uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD
```

The `3` local hooks are `conflict-markers`, `rejected-hunks`, and `knowledge-checks`. Read them in `.pre-commit-config.yaml.jinja` in a clone of the template.
