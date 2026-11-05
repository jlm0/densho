# Directive semantics

> **In the library:** the rules about signs. A "no food" sign at the entrance may or may not cover every room, so the system has to say which rooms it covers, where it stops, and what happens when two signs disagree.

**Status:** Planned. The `scope` and `also_attached_to` fields exist in the [schema](schema.md#directives). Nothing else on this page exists yet.

## What it does

This layer will work out which directives apply at each node, and it will check that the answer is consistent. It covers three things:

- **Inheritance:** a directive on a broader node reaches the nodes under it.
- **Exceptions:** a narrower node can step out of a directive it would otherwise inherit.
- **Conflicts:** two directives that apply to one node can disagree.

## How it works

The hierarchy alone never passes a rule down. Each directive states its reach through `scope`, which has no default:

| `scope`   | Reach                                        |
| --------- | -------------------------------------------- |
| `node`    | Only the nodes the directive attaches to     |
| `subtree` | The attached nodes and every node under them |

A directive lives in one file, and `also_attached_to` attaches it to other nodes.

## How it fits

This layer needs the sound hierarchy from [graph checks](graph-checks.md). The [runtime files](runtime-files.md) use its result, because a skill is an entry point in the middle of the tree and has to carry the rules it inherits.

## Not settled yet

- Whether inheritance can stop, and how an exception is written
- How a conflict is detected, and which conflicts a check can find without review
- Whether a narrower directive refines a broader one or contradicts it
