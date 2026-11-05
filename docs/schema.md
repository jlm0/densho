# Schema

`governance/schema/metamodel.yaml` defines what can exist in the knowledge graph: the node kinds, the fields they hold, and how they connect. It holds no knowledge itself. The Python models in `engine/knowledge_architecture/generated/` are generated from it, and the parser validates each node against those models.

Each class inherits the fields of the class above it:

```text
KnowledgeGraph            one root and the knowledge nodes

GovernedEntity            id, status, origin, sources
├─ Node                   kind, title, pointers, directives, body
│  ├─ Root                the top node
│  └─ KnowledgeNode       knowledge_type
│     ├─ TaxonomyNode     definition and the relationship edges
│     │  ├─ Domain
│     │  ├─ Discipline
│     │  ├─ PracticeArea
│     │  └─ Concept
│     └─ Skill            description, uses, applies
└─ Directive              text, scope, also_attached_to

Pointer                   kind, target, trigger
├─ AlwaysPointer
├─ PathPointer            paths
├─ SkillPointer
└─ TextPointer
```

`GovernedEntity`, `Node`, `KnowledgeNode`, `TaxonomyNode`, and `Pointer` are abstract. They only pass on fields, so no file can use them as its kind.

## Nodes

A node's `kind` selects its class. The value is the class name with the `ka:` prefix, such as `ka:Concept`.

| Kind              | What it is                                                  | `broader` can name                              |
| ----------------- | ----------------------------------------------------------- | ----------------------------------------------- |
| `ka:Root`         | The top node. Agents load it first. It needs a pointer.     | Has no `broader`                                |
| `ka:Domain`       | The top level of the taxonomy                               | Has no `broader`                                |
| `ka:Discipline`   | A field of work in a domain                                 | A domain                                        |
| `ka:PracticeArea` | A narrower area of work                                     | A domain, discipline, or practice area          |
| `ka:Concept`      | A principle, a technique, or a body of knowledge            | A domain, discipline, practice area, or concept |
| `ka:Skill`        | A reusable capability that composes knowledge from anywhere | Has no `broader`                                |

`broader` is required where the table allows it, and it can name more than one node, so the taxonomy is not limited to a strict tree.

## Field values

| Field            | Values                               | Meaning                                                                           |
| ---------------- | ------------------------------------ | --------------------------------------------------------------------------------- |
| `status`         | `proposed`, `accepted`, `deprecated` | Whether a reviewer approved the entity, or whether it stays only for reference    |
| `origin`         | `template`, `project`                | Whether the template or the project added the entity                              |
| `knowledge_type` | `domain`, `workspace`                | Universal knowledge, or knowledge specific to one project                         |
| `scope`          | `node`, `subtree`                    | A directive applies to the nodes it attaches to, or also to every node under them |

An `id` is a lowercase hyphenated slug. It stays the same when a file moves.

## Edges

An edge states a relationship. Each edge is a field on the node that holds it, and its value is a list of IDs.

| Edge         | Meaning                                                    | Available on                      |
| ------------ | ---------------------------------------------------------- | --------------------------------- |
| `broader`    | The parent in the taxonomy                                 | Discipline, PracticeArea, Concept |
| `related`    | An association that holds in both directions               | Taxonomy nodes                    |
| `informs`    | This node has an influence on the other                    | Taxonomy nodes                    |
| `depends_on` | This node needs the other                                  | Taxonomy nodes                    |
| `governs`    | This node sets rules for the other, or for itself          | Taxonomy nodes                    |
| `implements` | This workspace node gives project values for a domain node | Taxonomy nodes                    |
| `uses`       | Knowledge that the skill composes                          | Skill                             |
| `applies`    | Directives that the skill applies                          | Skill                             |

## Pointers

A pointer is a route to a node: it names a `target`, the `trigger` that tells an agent to follow it, and through its kind, how the node gets loaded.

| Kind               | How the target loads                                                   |
| ------------------ | ---------------------------------------------------------------------- |
| `ka:AlwaysPointer` | The agent tool loads it at session start                               |
| `ka:PathPointer`   | The agent tool loads it when the agent opens a file in `paths`         |
| `ka:SkillPointer`  | The agent picks it from the skill listing. The target must be a skill. |
| `ka:TextPointer`   | The agent opens it after it reads the pointer text                     |

## Directives

A directive is one instruction with its own ID. It lives in the file of one node, and other nodes attach to it with `also_attached_to`. `scope` has no default, so every directive states how far it reaches. A directive on the root with `scope: subtree` applies to the whole graph.

## Rules for rules

Governance is written in the same classes as everything else: a governance node is an ordinary node, and `governs` names what it sets rules for, which can include itself. Only `metamodel.yaml` stays outside the graph, because it defines what a node is.

## What the models do not check yet

The models read one node at a time and hold each reference as a plain string. Nothing yet checks that:

- an ID is unique
- a reference names something that exists
- a `broader` target has an allowed kind
- a skill pointer's target is a skill
- a skill has at least one of `uses` or `applies`
- `implements` starts from a workspace node
- `related` does not join a node to one in its own `broader` chain

## Change the schema

After you edit `metamodel.yaml`, regenerate the Python models:

```sh
uv run pre-commit run schema-models --all-files
```

The command rewrites the models and reports a failure when they changed. Stage the new models and run it again. The git hook runs the same step on each commit, so a schema change cannot land without its models, and a hand edit to the models does not survive.
