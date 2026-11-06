# Compiled outputs

> **In the library:** the printed catalog. People keep working with the books, while tools read one complete listing, and a fingerprint shows whether two printings match.

**Status:** Built.

This layer compiles the checked Markdown into JSON and RDF, so a tool can read the whole graph without parsing a node file. The same source always gives the same bytes, so a digest shows whether two builds hold the same knowledge. The code is in `engine/compiler/`.

## Build

```sh
uv run ka build
```

```text
in_force: This result holds only the accepted directives and exceptions. It leaves out each proposal.
graph.json sha256:cfcfcad0…
graph.ttl sha256:9f528066…
digest sha256:f4d8a64c…
3 nodes and 1 directives compiled, 1 directives left out, 0 problems
```

The command reads `knowledge/` in the current folder, or in a folder you name after `build`. It reads the tree once, then runs the [graph](graph-checks.md), [directive](directive-semantics.md), [governance](governance-workflow.md), and [language](language-checks.md) checks on what it read and compiles that same reading. A file that changes during a build can't slip past the checks.

Each problem prints as `path:line: code: message`, and any problem makes the command exit with status 1. A tree that fails a check writes nothing and also removes any earlier output, so `build/compiled/` never holds a graph for a tree that no longer passes.

The git hook runs the same command when a commit touches `knowledge/`, `engine/`, or `uv.lock`. A commit that only deletes files skips the hook.

Git ignores `build/`, and the repo doesn't commit this output. You can make it again from the source, and the digest proves the match.

## What a build writes

Each result writes three files to `build/compiled/`:

| Result    | Graph as JSON          | Graph as RDF Turtle   | Digests                  |
| --------- | ---------------------- | --------------------- | ------------------------ |
| In force  | `graph.json`           | `graph.ttl`           | `digests.json`           |
| Proposals | `graph.proposals.json` | `graph.proposals.ttl` | `digests.proposals.json` |

## In force by default

The default result is what binds an agent today. It follows the [governance workflow](governance-workflow.md): it holds only `accepted` directives and `accepted` exceptions.

| Entity                  | Default result | With `--proposals` |
| ----------------------- | -------------- | ------------------ |
| Node, unless `rejected` | Kept           | Kept               |
| `accepted` directive    | Kept           | Kept               |
| `proposed` directive    | Left out       | Kept               |
| `deprecated` directive  | Left out       | Left out           |
| `accepted` exception    | Kept           | Kept               |
| `proposed` exception    | Left out       | Kept               |
| `deprecated` exception  | Left out       | Left out           |
| Any `rejected` entity   | Gone           | Gone               |

Every entity keeps its `status` in the output. A node stays whatever its status, because the status of a node doesn't change what applies. `rejected` is the one exception: a rejected node goes from both results with everything in it, and so does a rejected directive or exception. The left-out count doesn't count them either, because a person already decided against them.

An exception also goes when its directive goes, and so does a reference to a left-out directive in `applies`, `refines`, or `conflicts_with`. Every reference in the output therefore resolves.

A tree where nothing has been accepted yet compiles to a graph with no directives. That isn't a tree with no rules, so the JSON counts what it left out, and `ka build` prints the count.

## See what acceptance would change

```sh
uv run ka build --proposals
```

This writes a separate result that also holds each proposal, with its own digest. It runs the same checks, and it leaves the default result alone. The marks are hard to miss:

- Each file name holds `proposals`.
- The JSON opens with `"result": "proposals"` and a notice that starts `NOT IN FORCE`, and the Turtle file opens with the same notice as a comment.
- The Turtle file holds the triple `ka:result "proposals"`.
- Each directive and exception keeps its `status`, and so does each entry in the JSON's list of what applies.

The result never replaces the default, and its digest differs even when the tree holds no proposal.

## Read the JSON

| Key              | What it holds                                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `result`         | `in_force` or `proposals`                                                                           |
| `notice`         | The same fact, in a sentence                                                                        |
| `format_version` | The version of this layout                                                                          |
| `left_out`       | The count of `directives` and `exceptions` that this result leaves out                              |
| `paths`          | Each node ID, with its file relative to the repository                                              |
| `applied`        | Each node ID, with the directives that apply there: `directive`, `status`, `holder`, and `route`    |
| `graph`          | The `root`, the `nodes`, and the `result`, in the shape of the `KnowledgeGraph` model in the schema |

`applied` comes from the same code as `uv run ka directives --at <node-id>`, and it starts with the longest route. `route` runs from the node where the directive attaches to the node where it applies.

Nodes sort by ID, and so do the directives in a node. Every other list sorts by value and drops repeats, because the order of a list in a file isn't knowledge. Reordering `broader` doesn't change a digest.

## Read the RDF

The Turtle file holds the same `graph`, loaded through the classes generated from the [schema](schema.md). Nodes use SKOS for `prefLabel`, `definition`, `broader`, and `related`, and the `ka:` prefix for almost everything else. It doesn't hold `paths` or `applied`.

```sparql
PREFIX ka: <https://github.com/jlm0/knowledge-architecture/schema/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?child ?parent WHERE {
  ?child skos:broader ?parent ;
         ka:status "accepted" .
}
```

The classes are plain `ka:` classes, such as `ka:Concept`. To treat a taxonomy node as a `skos:Concept`, also load `engine/generated/metamodel.owl.ttl`, which states that relationship.

## Check a digest

`digests.json` holds the SHA-256 of each graph file and one `digest` for the result. The result digest is the SHA-256 of the two lines that `shasum` prints, so you can work it out without the engine:

```sh
cd build/compiled
shasum -a 256 graph.json graph.ttl | shasum -a 256
```

These things don't change the bytes: the Python hash seed, the order of the files on disk, the folder that holds the repository, and the modified time of a file. The output holds no time stamp and no absolute path. The Turtle file gives each blank node a label from its content, so a run can't reorder them.

## Use it from code

```python
from pathlib import Path

from engine.compiler import compile_tree

report = compile_tree(Path(), proposals=False)
report.problems  # the same problems that ka build prints
report.compiled  # None if a check failed
```

`report.compiled.graph` is the `KnowledgeGraph` model, and `report.compiled.directives` maps each ID in the result to its directive. `report.compiled.applied[node_id]` lists what applies at a node, and `report.compiled.paths[node_id]` names its file. `compile_tree` writes nothing.

## Codes

These codes come from the build. Each other code comes from a check that the build runs.

| Code         | What it reports                                                                    |
| ------------ | ---------------------------------------------------------------------------------- |
| `empty-tree` | The tree holds no node. The checks pass on an empty tree, but no graph exists yet. |
| `path`       | The name of a node file isn't valid UTF-8, so the JSON can't hold it.              |
| `write`      | The build can't change `build/compiled/`, because a file or a permission blocks it |

## What it does not check yet

- Whether the output on disk still matches the source. Nothing compares them until the next build, so a result you don't rebuild can go stale. `ka build` and `ka build --proposals` each rewrite only their own files.
- Whether a generated model matches the schema. The `schema-models` hook checks that, and `ka build` doesn't run it.
- Who built the output. A digest shows that two builds match. It isn't a signature, and it says nothing about whether the knowledge is right.
- Whether two machines agree across different locked versions. A new rdflib release can change the layout of the Turtle file, so compare digests from the same `uv.lock`.
