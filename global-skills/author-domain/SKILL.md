---
name: author-domain
description: Add a discipline or a practice area to the template from established frameworks, and cite only sources that you opened. Use when a person asks for new domain knowledge in the template.
---

# Author a domain

This skill adds domain knowledge to a clone of the template: a discipline, or a practice area of a discipline. Each rule comes from a framework that a published source states, and you open each source before you cite it. If compaction removes this skill, invoke it again.

An agent proposes each entity, and a person accepts it. Run the steps in the template repo, where the engine runs as `uv run densho`.

## Directives

- Do not change a `status` to `accepted`.
- Set the `status` of each entity that you add to `proposed`.
- Open each source before you cite it.
- Do not add a directive that no opened source states.
- Write each directive in your own words.
- Do not copy more than one sentence of a source into a node.
- Set `origin: template` on each entity that you add.
- Set `basis` on each directive from the kind of its source, as `### Basis` states.
- Name the public URL of the template repo in the `User-Agent` of each request to a site.
- Do not send a name or an email to a site.
- Do not write the name or the email of a person in a node.
- Keep each downloaded page in a source folder outside `knowledge/`.
- Report each framework that you add to the outline, and each framework that you leave out.
- Do not use `--no-verify`.

## Procedure

### Plan the work

1. Ask a person for the outline: the discipline, its practice areas, its frameworks, and its candidate skills.
2. Record the commit, the count of nodes and directives, and the count from `uv run densho governance --pending`.
3. Read the reference page of each node that a new node links.
4. Do not repeat a rule of a linked node.
5. Make a new source folder and a source log file outside `knowledge/`.

### Open the sources

1. For each framework, find a primary page: the standard, the paper, or a page of the author.
2. Download each page into the source folder with the command from `### Commands`.
3. Read each page.
4. Add one row for each page to the source log, in the form of `### Source log`.
5. If a page does not load, open a snapshot of the page in the Wayback Machine.
6. Log each page that does not load.
7. If a framework comes from a book, cite an article of the author or another page that you opened.
8. Name the book of each such page in the source log.
9. If no opened page supports a framework, leave the framework out.

### Write the nodes

01. Put each finding in one form from `### Outputs`.
02. Add each `densho:PracticeArea` node under its discipline, and each `densho:Concept` node under its practice area.
03. Add a `densho:TextPointer` from the parent to each new node, with a trigger in the present tense.
04. Write each directive in the form of `### Node skeleton`.
05. Set `sources` of each directive to the URL of each opened page that states it.
06. Use `informs` when the output of a node is an input of another node.
07. Use `depends_on` only when a node has no meaning without another node.
08. Use `related` when two nodes coexist and no flow joins them.
09. Before you add a directive to a node that a skill uses, run `uv run densho directives --at <skill-id>`.
10. Add a skill only for an ordered procedure that no skill holds.
11. Keep each procedure of a skill to `9` steps.
12. If you add a `densho:Discipline` node, add its ID to `choices` and `default` of `disciplines` in `copier.yml`.
13. Add each new opening verb to `knowledge/governance/language/branches/<discipline-id>.yaml`.

### Check the work

01. Run `uv run densho language`.
02. Correct each problem from the first line down.
03. Run `uv run densho runtime`.
04. Run `uv run densho runtime --proposals` to read the size of each changed skill.
05. Run the URL search from `### Commands`.
06. Find each URL of the search in the source log.
07. Run `git add -A` for the result.
08. Run `uv run pre-commit run --all-files`.
09. If the first run changes a node file, follow the steps in `### Formatter changes`.
10. Read the diff as a reviewer, with the list in `### Review points`.

### Report the work

1. Report the count of new nodes, and the count of new directives for each `basis`.
2. Report each directive that you changed, with its old text and its new text.
3. Report each framework that you added to the outline, and each framework that you left out.
4. Report each skill that you merged into another skill.
5. Report each verb that you added to a vocabulary file.
6. Give a person the source log and the table from `### Entity table`.
7. Tell a person that no new entity is in force until a person accepts it.

## References

### Outputs

| Finding                        | Output                                    |
| ------------------------------ | ----------------------------------------- |
| A rule that an agent can check | A directive                               |
| A meaning                      | A `densho:Concept` node with a definition |
| An ordered procedure           | A `densho:Skill` node                     |

- Security, testing, and accessibility give mostly directives. Strategy and brand give mostly concepts and skills.
- A domain skill gets `invocation: agent`, unless its job changes something outside the repo.
- Each skill uses a part of the listing budget. Keep the count of new skills low, and merge a skill into another one when the two overlap.

### Basis

| Value          | Source                                            |
| -------------- | ------------------------------------------------- |
| `standard`     | a published standard or a versioned specification |
| `research`     | an empirical study or a model from research       |
| `practitioner` | a method of a named author or company             |
| `judgment`     | no source                                         |

- A directive from this skill always has a source, so it does not get `judgment`.
- The kind of the source sets the `basis`. A guidance article with no study is `practitioner`.

### Source log

| URL                         | Version                              | Book behind it      | Facts that the page supports     |
| --------------------------- | ------------------------------------ | ------------------- | -------------------------------- |
| `https://example.com/guide` | the edition, or the date on the page | the book, or `none` | each fact that a directive cites |

- Log each page that you opened, also a page that you do not cite. Say why you do not cite it.
- Log each page that did not load, with the HTTP status or the error.

### Entity table

| Entity                      | Kind             | Node             | `basis`        | Change |
| --------------------------- | ---------------- | ---------------- | -------------- | ------ |
| `error-messages`            | `densho:Concept` | `error-messages` | -              | new    |
| `error-cause-and-next-step` | directive        | `error-messages` | `practitioner` | new    |

### Review points

- A rule that is stricter than its source
- A fact that no opened source states
- A directive that states only a fact, and no instruction that an agent can check
- A broken or garbled sentence
- A skill that grows past its size, because a node in its `uses` received directives

### Node skeleton

```markdown
---
id: error-messages
kind: densho:Concept
title: Error messages
status: proposed
origin: template
knowledge_type: domain
broader:
  - interface-writing
---

## Definition

The text that tells a user what went wrong and how to continue.

## Directives

- State the cause and the next step in each error message. ^error-cause-and-next-step
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://example.com/error-messages
```

- An `id` is a lowercase slug with hyphens. Each `id` is unique across nodes and directives.
- Add the prefix of the discipline to a short `id` that can collide with an `id` of another discipline.
- A directive is one sentence of `20` words or fewer. A number, a path, and a command go in backticks.
- The language checks read `Must`, `Should`, `Could`, and `need to` as modals. Put a quoted word in backticks.

### Commands

```sh
curl -sS -L -A 'densho (+https://github.com/jlm0/densho)' -o <folder>/<name>.html <url>
git grep -h -o -E 'https?://[^ )>`]+' -- knowledge/nodes/ knowledge/skills/ | sort -u
```

- Replace the URL in the `User-Agent` with the public URL of your copy of the template.
- The `git grep` search prints each URL that a node cites, one time each.

### Formatter changes

`mdformat` can change a table or a numbered list in a node file during the first run of the hooks. The runtime files and the change history then differ from the node. Do these steps:

1. Run `uv run densho runtime`.
2. Run `git checkout HEAD -- knowledge/.densho/history.jsonl`.
3. Run `uv run densho history`.
4. Run `git add -A`.
