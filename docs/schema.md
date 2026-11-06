# Schema

> **In the library:** the design of the catalog card. It sets what a card must say about a book and how books can refer to each other. It holds no books itself.

**Status:** Built.

`knowledge/governance/schema/metamodel.yaml` defines what can exist in the knowledge graph: the node kinds, the fields they hold, and how they connect. It holds no knowledge itself. The files in `engine/generated/` are generated from it. The parser validates each node against the Python models, and the [graph checks](graph-checks.md) validate the whole graph against the SHACL shapes.

Each class inherits the fields of the class above it:

```text
KnowledgeGraph            one root, the knowledge nodes, and the result of a build

GovernedEntity            id, status, origin, sources, rejection_reason
├─ Node                   kind, title, pointers, directives, body
│  ├─ Root                the top node
│  └─ KnowledgeNode       knowledge_type, exceptions
│     ├─ TaxonomyNode     definition and the relationship edges
│     │  ├─ Domain
│     │  ├─ Discipline
│     │  ├─ PracticeArea
│     │  └─ Concept
│     └─ Skill            description, invocation, uses, applies
└─ Directive              text, scope, basis, also_attached_to, refines, conflicts_with

DirectiveException        directive, reason, status, rejection_reason

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

| Field            | Values                                             | Meaning                                                                               |
| ---------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `status`         | `proposed`, `accepted`, `deprecated`, `rejected`   | Whether a reviewer approved the entity, kept it only for reference, or turned it down |
| `origin`         | `template`, `project`                              | Whether the template or the project added the entity                                  |
| `knowledge_type` | `domain`, `workspace`                              | Universal knowledge, or knowledge specific to one project                             |
| `scope`          | `node`, `subtree`                                  | A directive applies to the nodes it attaches to, or also to every node under them     |
| `basis`          | `standard`, `research`, `practitioner`, `judgment` | The kind of source behind a directive. See [below](#directives).                      |
| `invocation`     | `agent`, `person`                                  | Whether an agent can start the skill by itself, or only a person can                  |
| `result`         | `in_force`, `proposals`                            | What a [compiled graph](compiled-outputs.md) holds. A source graph has no value.      |

A `rejected` entity also needs `rejection_reason`, one line that records why a person turned it down. The [governance workflow](governance-workflow.md#the-lifecycle) has the rules.

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

`basis` says what kind of source backs the directive, so a reader knows how much weight it carries:

| Value          | The directive rests on                            |
| -------------- | ------------------------------------------------- |
| `standard`     | a published standard or a versioned specification |
| `research`     | an empirical study or a model from research       |
| `practitioner` | a method of a named author or company             |
| `judgment`     | no source                                         |

A directive with no `sources` must say `judgment`. The check doesn't go the other way: a judgment call can still cite a page that it read.

`refines` names a broader directive that this one makes more specific. `conflicts_with` names a directive that must not apply at the same node. A knowledge node or a skill steps out of an inherited directive with an entry in `exceptions`, which holds a `directive`, a one-line `reason`, and its own `status`. The root cannot hold one. [Directive semantics](directive-semantics.md) explains each of these.

## Rules for rules

Governance is written in the same classes as everything else: a governance node is an ordinary node under `knowledge/governance/policies/`, and `governs` names what it sets rules for, which can include itself. `metamodel.yaml` and the files in `knowledge/governance/language/` stay outside the graph. The first defines what a node is, and the second is data that the language checks read. The `schema-rules` and `language-rules` [policies](governance-workflow.md#the-policies) name them as sources.

## What the models do not check

The models read one node at a time and hold each reference as a plain string, so they cannot check that:

- an ID is unique
- a reference names something that exists
- a `broader` target has an allowed kind
- a skill pointer's target is a skill
- a skill has at least one of `uses` or `applies`
- `implements` starts from a workspace node
- `related` does not join a node to one in its own `broader` chain
- `refines`, `conflicts_with`, and an exception each name a directive, not a node

[Graph checks](graph-checks.md) cover each of these points. They read the kinds that an edge can name from this schema, so each of those rules stays in one place.

## Change the schema

The engine reads its own copy of the schema, so you change the schema in the template. A project's `knowledge/governance/schema/metamodel.yaml` is a reference, and editing it changes no check.

After you edit `metamodel.yaml`, regenerate the files in `engine/generated/`:

```sh
uv run pre-commit run schema-models --all-files
```

The command rewrites the Python models, the RDF classes, the SHACL shapes, the ontology, and the engine's copy of the schema, and it reports a failure when any of them changed. Stage the new files and run it again. The lint settings and the template for the Python models sit in `engine/schema/`, so a project doesn't receive them. The git hook runs the same step on each commit, so a schema change cannot land without its generated files, and a hand edit to one of them does not survive.
