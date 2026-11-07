---
name: migrate-project
description: Convert the rules and the docs of an existing project into proposed workspace nodes. Use when a person asks for a knowledge migration.
---

# Migrate a project

This skill converts the knowledge of an existing project into proposed workspace nodes of the knowledge architecture. Later template pulls use the `sync-template` skill of the project. If compaction removes this skill, invoke it again.

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
04. If `knowledge/.ka/ka` does not exist, ask a person which disciplines the project takes.
05. Run the install command from `### Commands` with the disciplines of the answer.
06. If the project keeps its own `.pre-commit-config.yaml`, add the `4` local hooks from `### Commands`.
07. If you moved a hand-written `AGENTS.md`, ask a person whether the old root stays in force during the review.
08. Tell a person that you recommend that the old root stays.
09. If the old root stays, add the line `@knowledge-migration/source/root-agents.md` to `CLAUDE.md`.
10. Run `knowledge/.ka/ka adopt`.
11. If `pre-commit` does not exist, run `uv tool install pre-commit`.
12. Run `pre-commit install`.
13. Commit the install before you add a node.

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
12. Add the path and the line of the source of each directive to `## Signals` at the end of the body.
13. Set `basis: judgment` on each directive whose source cites no standard, no study, and no named method.
14. Set `basis` to `standard`, `research`, or `practitioner` on each other directive, from the kind of its cited source.
15. Set `sources` of each of these directives to the URL or the citation that its source names.
16. If a rule covers each task in the project, put it in `knowledge/node.md` with `scope: node`.
17. If a rule also covers the child documents of its document, set `scope: subtree`.
18. Set `scope: node` on each other rule.
19. In a rule, replace each path of a converted document with the node ID.
20. Add a pointer from the node of that rule to the named node.
21. Copy each procedure under `## Procedures` in the node body, in the order of its steps.
22. Copy each table, list, and example under `## References` in the node body.
23. Copy each rationale document under `## Rationale` in the body of its node.
24. List each heading of a rule group under `## Rule groups` in the node body, with the IDs of its rules.
25. If a skill in the source has its own trigger, add a `ka:Skill` node under `knowledge/skills/<id>/node.md`.
26. Set `invocation: person` on a skill whose source sets `disable-model-invocation: true`, and `invocation: agent` on each other skill.
27. Leave a copy of a skill for another agent tool at its path.
28. If an item stays out of the graph, add it to the `## Not converted` table of the ledger.

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
6. Tell a person to review the proposals with the `review-proposals` skill of the project.
7. Tell a person to remove the old text from `CLAUDE.md` after a person accepts its replacements.
8. Tell a person to keep only the `@AGENTS.md` import and personal items in `CLAUDE.md`.
9. Tell a person to remove `knowledge-migration/` and the converted source files after the review.

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
  - basis: judgment
  - status: proposed
  - origin: project

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

## Signals

- `use-whole-words`: 2026-11-06, migration. `rules/coding.md:14`.
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

Secret material also covers each credential, session header, one-time code, and personal identity list that the search does not match. The `knowledge-checks` hook searches only `knowledge/`, and it finds only the forms of the `secret` and `email` checks.

### Commands

```sh
uvx --python 3.14 copier copy --trust --defaults --vcs-ref=HEAD --data 'disciplines=[<id>, <id>]' https://github.com/jlm0/knowledge-architecture.git .
```

Replace each `<id>` with a discipline from the answer of the person. `copier.yml` of the template lists the choices under `disciplines`. Leave out `--data` to take each discipline.

The `4` local hooks are `conflict-markers`, `rejected-hunks`, `knowledge-checks`, and `eval-tasks`. Read them in `.pre-commit-config.yaml.jinja` in a clone of the template.
