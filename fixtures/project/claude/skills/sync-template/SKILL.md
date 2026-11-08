---
name: sync-template
description: "Pull template changes into this project, or prepare a workspace rule for the template. Use when a person asks for a template pull or an upstream proposal."
disable-model-invocation: true
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Sync with the template

If compaction cuts this skill, ask the person to invoke the skill again.

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

From [Language rules](../../references/language-rules.md):

- Add each new opening verb to `knowledge/governance/language/vocabulary.yaml` or to the branch file of the node. ^add-the-verb
- Write each directive, trigger, and skill description in the grammar of `knowledge/governance/language/grammar.yaml`. ^follow-the-grammar

From [Lifecycle](../../references/lifecycle.md):

- Before you remove an `accepted` node or directive, set its `status` to `deprecated`. ^deprecate-before-removing
- Do not apply a `deprecated` node or directive to new work. ^deprecated-is-for-reference
- Keep the `id` of a node or a directive when you move its file. ^keep-the-id
- Do not change the `origin` of a node or a directive. ^keep-the-origin
- Before you deprecate a node, move the nodes under it. ^move-before-deprecating
- Follow a directive while its exception stays `proposed`. ^proposed-exception-stops-nothing
- Treat a `proposed` directive as a draft, not as a rule. ^proposed-is-a-draft
- Before you reject a node, leave no `proposed` or `accepted` directive or exception in it. ^reject-the-contents
- Do not apply a `rejected` node or directive to any work. ^rejected-applies-nowhere
- Before you reject an entity, remove each reference to it from the entities that are not `rejected`. ^remove-references-before-rejecting
- Set `status` to `proposed` on each new node, directive, and exception. ^start-as-proposed
- Set `rejection_reason` on each `rejected` node, directive, and exception. ^state-the-rejection-reason
- Set `origin` to `project` on each entity in workspace knowledge. ^workspace-is-project

From [Sync with the template](SKILL.md):

- Copy only an `accepted` workspace directive to the template clone. ^copy-accepted-rules-only
- Find each entity by its `id`, not by its path. ^find-entities-by-id
- Do not edit `knowledge/.densho/history.jsonl` in a project. ^keep-the-project-history
- Do not push a change to the template. ^no-push-to-the-template
- Do not open a pull request on the template. ^no-template-pull-request
- Do not pull a template change until a person asks for the pull. ^pull-on-request
- If a person does not answer a question, stop the job. ^stop-without-an-answer

## Inputs

- `.copier-answers.yml`, with `_src_path`, `_commit`, and `disciplines`
- `knowledge/.densho/history.jsonl` of the project, and the same file in a clone of the template
- The choice of the person: a pull, an upstream proposal, or both

This skill has two jobs: a pull and an upstream proposal. Do one job at a time. In the template repo, use `uv run densho` in place of `knowledge/.densho/densho`.

## Procedure

### Read what changed

1. If `git status --short` prints a line, ask the person to commit the work first.
2. If `.copier-answers.yml` does not exist, report that the project has no template record, and stop.
3. Run `git clone --quiet <_src_path> <clone>` with a new folder outside the project as `<clone>`.
4. Save the output of `knowledge/.densho/densho history --drift` to a file outside the project.
5. List each line of `<clone>/knowledge/.densho/history.jsonl` with a higher `change` than the last line of `knowledge/.densho/history.jsonl`.
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

1. Run `knowledge/.densho/densho adopt` after you resolve each entity.
2. Read each entity that the command sets to `proposed`. Tell the person that each one is out of force until a person accepts it.
3. For each new template directive that states the rule of a project directive, ask the person whether to deprecate the project directive.
4. Run `knowledge/.densho/densho history --drift` again.
5. Report each new drift line with the `action` `changed` or `removed`, outside the classes of the selection.
6. Remove `<clone>`.
7. Run `git add -A` for the pull, then commit it.

### Find rules for the template

1. Run `knowledge/.densho/densho build`. It writes `build/compiled/graph.json`, which holds only the directives in force.
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
4. If no node covers the subject, add one `densho:Concept` node under the practice area that covers it, with a pointer from that practice area.
5. If no practice area covers the subject, tell the person to add one with `author-domain`. Do not write the rule.
6. Run `uv run --directory <upstream> densho runtime`. Correct each problem from the first line down.
7. Run `git -C <upstream> status --short` and `git -C <upstream> diff`, and show the person the result.
8. Tell the person the path of `<upstream>`. The change waits there with no commit, for the person to commit and send.

## Output

A pull: one commit that passes the hook, with each conflict resolved by the person. An upstream proposal: a change in `<upstream>` that passes each check of the template, with no commit and no push.

## Validation

After a pull, `knowledge/.densho/densho runtime --verify` passes, and the report names each entity that left force. After an upstream proposal, `git -C <upstream> status --short` lists only the changed node files, the runtime files, and a vocabulary file if a verb was new.

## References

### Pull classes

Leave `status` out when you compare `fields`. A template `status` does not carry over, because `knowledge/.densho/densho adopt` sets it back.

The last line of `knowledge/.densho/densho history --drift` is a count. A line that starts with `note:` gives the count of entities in a discipline that `disciplines` leaves out. Each other line is a JSON object.

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
- `outside selection`: the template `path` sits under the folder of a `densho:Discipline` node that `disciplines` in `.copier-answers.yml` does not name. `knowledge/.densho/densho select` keeps that discipline out on each pull.
- The drift line and the template line each hold a digest for each field in `content`.
- A pointer conflict in front matter can split one pointer. Keep each pointer whole, with its `kind`, `target`, and `trigger`.
- The update can bring back the generated file of a removed node in `.claude/`. `knowledge/.densho/densho adopt` removes it.
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

- `--trust` lets the update run `knowledge/.densho/densho select`, so the choice of disciplines stays.
- `--data 'disciplines=[<id>, <id>]'` changes the choice of disciplines.

## References

- Read [Change rules](../../references/change-rules.md).
- Read [Language rules](../../references/language-rules.md).
- Read [Lifecycle](../../references/lifecycle.md).
