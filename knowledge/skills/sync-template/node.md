---
id: sync-template
kind: ka:Skill
title: Sync with the template
status: proposed
origin: template
knowledge_type: domain
description: Pull template changes into this project, or prepare a workspace rule for the template. Use when a person asks for a template pull or an upstream proposal.
invocation: person
uses:
  - change-rules
  - lifecycle
  - language-rules
---

## Directives

- Do not pull a template change until a person asks for the pull. ^pull-on-request
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not edit `knowledge/.ka/history.jsonl` in a project. ^keep-the-project-history
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Find each entity by its `id`, not by its path. ^find-entities-by-id
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Copy only an `accepted` workspace directive to the template clone. ^copy-accepted-rules-only
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not push a change to the template. ^no-push-to-the-template
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Do not open a pull request on the template. ^no-template-pull-request
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If a person does not answer a question, stop the job. ^stop-without-an-answer
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template

## Inputs

- `.copier-answers.yml`, with `_src_path`, `_commit`, and `disciplines`
- `knowledge/.ka/history.jsonl` of the project, and the same file in a clone of the template
- The choice of the person: a pull, an upstream proposal, or both

This skill has two jobs: a pull and an upstream proposal. Do one job at a time. In the template repo, use `uv run ka` in place of `knowledge/.ka/ka`.

## Procedure

### Read what changed

1. If `git status --short` prints a line, ask the person to commit the work first.
2. If `.copier-answers.yml` does not exist, report that the project has no template record, and stop.
3. Run `git clone --quiet <_src_path> <clone>` with a new folder outside the project as `<clone>`.
4. Save the output of `knowledge/.ka/ka history --drift` to a file outside the project.
5. List each line of `<clone>/knowledge/.ka/history.jsonl` with a higher `change` than the last line of `knowledge/.ka/history.jsonl`.
6. Match each listed line to a drift line by `kind` and `id`, and put it in one class from `### Pull classes`.
7. Mark each match with a drift `status` of `accepted`. It leaves force if a reviewed field changes.
8. Report the template commits from `git -C <clone> log --oneline <_commit>..HEAD`, the classes, and the marks.
9. Ask the person whether to pull. If the person declines, remove `<clone>`, and stop.

### Prepare the pull

1. For each `collision`, ask the person for a new `id` of the project entity.
2. Commit each new `id` before you run the update.
3. Run the update command from `### Commands`.
4. Run `git grep -n -E '^(<{7} |>{7} )'` to list each conflict.
5. Run `git status --short` to list each `.rej` file.

### Resolve each entity

1. For each `same field` entity, read the base text with `git -C <clone> show <_commit>:<path>`.
2. Show the person the base text, the project text, and the template text, with your recommendation.
3. Write the text that the person chooses in place of the conflict markers.
4. For each `moved` entity, read the change with `git -C <clone> diff <_commit> HEAD -- <path>`, and ask the person whether to take it.
5. Edit the node at the `path` of its drift line.
6. Keep each `deleted` entity out of the project, unless the person asks for it.
7. If the person declines a change to a file, run `git checkout HEAD -- <path>` on that file.
8. Compare `.gitignore` with `<clone>/.gitignore.jinja`. The update merges `.pre-commit-config.yaml`, so step 5 lists a hunk that it cannot apply.
9. Report each line that the template file adds.

### Finish the pull

1. Run `knowledge/.ka/ka adopt` after you resolve each entity.
2. Read each entity that the command sets to `proposed`. Tell the person that each one is out of force until a person accepts it.
3. For each new template directive that states the rule of a project directive, ask the person whether to deprecate the project directive.
4. Run `knowledge/.ka/ka history --drift` again.
5. Report each new drift line with the `action` `changed` or `removed`, outside the classes of the selection.
6. Remove `<clone>`.
7. Run `git add -A` for the pull, then commit it.

### Find rules for the template

1. Run `knowledge/.ka/ka build`. It writes `build/compiled/graph.json`, which holds only the directives in force.
2. List each directive in that file with `"origin": "project"`.
3. Keep each directive that passes each test of `### Rules for each project`.
4. Show the person the list, with a reason for each directive. Ask which directives to copy to the template.
5. Run `git clone --quiet <_src_path> <upstream>` with a new folder outside the project as `<upstream>`. Keep this folder.
6. Run `git -C <upstream> grep -n 'status: rejected' -- knowledge/`. Skip a hit inside a code block of a skill.
7. Drop each rule that a `rejected` entity states, and tell the person its `rejection_reason`.
8. Drop each rule that a template directive already states, and tell the person its ID.

### Write the upstream proposal

1. Find the template node whose definition covers the subject of the rule.
2. Write the rule in general words, with no path, command, name, or value of the project.
3. Add the rule to that node as a directive, in the form of `### Upstream directive`.
4. If no node covers the subject, add one `ka:Concept` node under the practice area that covers it, with a pointer from that practice area.
5. If no practice area covers the subject, tell the person to add one with `author-domain`. Do not write the rule.
6. Run `uv run --directory <upstream> ka runtime`. Correct each problem from the first line down.
7. Run `git -C <upstream> status --short` and `git -C <upstream> diff`, and show the person the result.
8. Tell the person the path of `<upstream>`. The change waits there with no commit, for the person to commit and send.

## Output

A pull: one commit that passes the hook, with each conflict resolved by the person. An upstream proposal: a change in `<upstream>` that passes each check of the template, with no commit and no push.

## Validation

After a pull, `knowledge/.ka/ka runtime --verify` passes, and the report names each entity that left force. After an upstream proposal, `git -C <upstream> status --short` lists only the changed node files, the runtime files, and a vocabulary file if a verb was new.

## References

### Pull classes

Leave `status` out when you compare `fields`. A template `status` does not carry over, because `knowledge/.ka/ka adopt` sets it back.

The last line of `knowledge/.ka/ka history --drift` is a count. A line that starts with `note:` gives the count of entities in a discipline that `disciplines` leaves out. Each other line is a JSON object.

| Class               | Template line | Drift line                             | What the update does                           | What you do             |
| ------------------- | ------------- | -------------------------------------- | ---------------------------------------------- | ----------------------- |
| `outside selection` | any           | any                                    | keeps it out                                   | skip it                 |
| `clean`             | any           | none                                   | applies it                                     | read the result         |
| `moved`             | `changed`     | `fields` holds `path` or `holder`      | does not reach the new path, with no conflict  | take the change by hand |
| `deleted`           | `changed`     | `action` is `removed`                  | keeps it out                                   | report it               |
| `other field`       | `changed`     | no shared field                        | merges it when the lines differ                | read the result         |
| `same field`        | `changed`     | a shared field with a different digest | writes conflict markers when the lines overlap | ask the person          |
| `same result`       | `changed`     | a shared field with the same digest    | keeps one text                                 | read the result         |
| `collision`         | `added`       | `added` with the same `id`             | ends with `duplicate-id`                       | commit a new `id` first |
| `template removal`  | `removed`     | any                                    | removes the file, or writes conflict markers   | ask the person          |
| `vocabulary`        | `file`        | any                                    | merges the file                                | read the words          |

- Sort each line into the first class that fits, from the top of the table.
- `outside selection`: the template `path` sits under the folder of a `ka:Discipline` node that `disciplines` in `.copier-answers.yml` does not name. `knowledge/.ka/ka select` keeps that discipline out on each pull.
- The drift line and the template line each hold a digest for each field in `content`.
- A pointer conflict in front matter can split one pointer. Keep each pointer whole, with its `kind`, `target`, and `trigger`.
- The update can bring back the generated file of a removed node in `.claude/`. `knowledge/.ka/ka adopt` removes it.
- A rename fails `removed-accepted` when the entity is `accepted`. Set it to `deprecated` in one commit, and remove it in a later commit.

### Rules for each project

A directive goes to the template only when each of these holds:

- A person accepted it in this project.
- It names no path, file, command, service, product, person, or value that only this project has.
- It covers the work of a discipline that the template holds.
- No template directive states it, and no `rejected` template entity states it.

### Upstream directive

```markdown
- Show the cause and the fix in each error message. ^error-states-cause-and-fix
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
```

- Set `origin: template`, because the template holds the rule as domain knowledge.
- Keep `basis: judgment` and leave out `sources`, unless you open a source that states the rule.
- If the text of the project directive differs, keep the new text. Tell the person both texts.

### Commands

```sh
uvx --python 3.14 copier update --trust --defaults --vcs-ref=HEAD
```

- `--trust` lets the update run `knowledge/.ka/ka select`, so the choice of disciplines stays.
- `--data 'disciplines=[<id>, <id>]'` changes the choice of disciplines.
