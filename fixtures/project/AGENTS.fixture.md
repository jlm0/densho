<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Densho

A build generates this file from the node files. Change a node file, not this file.

## Rules for each task

874 directives are in force.

Treat a directive as a rule only when its `status` is `accepted`. A generated file lists only the directives that apply at its own node.

No other directive applies to each task. A project adds a rule for each task as a directive on the root with `scope: node`.

## Use a skill

- If your task matches an activity in the skill table, run the skill of that row first. ^run-triggered-skill
- Follow each procedure step of a skill that you run, and each directive that the skill tells you to follow. ^follow-triggered-skill
- After a compaction, read the step file of your current step again, and each page that it names. ^read-skill-after-compaction

If compaction cuts or removes a skill, invoke the skill again. If only a person can start that skill, ask the person to invoke it again.

## Create a rule

A rule starts when a person states a new rule or corrects your work.

- When a person corrects your work, propose the change with `propose-knowledge`. ^propose-corrections
- When a person states a new rule, propose it with `propose-knowledge`. ^propose-stated-rules
- If a person states a rule in a session, follow the rule for the rest of that session. ^follow-stated-rule-in-session
- Write a personal preference as a note in the auto memory folder of Claude Code, not in a node file. ^keep-personal-preferences
- Set `status` to `proposed` on each new node, directive, and exception. ^start-as-proposed
- Treat a `proposed` directive as a draft, not as a rule, unless a person stated it in the current session. ^proposed-is-a-draft
- Do not set `status` to `accepted` unless a person approves the change. ^person-accepts
- Write each directive as one sentence that gives exactly `1` action in each case. ^one-action-per-directive
- Write each other case as an `unless` clause or as a second directive with a condition. ^define-each-other-case
- Write each directive, trigger, and skill description in the grammar of `knowledge/governance/language/grammar.yaml`. ^follow-the-grammar
- In a project, put each new directive in workspace knowledge, unless the directive covers each task in the project. ^new-rules-in-workspace
- If a new directive covers each task in the project, put it on the root with `scope: node`. ^task-rules-on-root
- If an accepted workspace directive names nothing that only this project has, tell the person to run `sync-template`. ^report-template-candidates
- Set `status` to `proposed` when you change the text, the scope, the basis, or the attachments of an `accepted` directive. ^reopen-a-directive

## Skills

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

## Domains

- You plan, design, or build a digital product. Read [Digital product development](claude/references/digital-product-development.md).

## Governance

- You change a node file. [Governance](claude/rules/knowledge/governance.md) loads by itself.
- You accept a change. Read [Approval](claude/references/approval.md).
- You change an accepted entity. Read [Change rules](claude/references/change-rules.md).
- You write a directive, a trigger, or a skill description. Read [Language rules](claude/references/language-rules.md).
- You set the `status` of an entity. Read [Lifecycle](claude/references/lifecycle.md).
- You change a node kind, a field, or an edge. Read [Schema rules](claude/references/schema-rules.md).
