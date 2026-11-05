# Graph checks

> **In the library:** a walk through the whole building. The scanner looks at one card at a time, so only this walk can find a "see also" note that leads to a missing book, or a book that no route reaches.

**Status:** Built.

The parser checks each file on its own, so `broader: [does-not-exist]` passes it. This layer loads every node into one graph and checks what only the whole graph can show. The code is in `engine/knowledge_architecture/graph/`.

## Run the checks

```sh
uv run ka graph
```

The command reads `knowledge/` and `skills/` in the current folder, or in a folder you name after `graph`. Each problem prints as `path:line: code: message`, and any problem makes the command exit with status 1. The git hook runs the same command on each commit.

An empty tree passes, so a new copy of the template starts clean.

## What fails

| Check        | Code           | What fails                                                                                                                                           |
| ------------ | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Identity     | `duplicate-id` | Two nodes or directives share an ID                                                                                                                  |
| Root         | `root`         | Nodes exist, but none of them is a `ka:Root`                                                                                                         |
| Placement    | `placement`    | A node's kind does not match its folder, including a second root                                                                                     |
| References   | `reference`    | An edge, a pointer, or `also_attached_to` names an ID that does not exist                                                                            |
| Types        | `type`         | A reference names a kind the [schema](schema.md) does not allow, such as a `broader` target of the wrong rank, or a non-skill behind a skill pointer |
| Skills       | `skill`        | A skill has neither `uses` nor `applies`                                                                                                             |
| Ownership    | `implements`   | `implements` starts from a node that is not workspace knowledge                                                                                      |
| Associations | `association`  | `related` joins a node to one in its own `broader` chain, up or down                                                                                 |
| Cycles       | `cycle`        | A chain of `broader` edges, or a chain of `depends_on` edges, leads back to its start                                                                |
| Reachability | `unreachable`  | No chain of pointers from an entry point reaches a node, so an agent could never find it                                                             |
| Depth        | `depth`        | The shortest pointer route to a node takes more than 6 hops                                                                                          |

Two more codes report a graph that the checks cannot read. `schema` means the graph breaks a rule of the graph as a whole, such as a root with no other node. `shape` means the shape check failed in a way that has no location of its own, so the problem points at the root node.

## Placement

The kind of a node sets where its file goes:

- The root is `knowledge/node.md`, and no other node can use that file.
- A skill goes under `skills/`.
- Every other node goes under `knowledge/`.

Inside those folders the path is free. It stays a navigation aid, so a file can move without changing what it means.

## Reachability and depth

There are two entry points: the root node and the skill listing. An agent tool loads both at session start, and every other node loads when the agent follows a pointer. Every skill is in the listing, so every skill is an entry point.

Only pointers count. An edge such as `uses` or `broader` states a relationship, but it gives an agent no route and no trigger for following it. A node that a skill needs and nothing else reaches therefore needs a pointer from that skill.

A hop is one pointer. An entry point is at depth 0, and a node passes at 6 hops or fewer. If several routes reach a node, the shortest one counts, whichever entry point it starts from.

## Cycles

Not every cycle is a mistake. The taxonomy must stay acyclic so that "broader than" keeps its meaning, and a dependency that leads back to itself can never be satisfied. `related`, `informs`, and `governs` can loop, and a node can govern itself.

Each edge kind is checked on its own, so a chain that mixes `broader` and `depends_on` is not a cycle. Each tangled group of nodes gives one problem, which names the shortest cycle through the group's first ID. A group with several cycles can therefore report another one after you fix the first.

## How it works

The checks run in an order that keeps the report free of noise:

1. Every file must parse. A node that fails to parse is left out of the graph, so each reference to it would look broken. A parse problem stops the rest and prints like any other problem.
2. The identity, placement, skill, and ownership checks always run.
3. A duplicate ID stops the rest, because each ID must name one thing.
4. The reference, association, and cycle checks run next.
5. A broken reference or a wrong number of roots stops the type, reachability, and depth checks.

The type check uses SHACL, with shapes generated from the [schema](schema.md), so each range lives in one place. networkx handles cycles, reachability, and depth. The rules the schema does not state are plain Python.

## How it fits

This layer needs the [schema](schema.md) and the [parser](node-format.md). Every later layer relies on its result: inheritance needs a sound hierarchy, and the build needs references that resolve.

## What it does not check yet

- Whether a `paths` pattern on a path pointer matches any file
- Whether a trigger is well written. See [language checks](language-checks.md).
- Links in the body text of a node. Only edges and pointers count as references.
- Whether the target of `implements` is domain knowledge. Only the source is checked.
- A node that names itself in `related`
- The `status` of a node. A pointer to a `deprecated` node passes. See [governance workflow](governance-workflow.md).
- Nodes outside `knowledge/` and `skills/`, such as policy nodes under `governance/policies/`
- What a commit will hold. The command reads the working tree, so an untracked node counts.
