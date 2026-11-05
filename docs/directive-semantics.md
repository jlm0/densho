# Directive semantics

> **In the library:** the rules about signs. A "no food" sign at the entrance may or may not cover every room, so the system has to say which rooms it covers, where it stops, and what happens when two signs disagree.

**Status:** Built.

This layer works out which directives apply at each node and checks that the answer holds together. The code is in `engine/knowledge_architecture/directives/`.

The checks read structure and declarations. They cannot tell whether two sentences contradict each other, so that stays a matter for review. See [what a pass does not mean](#what-a-pass-does-not-mean).

## Run the checks

```sh
uv run ka directives
```

The command reads `knowledge/`, `skills/`, and `governance/` in the current folder, or in a folder you name after `directives`. Each problem prints as `path:line: code: message`, and any problem makes the command exit with status 1. An empty tree passes.

These checks need a sound hierarchy, so the command runs the [graph checks](graph-checks.md) first. A parse or graph problem prints and stops the directive checks.

The git hook runs the same command when a commit touches `knowledge/`, `skills/`, `governance/`, `engine/`, or `uv.lock`. A commit that only deletes files skips it. A deletion can change what applies elsewhere only through a reference to the deleted node, and the graph checks run on every commit and report that reference.

To see what applies at one node, and how each directive gets there:

```sh
uv run ka directives --at unit-tests
```

```text
write-test-first (subtree) from software-testing -> unit-tests: Write a failing test before you change behavior.
1 directives apply at unit-tests, 0 proposed, 0 problems
```

## What applies where

The hierarchy alone never passes a rule down. Each directive states its reach through `scope`, which has no default:

| `scope`   | Reach                                                                      |
| --------- | -------------------------------------------------------------------------- |
| `node`    | Only the nodes it attaches to, and each skill that uses one of them        |
| `subtree` | The nodes it attaches to, and each node under them, including those skills |

A directive attaches to the node that holds it and to each node in its `also_attached_to`. A skill can also attach one by naming it in `applies`. A directive always applies at a node it attaches to.

One node is under another through `broader` edges, followed down from parent to child. Every node is under the root, so a `subtree` directive on the root covers the whole graph, skills included. A directive never travels up, or to a sibling.

No other edge carries a directive. `related`, `informs`, `depends_on`, `governs`, `implements`, and pointers state a relationship or a route, and nothing more. To reach a node across one of them, use `also_attached_to`.

Only an `accepted` directive is in force. A `proposed` directive binds nobody until a reviewer accepts it, and a `deprecated` directive applies nowhere. The `status` of a node does not change what it carries. See [governance workflow](governance-workflow.md).

The checks read two states: what is in force, and what would apply if a reviewer accepted every proposal. So a proposal that conflicts with an accepted rule fails before the review.

## Skills

A skill is an entry point in the middle of the tree, and it has no `broader` edge. These directives apply at a skill:

- Each directive attached to it, through its own file, `also_attached_to`, or `applies`
- Each `subtree` directive attached to the root
- Each `subtree` directive that applies at a node in `uses`
- Each `node` directive attached to a node in `uses`

A skill carries the `node` directives of what it uses because an agent can come in through the skill and never open the node. Directives on nodes below a used node do not apply, because a directive never travels up.

Nothing can sit under a skill, so `node` and `subtree` mean the same thing on one.

## Stepping out

A node can step out of a directive it would otherwise inherit. List the directive under `exceptions` in the front matter, with a reason and a status:

```markdown
---
id: prototypes
kind: ka:PracticeArea
title: Prototypes
status: accepted
origin: project
knowledge_type: workspace
broader: [software-testing]
exceptions:
  - directive: write-test-first
    reason: A prototype is thrown away before it ships.
    status: accepted
---

## Definition

Code written to try out an idea.
```

The directive stops at this node and at each node it could only reach through this node, once the exception is `accepted`. A `proposed` exception stops nothing, so a rule can't be switched off without a review, and a `deprecated` one stays only for reference. The [governance workflow](governance-workflow.md) has the steps. Exceptions name one directive at a time. There is no switch that stops all inheritance, because that would also hide every rule added above the node later.

The narrower node holds the exception, so a project can step out of a template rule without editing the template's file. The root cannot hold one, because nothing is above it.

To bring a directive back further down, attach it to that lower node with `also_attached_to`.

## More than one route

`broader` can name several parents, so a directive can reach a node along several routes. The directive applies if any route reaches the node, and it applies once. A rule stays in force until every route stops.

When one route stops and another still reaches the node, the author of the exception probably expected the rule to stop, so the check reports `route-conflict` at the node where the routes meet. Settle it at that node, one way or the other:

- To stop the directive, add an exception at that node.
- To keep the directive, attach it to that node. A skill can name it in `applies`.

A skill counts its link to the root and its link to each used node as routes, so a skill that uses a node with an exception gets the same report for a directive that also reaches it from the root.

## When two directives disagree

A check can't tell from the words whether a narrower directive refines a broader one or contradicts it, so the author says which.

Use `refines` when both rules apply and the narrower one adds detail:

```markdown
## Directives

- Write a test for each public function. ^test-public-functions
  - scope: subtree
  - status: accepted
  - origin: project
  - refines: write-test-first
```

The check requires the refined directive to apply at every node where the refining directive applies. That is the structural meaning of "narrower", and it catches a refinement left behind when the broader rule stops.

When a narrower rule contradicts a broader one, the two can't both apply. Add an exception for the broader rule, with the reason, and write the narrower rule on the same node.

Use `conflicts_with` to record a pair that must never apply at one node:

```markdown
## Directives

- Use a fixture for each database. ^use-a-fixture
  - scope: subtree
  - status: accepted
  - origin: project
  - conflicts_with: use-a-live-database
```

One side is enough. A person decides the pair once, and the check then finds every node where both apply, now and after later changes. This matters most for skills, which compose branches that otherwise never meet.

The check also compares text in one narrow way. It reports two directives that apply at one node when one is the other with `Do not`, ignoring case and spacing. `If a test fails, stop the release.` and `If a test fails, do not stop the release.` are a match. `Use a mock.` and `Avoid a mock.` are not.

## What fails

| Code                 | What fails                                                                    |
| -------------------- | ----------------------------------------------------------------------------- |
| `exception-unused`   | An exception stops nothing, because no route brings the directive to the node |
| `exception-attached` | A node attaches a directive and also steps out of it                          |
| `exception-repeated` | A node names one directive in two exceptions                                  |
| `route-conflict`     | One route to a node stops, and another still reaches it                       |
| `conflict`           | Two directives in a `conflicts_with` pair apply at one node                   |
| `opposite`           | A rule and the same rule with `Do not` apply at one node                      |
| `refines-outside`    | A directive applies at a node where the directive it refines does not         |
| `refines-cycle`      | A chain of `refines` leads back to its start                                  |
| `applies-deprecated` | A skill names a `deprecated` directive in `applies`                           |

An exception under another exception fails as `exception-unused`, because the one above already stopped the route. So does an exception for a `deprecated` directive. These checks read a `proposed` exception as if it were accepted, and they skip a `deprecated` one.

An `accepted` directive that refines a `proposed` one fails `refines-outside`, because only the narrower rule is in force.

A `refines`, a `conflicts_with`, or an exception that names a missing ID, or an ID that is not a directive, fails earlier as a `reference` or `type` problem from the [graph checks](graph-checks.md).

## What a pass does not mean

A check can read the graph and the declarations. It cannot read meaning.

| Question                                 | A check catches                                    | Review still decides                               |
| ---------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| Do two directives contradict each other? | A declared pair, and an exact `Do not` mirror      | Any contradiction in other words                   |
| Does a directive refine another?         | A refinement that reaches outside the broader rule | Whether the narrower rule is narrower in meaning   |
| Should this node step out?               | An exception that stops nothing                    | Whether the reason is sound, before it is accepted |
| Is `scope` right for this directive?     | Nothing                                            | All of it                                          |

`uv run ka directives --at <node-id>` gives a reviewer the list to read.

## Use it from code

```python
from knowledge_architecture.directives import resolve_directives

applied = resolve_directives(items).at("write-tests")
```

`items` are parsed nodes that passed the graph checks. The result holds what is in force. Pass `proposals=True` to see what would apply if a reviewer accepted every proposal. Each entry has the `directive`, the `holder` (the ID of the node whose file holds it), and the `route` from the attached node to this one. The route is the shortest one, with a fixed order on a tie, because a graph can hold too many routes to list. The longest route comes first, so broad rules come before narrow ones.

## How it fits

This layer needs the sound hierarchy from [graph checks](graph-checks.md). The [runtime files](runtime-files.md) use its result, because a skill has to carry the rules that apply to it.

## What it does not check yet

- Meaning. See the table above.
- The `reason` of an exception, beyond being one line. The [language checks](language-checks.md) do not read it.
- What a commit will hold. The command reads the working tree, so an untracked node counts.
