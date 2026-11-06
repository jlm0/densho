<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Knowledge architecture

A build generates this file from the node files. Change a node file, not this file.

## Directives

No directive is in force. The graph holds 425 directives and 1 exception that are not in force.

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

- `audit-accessibility`: Check an interface against the WCAG `2.2` success criteria of level A and AA. Use when a screen, a component, or a flow needs an accessibility check.
- `define-success-metrics`: Define the goals, the signals, and the metrics of a product or a feature. Use when you decide how to measure the success of a product or a feature.
- `design-settings-interface`: Design a settings interface from its options and its users. Use when you design or change a settings screen.
- `map-opportunities`: Map the customer needs, the solutions, and the assumption tests under one product outcome. Use when a team chooses the next customer need that it works on.
- `prioritize-work`: Order a backlog or a roadmap with RICE, cost of delay, MoSCoW, or the Kano model. Use when you set the order of the work of a team.
- `review-code-change`: Review a code change for its design, its behavior, its tests, and its security. Use when a change is ready for review.
- `review-screen-hierarchy`: Review a screen for its hierarchy, its grouping, and its use of prose. Use when a screen design is ready for review.
- `review-usability`: Review a flow against the usability heuristics, the size and position of its targets, and its choices. Use when a flow is ready for a usability review.
- `write-decision-record`: Write an architecture decision record for one decision. Use when you make or change a decision about the structure of a system.
- `write-positioning`: Write the positioning of a product from its alternatives, unique attributes, value, target customers, and market category. Use when you write or change the positioning of a product.
- `write-strategy`: Write a strategy as a diagnosis, a guiding policy, and coherent actions. Use when you write the strategy of a product, a team, or a company.
