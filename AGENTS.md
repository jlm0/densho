<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Densho

A build generates this file from the node files. Change a node file, not this file.

## Directives

No directive is in force. The graph holds 854 directives that are not in force.

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

Each row names an activity and the skill for it.

| Activity | Skill |
| --- | --- |
| A person asks for an accessibility check of an interface. | `audit-accessibility` |
| You review the touchpoints of a brand for consistency. | `audit-brand-consistency` |
| You define or change the strategy, the voice, the visual identity, or the guidelines of a brand. | `design-brand` |
| You plan or write the content of a product. | `design-content` |
| You create or change a user interface. | `design-interface` |
| You write, test, or release software. | `engineer-software` |
| You decide what a product does, who it is for, or what a team builds next. | `plan-product-strategy` |
| You study the people who use a product. | `research-users` |
| A code change is ready for review. | `review-code-change` |
| A screen or a flow is ready for review. | `review-interface` |
| A person asks for a review of the hierarchy of a screen. | `review-screen-hierarchy` |
| A person asks for a usability review of a flow. | `review-usability` |

These skills have no row:

- `evaluate-knowledge`: Run the eval tasks of a discipline with and without its directives, and propose deprecations. Use when a person asks whether the directives of a discipline help. Only a person can start this skill.
- `propose-knowledge`: Convert a correction or a repeated note into one small knowledge proposal. Use when a person corrects your work.
- `review-proposals`: Show the knowledge proposals branch by branch, with the effect and the conflicts of each one. Use when a person reviews the proposals. Only a person can start this skill.
- `sync-template`: Pull template changes into this project, or prepare a workspace rule for the template. Use when a person asks for a template pull or an upstream proposal. Only a person can start this skill.
