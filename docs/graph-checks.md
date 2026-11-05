# Graph checks

> **In the library:** a walk through the whole building. The scanner looks at one card at a time, so only this walk can find a "see also" note that leads to a missing book, or a book that no route reaches.

**Status:** Planned. Nothing on this page exists yet.

## What it does

The parser checks each file on its own, so `broader: [does-not-exist]` passes today. This layer will load every node into one graph and check what only the whole graph can show. A failed check will stop the commit.

| Check        | What will fail                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------ |
| Identity     | Two nodes or directives share an ID, or the graph does not have exactly one root                                   |
| References   | An edge or a pointer names an ID that does not exist                                                               |
| Types        | A `broader` target has a kind the [schema](schema.md#nodes) does not allow, or a skill pointer targets a non-skill |
| Skills       | A skill has neither `uses` nor `applies`                                                                           |
| Ownership    | `implements` starts from a node that is not workspace knowledge                                                    |
| Associations | `related` joins a node to one in its own `broader` chain                                                           |
| Cycles       | A chain of `broader` edges leads back to its start                                                                 |
| Reachability | No chain of pointers from an entry point reaches a node, so an agent could never find it                           |
| Depth        | A node takes too many hops to reach                                                                                |

## How it works

The graph checks will run only after every file parses, because a node that fails to parse would make each reference to it look broken. Each problem will carry the file and line of the field that caused it.

There are two entry points: the root node and the skill listing. An agent tool loads both at session start, and every other node loads when the agent follows a pointer. Reachability follows those same routes.

Not every cycle is a mistake. The taxonomy must stay acyclic so that "broader than" keeps its meaning, while associations such as `related` can loop.

## How it fits

This layer needs the [schema](schema.md) and the [parser](node-format.md). Every later layer relies on its result: inheritance needs a sound hierarchy, and the build needs references that resolve.

## Not settled yet

- The depth limit, and how a hop is counted
- Which edges other than `broader` must stay acyclic, such as `depends_on`
- Whether a node's kind must match its folder, such as a skill under `skills/`
