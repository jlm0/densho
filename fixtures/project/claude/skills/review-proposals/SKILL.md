---
name: review-proposals
description: "Show the knowledge proposals branch by branch, with the effect and the conflicts of each one. Use when a person reviews the proposals."
disable-model-invocation: true
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Review proposals

If compaction cuts this skill, ask the person to invoke the skill again.

## Directives

From [Governance](../../rules/knowledge/governance.md):

- Set `basis` to `judgment` on each directive that names no source. ^judgment-without-a-source
- Do not use `--no-verify` on a commit. ^keep-the-hook
- Do not write the name or the email of a person in a node or a test. ^no-personal-data
- Apply one workflow to domain knowledge and to workspace knowledge. ^one-workflow
- Run each hook in `.pre-commit-config.yaml` on each file before each commit. ^run-checks-before-commit

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

From [Approval](../../references/approval.md):

- Run the engine with `governance --pending` to list each proposal. ^list-the-proposals
- Do not set `status` to `accepted` unless a person approves the change. ^person-accepts
- Do not set `status` to `deprecated` unless a person approves the change. ^person-deprecates
- Do not set `status` to `rejected` unless a person rejects the proposal. ^person-rejects
- Read the reason of each exception before you accept it. ^read-the-reason
- Run the engine with `directives --at` on the node before you accept a directive. ^read-what-applies

From [Review proposals](SKILL.md):

- Name each conflict before the person decides. ^name-conflicts-first
- Show the proposals of one branch at a time. ^one-branch-at-a-time
- Do not run the `densho accept` command. ^person-runs-accept
- Write the reason of the person in `rejection_reason`. ^use-the-reason-of-the-person

## Inputs

- The queue: each `proposed` entity that `knowledge/.densho/densho governance --pending` lists
- The citation of each proposal in `## Signals` of its node
- Each `accepted` directive with a line of the class `eval` in `## Signals`: a proposal to deprecate it
- A person who decides on each proposal

In a project, run the engine as `knowledge/.densho/densho`. In the template repo, use `uv run densho` in its place.

## Procedure

### Prepare the queue

1. If `git status --short` lists a file under `knowledge/`, ask the person to commit it first. `densho accept` reads the last commit.
2. Run `knowledge/.densho/densho governance --pending`. Save the output to a file outside the repo.
3. Run `knowledge/.densho/densho runtime --proposals`. It writes the review copy to `build/runtime-proposals/`.
4. Run the search from `### Eval signals`. Add each `accepted` directive that it lists to the queue as a deprecation.
5. Find the branch of each entity, as `### Branches` states.
6. Show the person one line for each branch, with its count of nodes, directives, and exceptions.
7. Ask the person which branch to review first.

### Explain each proposal

Do these steps for each proposal of one branch. Then go to the next branch.

1. Read the entity in its node file.
2. State in one sentence what the entity tells an agent, or what it changes in the tree.
3. State its effect, as `### Effect` states.
4. State its signal from `## Signals` of its node. For template knowledge, state its `basis` and its `sources`.
5. Name each conflict that `### Conflicts` lists, with the IDs on both sides.
6. Give your recommendation: accept, reject with a reason, or keep for later.
7. If a branch holds more than `20` proposals, explain its nodes first. Ask the person whether to go through each directive.

### Record the decision

01. Ask the person to decide on each proposal of the branch: accept, reject, or keep for later.
02. For the proposals that the person accepts, write one `knowledge/.densho/densho accept` command with their names. The person runs it.
03. For each proposal that the person rejects, ask the person for the reason.
04. Set its `status` to `rejected`, and add the reason in the form of `### Rejection`.
05. Do not change a proposal that the person keeps for later.
06. For each deprecation that the person approves, set the `status` of the directive to `deprecated`. Remove each eval target that names it, and each eval task with no target left.
07. For each deprecation that the person declines, remove its `eval` line.
08. Run `knowledge/.densho/densho runtime`. Correct each problem from the first line down.
09. Show the person `git diff`, and ask whether to commit the decisions now.
10. After the commit, invoke the `propose-knowledge` skill. Its first steps remove the notes and the citations of the decided proposals.

### Report the review

1. Report the count of accepted, rejected, and kept proposals for each branch.
2. Report each conflict that stays open.
3. Tell the person which branches still wait for review.

## Output

The decision of the person on each proposal of the reviewed branches. An accepted proposal has the status that the `densho accept` run of the person wrote. A rejected proposal has the reason of the person.

## Validation

Each change to `accepted` comes from a `densho accept` run of the person. Each `rejected` entity holds the reason of the person, with no name and no email. The diff holds no other change to a field that needs review.

## References

### Branches

- The branch of a node is the discipline that its `broader` chain reaches.
- A workspace node with no discipline above it has the branch of its domain.
- The governance nodes form the branch `governance`. The skills form the branch `skills`. The root forms the branch `root`.
- A directive and an exception have the branch of the node that holds them.
- Follow `broader`, not the folder path. A path only helps a person to find a file.

### Effect

| Entity                          | Effect, and how you find it                                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| a directive                     | It applies at its node, and with `scope: subtree` at each node under it. The search in `### Commands` lists its files. |
| an exception                    | It stops a directive at its node. `knowledge/.densho/densho directives --at <node-id>` names the directive.            |
| a node                          | Its definition and its place in the tree. The status of a node does not change which directives apply.                 |
| a skill                         | Its description goes in the skill listing. With `invocation: person`, only a person starts it.                         |
| an edit of an `accepted` entity | The entity stays out of force until a person accepts it again. Compare its text with `git show HEAD:<path>`.           |

### Conflicts

Name a conflict in each of these cases:

- Two proposals ask for opposite actions on the same object.
- A proposal contradicts a directive that applies at the same node. `knowledge/.densho/densho directives --at <node-id>` lists them.
- A proposal states the same change as a `rejected` entity.
- An exception stops a directive that the person accepts in this review.
- A proposal names another proposal in `broader`, `uses`, `applies`, or an exception. The second proposal also needs a decision.

### Rejection

A node or an exception holds the fields in its front matter. A directive holds them as sub-items:

```markdown
- Run `npm test` before each commit. ^run-npm-tests
  - scope: node
  - basis: judgment
  - status: rejected
  - rejection_reason: The project uses pnpm, and use-pnpm covers the test command.
  - origin: project
```

- Write the reason in one line, in the words of the person, with no name and no email.
- Write the reason as plain text, with no backticks. The parser rejects a code span inside the value.
- Before you reject a node, leave no `proposed` or `accepted` directive or exception in it.
- Before you reject an entity, remove each reference to it from the entities that are not `rejected`.

### Eval signals

```sh
git grep -n -E '^- `[a-z0-9-]+`: [0-9-]+, eval\.' -- knowledge/
```

- The `evaluate-knowledge` skill writes each hit. The line gives the passes with and without the discipline.
- A hit for a `proposed` directive is its signal. A hit for an `accepted` directive proposes its deprecation.
- An eval target is a `directive` entry in a `task.yaml` file under `knowledge/evals/`.

### Commands

```sh
knowledge/.densho/densho accept <id> <id>
knowledge/.densho/densho accept <node-id>:<directive-id>
knowledge/.densho/densho accept --subtree <node-id>
knowledge/.densho/densho accept --dry-run <id>
knowledge/.densho/densho view
grep -rl -F -e '^<id> (proposed)' build/runtime-proposals/
```

- `--subtree` follows `broader`. Only the subtree of the root reaches a skill, so name a skill by its ID.
- `knowledge/.densho/densho view` writes a site to `build/view/`. Its `review.html` groups the queue by node, for the person to read.
- The `grep` search lists each file of the review copy that holds a directive after acceptance.

## References

- Read [Approval](../../references/approval.md).
- Read [Lifecycle](../../references/lifecycle.md).
