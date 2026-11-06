<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Knowledge architecture

A build generates this file from the node files. Change a node file, not this file.

## Directives

No directive is in force. The graph holds 81 directives and 1 exception that are not in force.

Treat a directive as a rule only when its `status` is `accepted`. A generated file lists only the directives that apply at its own node.

## Architecture

- A pointer or an edge carries meaning. A folder path only helps navigation, so a file can move and keep its meaning.
- Domain knowledge is universal. Workspace knowledge belongs to one project. One schema, one set of checks, and one workflow cover both.
- An agent can propose a node, a directive, or an exception. Only a person accepts one.
- The governance rules are nodes too. They follow their own rules, and the same checks read them.
- A project owns its copy of this graph, and its copy can differ from the template.

## Domains

- You plan, design, or build a digital product. Read [Digital product development](.claude/references/digital-product-development.md).

## Governance

- You change a node file. [Governance](.claude/rules/knowledge/governance.md) loads by itself.
- You accept a change. Read [Approval](.claude/references/approval.md).
- You change an accepted entity. Read [Change rules](.claude/references/change-rules.md).
- You write a directive, a trigger, or a skill description. Read [Language rules](.claude/references/language-rules.md).
- You set the `status` of an entity. Read [Lifecycle](.claude/references/lifecycle.md).
- You change a node kind, a field, or an edge. Read [Schema rules](.claude/references/schema-rules.md).

## Skills

If compaction removes a skill, invoke the skill again.

- `design-settings-interface`: Design a settings interface from its options and its users. Use when you design or change a settings screen.
- `review-screen-hierarchy`: Review a screen for its hierarchy, its grouping, and its use of prose. Use when a screen design is ready for review.
