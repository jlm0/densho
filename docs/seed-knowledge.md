# Seed knowledge

> **In the library:** the first real books. They give every check real text to read, and they give a new project something to start from.

**Status:** Built.

A project that copies the template receives this knowledge. It is ordinary content: one domain, two skills, and a few language terms, and it goes through the same checks and the same workflow as anything a project adds. Nothing in it binds an agent until a person accepts it.

## What ships

The domain is Digital Product Development, under `knowledge/digital-product-development/`. All four disciplines are there, but only UI/UX Design goes deep, because branch depth follows real classification and does not have to match:

```text
Digital product development
├── Product strategy
├── Brand design
├── UI/UX design
│   ├── Information architecture
│   │   └── Categorization
│   ├── Interaction design
│   │   ├── Progressive disclosure
│   │   └── Navigation
│   ├── Visual design
│   │   ├── Information hierarchy
│   │   ├── Visual grouping
│   │   └── Visual communication
│   ├── Accessibility
│   └── Responsive design
└── Software engineering
```

Directives sit at every level of the taxonomy. A pointer on the root reaches the domain, and pointers lead from there down the tree, so every node is four hops or fewer from the root.

The hierarchy is not the only structure. `informs`, `depends_on`, and `related` record links across branches, such as Product strategy informing the other three disciplines. Those edges state a relationship and carry no directive, so one accessibility rule also attaches to Visual design and Brand design with `also_attached_to`.

## The skills

| Skill                       | Use it when                            | What it draws on                                                                                           |
| --------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `design-settings-interface` | You design or change a settings screen | Progressive disclosure, Information hierarchy, Visual grouping, Accessibility, Brand and Responsive design |
| `review-screen-hierarchy`   | A screen design is ready for review    | Information hierarchy, Visual grouping, Visual communication, and two contrast rules through `applies`     |

A skill source names knowledge and does not copy it. Its body holds only the inputs, the procedure, the output, and how to validate the result. The [generated skill file](runtime-files.md#why-a-skill-holds-a-copy) holds the directives in force. To see every rule a skill carries, with each proposal labeled:

```sh
uv run ka directives --at design-settings-interface
```

`design-settings-interface` also steps out of one inherited rule, because a settings screen has no single primary action. That [exception](directive-semantics.md#stepping-out) is a proposal too, so a reviewer decides whether it stands.

## Accept what you received

Every node, directive, and exception here is `proposed`, so the seed is checked but not in force. `ka directives --at` labels each one as a proposal, and code that asks what is in force gets nothing back until a person reviews it:

```sh
uv run ka governance --pending
```

Read the list, then accept what you want in a commit that changes only `status`. You can do that in one batch. The [governance workflow](governance-workflow.md#make-a-change) has the steps.

## Make it your own

The knowledge is yours to change:

- To add a concept, add a `node.md` under `knowledge/` with `status: proposed` and `origin: project`, name its parent in `broader`, and give some node a pointer to it.
- To give a domain node project values, such as your brand colors, add a workspace node that names it in `implements`.
- To add a rule, follow the grammar in [language checks](language-checks.md). If it opens with a verb the vocabulary doesn't approve, add the verb to `governance/language/vocabulary.yaml`, or to `governance/language/branches/<node-id>.yaml` if only one branch needs it.
- To remove a branch, delete its nodes, each reference to them, and any branch vocabulary named after them. The [graph checks](graph-checks.md) list what still points at a deleted node. An accepted entity goes through [deprecation first](governance-workflow.md#remove-something).

## Language terms

Two branches add terms in `governance/language/branches/`. `ui-ux-design.yaml` approves `design` as an opening verb and prohibits vague words such as `intuitive` and `clean`, which say how a screen should feel without saying what to do. `software-engineering.yaml` approves `revoke`.

## Sources

A `sources` value names a page that was read when the rule was written: the Web Content Accessibility Guidelines, Nielsen Norman Group articles, MDN, and the OWASP Secrets Management Cheat Sheet. A rule with no `sources` is a judgment call, so read it with more care.

## How it fits

This is the first real content for the [schema](schema.md), the [format](node-format.md), and the checks. The [compiled outputs](compiled-outputs.md) read it now, and the [runtime files](runtime-files.md) build from it next. While a seed directive is `proposed`, only `uv run ka build --proposals` holds it.

## What it does not check yet

- Whether a rule is right. The checks read form and structure, and a reviewer reads meaning.
- Whether a value in `sources` exists, says what the rule says, or still says it
- The definitions and the body text. The [language checks](language-checks.md) read only directives, triggers, and skill descriptions.
- A `conflicts_with` pair on real content. No seed directive declares one, because no two seed rules truly conflict.
