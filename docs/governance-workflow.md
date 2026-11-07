# Governance workflow

> **In the library:** the acquisitions policy, which says who can add or change a book and how. Without it the library is tidy, but anyone can change anything.

**Status:** Built.

The other checks prove that knowledge is well formed. This layer decides whether it is in force: what a proposal can do before anyone reviews it, which changes reopen a review, and how a change gets promoted. The policies are nodes in `knowledge/governance/policies/`, and the code is in `engine/governance/`.

A local check has limits here. It can compare a change with the last commit, but it can't tell who made the change or whether anyone read it. See [what a check can and cannot prove](#what-a-check-can-and-cannot-prove).

## Run the checks

```sh
uv run ka governance
```

The command reads `knowledge/` in the current folder, or in a folder you name after `governance`. Each problem prints as `path:line: code: message`, and any problem makes the command exit with status 1. An empty tree passes.

The git hook runs the same command on each commit, including a commit that only deletes files.

To list what waits for review:

```sh
uv run ka governance --pending
```

```text
knowledge/nodes/retries/node.md:5: node retries
knowledge/nodes/retries/node.md:17: directive retry-with-backoff
2 entities wait for review, 0 problems
```

## The lifecycle

Each node, directive, and exception has its own `status`:

| `status`     | Meaning                                                  | A directive or an exception is |
| ------------ | -------------------------------------------------------- | ------------------------------ |
| `proposed`   | An author recommends it, and no reviewer has approved it | Not in force, but checked      |
| `accepted`   | A reviewer approved this content                         | In force                       |
| `deprecated` | It stays only for reference                              | Not in force                   |
| `rejected`   | A person turned it down                                  | Not in force, and left out     |

`status` is the only thing that keeps experimental knowledge apart from authoritative knowledge. There is no separate folder for drafts, because a folder never carries meaning here.

Domain knowledge and workspace knowledge follow the same lifecycle and the same rules, so a project governs its own knowledge the way the template governs what it ships.

## What is in force

An unreviewed sentence should not be able to bind an agent or switch off a rule, so:

- Only an `accepted` directive applies.
- Only an `accepted` exception stops a directive. While the exception is `proposed`, the directive stays in force at that node.
- A `rejected` entity applies nowhere. The compiled graph, the runtime files, and the site leave it out, and so do its directives and exceptions.
- Apart from `rejected`, the `status` of a node does not change what applies. It covers the node's own definition and place in the tree. Otherwise a small edit to a definition would switch off every rule on that node.

`uv run ka directives --at <node-id>` shows what is in force at a node, and it labels what a review would change:

```text
run-tests (subtree) from sample -> child: Run `pytest` before you commit.
proposed: use-a-fixture (subtree) from sample -> child: Use a fixture for each database.
proposed: an exception stops run-tests here
1 directives apply at child, 1 proposed, 0 problems
```

[`uv run ka build`](compiled-outputs.md) follows the same rule: its default output holds only what is in force.

A proposal is not exempt from the checks. The [directive checks](directive-semantics.md) run twice, once on what is in force and once as if every proposal were accepted, so a conflict shows up before the review and not after it.

There is one cost. When you reopen an accepted rule to change it, the rule is out of force until a reviewer accepts the new text. The diff shows that gap, and the alternative is a rule that binds with text nobody has approved.

## Who does what

An agent can propose a concept, a directive, or an exception by adding it with `status: proposed`. A person approves it and runs [`ka accept`](human-interface.md#accept-what-you-approve), or [rejects it](#reject-something).

The [`approval` policy](#the-policies) states this as directives. No check can enforce it, for the reasons [below](#what-a-check-can-and-cannot-prove). A project decides who its reviewers are, and a node never records a name or an email. Git history already holds the author of each commit.

## Make a change

### Add something

Add the node, directive, or exception with `status: proposed`. Anything new with another status fails `new-status`.

### Accept something

Promotion takes two commits, so a reviewer approves exactly the text that the last commit holds:

1. An author commits the entity as `proposed`.
2. A reviewer runs `uv run ka view` and reads the entity, its reasons, and what applies in `build/view/review.html`. In a terminal, `uv run ka governance --pending` and `uv run ka directives --at <node-id>` give the same facts.
3. A later commit changes `status` to `accepted` and changes nothing else that needs review. [`uv run ka accept`](human-interface.md#accept-what-you-approve) makes that change in the working tree.
4. That commit also holds the [runtime files](runtime-files.md) that `uv run ka runtime` writes, because the accepted directive now reaches them.

One commit can promote any number of entities, so a person can accept a whole batch at once.

### Reject something

A person who turns a proposal down sets its `status` to `rejected` and adds `rejection_reason`, one line that says why:

```yaml
status: rejected
rejection_reason: The project keeps one style guide, and this rule repeats it.
```

In a directive or an exception the field sits next to `status`, in the same form. There is no `ka reject`, so you edit the line by hand, or let the `review-proposals` skill write your reason for you, as the [improvement loop](improvement-loop.md#review-the-queue) explains. The reason needs no review, so you can reword it later.

The entity stays in the file as a record that someone weighed it, so the same idea doesn't come back unread. `--pending` stops listing it, and no generated file holds it. To look at it again, set it back to `proposed`. It can't go straight to `accepted`, which fails `status-jump`, so a reviewer reads it again first. When nobody needs the record any more, delete the entity. Git history keeps it.

Only a proposal can be rejected. An `accepted` or `deprecated` entity that goes straight to `rejected` fails `status-jump`. Set an `accepted` one to `deprecated` instead, and delete it later if nobody needs it.

Before you reject a node, leave nothing live in it, and move what rests on it:

- A `rejected` node can't hold a `proposed` or `accepted` directive or exception. That fails `rejected-holder`.
- Only a `rejected` entity, or an entity in a `rejected` node, can name a `rejected` one in an edge, pointer, exception, `applies`, or directive field. Anything else fails `rejected-reference`, so the nodes under a rejected node have to move too.
- The root can't be rejected, because it holds the graph. That fails `rejected-root`.

### Change something accepted

Set `status` back to `proposed` in the same commit as the change, then accept it again later. These fields reopen a review, and the rest do not:

| Entity    | Reopens a review                                                                                                             | Does not reopen a review                                                               |
| --------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Node      | Every other field: `kind`, `definition`, `knowledge_type`, each edge, and a skill's `description`, `invocation`, and scripts | `title`, `body`, `pointers`, `sources`, `rejection_reason`, `exceptions`, `directives` |
| Directive | `text`, `scope`, `basis`, `also_attached_to`, `refines`, `conflicts_with`, and the node that holds it                        | `sources`, `rejection_reason`                                                          |
| Exception | `reason`                                                                                                                     | `rejection_reason`                                                                     |

A pointer does not reopen a review, because every new node needs a pointer and would otherwise reopen its parent. The [graph checks](graph-checks.md) still prove the route, and a reviewer reads the trigger. A node's `exceptions` and `directives` have their own `status`, so adding one leaves the node alone.

The scripts of a skill count as one field. The check hashes the path, the bytes, and the executable bit of each file under the skill's `scripts/` folder, so a script that changes, arrives, goes, moves, or becomes executable reopens the skill.

The comparison uses rendered Markdown and ignores the order of a list, so a formatter can't reopen a review. A moved file is the same entity, because its ID identifies it.

### Remove something

Set an `accepted` node or directive to `deprecated` in one commit, and delete it in a later commit. A `proposed`, `deprecated`, or `rejected` entity can go at any time, and so can an exception.

This rule also keeps IDs stable. Renaming an accepted ID looks like a removal, so it fails. Deprecate the old ID and add a new one instead.

Before you deprecate a node, move the nodes under it and the directives on it. `deprecated-holder` and `deprecated-reference` report what still rests on it. A pointer to a `deprecated` node passes, because the node stays for reference and every node needs a route.

### Step out of a rule

An exception follows the same path as everything else. [Directive semantics](directive-semantics.md#stepping-out) shows the format. It has no effect until a reviewer accepts it, and the reviewer decides whether its `reason` is sound.

## Knowledge from the template

A project owns its copy, so it can change or delete anything it received, and no rule reads `origin` to prevent that. It goes through the same steps as its own knowledge: reopen the entity, deprecate it, or reject it.

`origin` records who added an entity, so it does not change, and the template ships no workspace knowledge. A project can add domain knowledge of its own.

Everything from the template counts as new, in a new repo and in one with history. It arrives as `proposed`, and a person accepts it. [The install](template-packaging.md#which-status-knowledge-arrives-with) sets those statuses for you, and a later pull follows the same rule.

The install can also keep what the template already accepted. Then `new-status` lets an `accepted` entity through when the template's `knowledge/.ka/history.jsonl` holds its last line as `accepted`, with the same digest for each field. This narrow pass holds only while the last commit has no `knowledge/.ka/history.jsonl`, so it covers the install commit and never a pull. A history file that doesn't parse or replay gives no pass.

## What fails

| Code                   | What fails                                                                                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `new-status`           | An entity that the last commit does not have, with a status other than `proposed`, unless the [narrow pass](#knowledge-from-the-template) covers it |
| `promotion-change`     | One commit accepts an entity and also changes a field that needs review                                                                             |
| `accepted-change`      | An entity stays `accepted`, and a field that needs review changes                                                                                   |
| `status-jump`          | An entity goes from `deprecated` or `rejected` straight to `accepted`, or from `accepted` or `deprecated` to `rejected`                             |
| `origin-change`        | The `origin` of a node or a directive changes                                                                                                       |
| `removed-accepted`     | An `accepted` node or directive leaves the tree. When `disciplines` leaves out its discipline, the message says so                                  |
| `template-workspace`   | `origin: template` on a workspace node, or on a directive in one                                                                                    |
| `deprecated-holder`    | A `deprecated` node holds a directive that is `proposed` or `accepted`                                                                              |
| `deprecated-reference` | A live entity names a `deprecated` one in `broader`, `uses`, `depends_on`, `implements`, `also_attached_to`, or `refines`                           |
| `rejected-reason`      | A `rejected` entity has no `rejection_reason`                                                                                                       |
| `rejected-holder`      | A `rejected` node holds a directive or an exception that is `proposed` or `accepted`                                                                |
| `rejected-reference`   | An entity that isn't `rejected`, and isn't in a `rejected` node, names a `rejected` one in any reference                                            |
| `rejected-root`        | The root is `rejected`                                                                                                                              |
| `basis`                | A directive with no `sources` has a `basis` other than `judgment`, or a directive with `sources` has `judgment`                                     |
| `source-form`          | A value in `sources` is not an `https` or `http` URL with a host, a file path from the repository root, or a citation of two or more words          |
| `secret`               | A line of a file in `knowledge/` holds what reads as a key, a token, a password, or a private key                                                   |
| `email`                | A line of a file in `knowledge/` holds an email address                                                                                             |
| `policy-governs`       | A policy has no `governs`, or no policy names it in `governs`                                                                                       |
| `base`                 | Git can't read the last commit                                                                                                                      |

The state rules need only the working tree. The change rules also need a last commit, and the command prints a `note:` and skips them when:

- The folder is not a git repository, git is not installed, or the repository has no commit yet.
- A merge is in progress. The commits on the branch went through the hook, and comparing a whole branch at once would fail on each promotion in it.
- A node file in the last commit does not parse, for example after a schema change. Only that file is skipped.

## What a check can and cannot prove

This repo has no CI, so the git hook is the only gate.

| A check can prove                                              | A check cannot prove                                              |
| -------------------------------------------------------------- | ----------------------------------------------------------------- |
| The working tree holds the state rules                         | Who changed a `status`, or that the person who did was allowed to |
| The difference from the last commit follows the change rules   | That anyone read the change before it was accepted                |
| A promotion changed nothing that needs review                  | That a reason is sound, or that a rule is a good rule             |
| Each policy passes the same checks as the knowledge it governs | That an agent obeyed a rule                                       |

The checks also have gaps that a person can use, on purpose or by accident:

- A commit with `--no-verify`, or a clone with no hook installed, skips every check.
- `git commit --amend` compares with the commit it replaces, so proposing in one commit and promoting in an amend looks like a plain promotion.
- A rebase or a fast-forward merge runs no hook, and nothing reads old commits later.
- Anyone can run `ka accept`, or write `status: accepted`, in a second commit and call it approved.

So `accepted` is a claim that the project's history supports, not a proof. A reviewer who wants to check it reads `git log -p` for the commit that changed the `status`.

## The policies

The rules above are written down as ordinary nodes under `knowledge/governance/policies/`, so an agent can load them like any other knowledge:

| Node             | What it holds                                                |
| ---------------- | ------------------------------------------------------------ |
| `governance`     | The domain: the rules for every commit, and the routes below |
| `lifecycle`      | What each `status` means and how an entity leaves the tree   |
| `approval`       | Who approves, and what a reviewer reads                      |
| `change-rules`   | Which changes reopen a review                                |
| `language-rules` | The grammar and the vocabulary, named as sources             |
| `schema-rules`   | The metamodel, named as a source                             |

The folder is part of the graph. Every command reads it, a policy needs a pointer like any node, and a node elsewhere under `knowledge/governance/` fails `placement`. The root node reaches the `governance` domain through a path pointer on `knowledge/`, so an agent tool loads these rules when an agent opens a node file. They do not attach to the root, because that would copy them into every skill, where they don't help.

`governs` names what a policy sets rules for. Each policy must name something, and a policy must name each policy. The `governance` domain names itself, which closes the loop: the rules for rules follow their own rules, and they start as `proposed` like everything else.

You can change or delete these policies in your own copy. The checks read them as data and do not depend on them. If you delete them, point the root at your own domain in the same commit, or delete the root too. The language checks still need `knowledge/governance/language/`. [Template packaging](template-packaging.md#what-you-can-delete-from-governance) lists what a project can delete.

## How it fits

This layer sits on top of the [graph checks](graph-checks.md) and the [directive semantics](directive-semantics.md), and it changes one answer from the latter: which directives are in force. The [runtime files](runtime-files.md) use that answer, so a proposal does not reach an agent as a rule, and the [human interface](human-interface.md) shows it to a person.

## What it does not check yet

- Who approved a change. Nothing local can. See the table above.
- Where `knowledge/.ka/history.jsonl` came from. The narrow pass reads the working copy, so an edited file in the install commit can let an `accepted` entity through.
- Old commits. The comparison covers one step, from the last commit to the working tree.
- Whether a change to `body`, `title`, or a pointer's trigger changes what an agent does. These count as routine, so a reviewer has to catch it.
- A `broader` edge on a `proposed` node. It carries directives as soon as it exists, so moving a node can drop a rule before anyone reviews the move. The `status` change and the diff show it.
- Whether a `deprecated` rule is reused under a new ID, or a deleted ID comes back with a new meaning
- Whether a `basis` fits its source. The check reads only whether `sources` is empty and the form of each value, so `standard` on a blog post passes.
- What a script does. The checks never read one, so a reviewer reads each script.
- Who rejected an entity. Only a `proposed` entity can move to `rejected`, but nothing local can tell who made the change.
- A name in a node. The `no-personal-data` directive states the rule, and a reviewer enforces it. The `email` check finds an email address, and an SSH remote such as `git@github.com:` reads as one too, so write the `https` form.
- Secret material in a form that no pattern of the `secret` check knows. The check reads each line on its own, so a key split over two lines passes.
- Whether a source page exists or says what the directive says. The checks run with no network.
- Changes to `knowledge/governance/language/` and `knowledge/governance/schema/`. They have no `status`, so they reach a reviewer only through the diff.
