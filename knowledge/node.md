---
id: root
kind: densho:Root
title: Densho
status: proposed
origin: template
pointers:
  - kind: densho:TextPointer
    target: digital-product-development
    trigger: You plan, design, or build a digital product.
  - kind: densho:PathPointer
    target: governance
    trigger: You change a node file.
    paths:
      - knowledge/**/*
  - kind: densho:SkillPointer
    target: plan-product-strategy
    trigger: You decide what a product does, who it is for, or what a team builds next.
  - kind: densho:SkillPointer
    target: research-users
    trigger: You study the people who use a product.
  - kind: densho:SkillPointer
    target: design-brand
    trigger: You define or change the strategy, the voice, the visual identity, or the guidelines of a brand.
  - kind: densho:SkillPointer
    target: design-content
    trigger: You plan or write the content of a product.
  - kind: densho:SkillPointer
    target: design-interface
    trigger: You create or change a user interface.
  - kind: densho:SkillPointer
    target: engineer-software
    trigger: You write, test, or release software.
  - kind: densho:SkillPointer
    target: review-interface
    trigger: A screen or a flow is ready for review.
  - kind: densho:SkillPointer
    target: review-screen-hierarchy
    trigger: A person asks for a review of the hierarchy of a screen.
  - kind: densho:SkillPointer
    target: review-usability
    trigger: A person asks for a usability review of a flow.
  - kind: densho:SkillPointer
    target: audit-accessibility
    trigger: A person asks for an accessibility check of an interface.
  - kind: densho:SkillPointer
    target: audit-brand-consistency
    trigger: You review the touchpoints of a brand for consistency.
  - kind: densho:SkillPointer
    target: review-code-change
    trigger: A code change is ready for review.
use_a_skill:
  - run-triggered-skill
  - follow-triggered-skill
  - read-skill-after-compaction
create_a_rule:
  - propose-corrections
  - propose-stated-rules
  - follow-stated-rule-in-session
  - keep-personal-preferences
  - start-as-proposed
  - proposed-is-a-draft
  - person-accepts
  - one-action-per-directive
  - define-each-other-case
  - follow-the-grammar
  - new-rules-in-workspace
  - task-rules-on-root
  - report-template-candidates
  - reopen-a-directive
---

## Directives

- When a person corrects your work, propose the change with `propose-knowledge`. ^propose-corrections
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If your task matches an activity in the skill table, run the skill of that row first. ^run-triggered-skill
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Follow each procedure step of a skill that you run, and each directive that the skill tells you to follow. ^follow-triggered-skill
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- After a compaction, read the step file of your current step again, and each page that it names. ^read-skill-after-compaction
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- When a person states a new rule, propose it with `propose-knowledge`. ^propose-stated-rules
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If a person states a rule in a session, follow the rule for the rest of that session. ^follow-stated-rule-in-session
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- In a project, put each new directive in workspace knowledge, unless the directive covers each task in the project. ^new-rules-in-workspace
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If a new directive covers each task in the project, put it on the root with `scope: node`. ^task-rules-on-root
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- If an accepted workspace directive names nothing that only this project has, tell the person to run `sync-template`. ^report-template-candidates
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template

## Architecture

- A pointer or an edge carries meaning. A folder path only helps navigation, so a file can move and keep its meaning.
- Domain knowledge is universal. Workspace knowledge belongs to one project. One schema, one set of checks, and one workflow cover both.
- An agent can propose a node, a directive, or an exception. Only a person accepts one.
- The governance rules are nodes too. They follow their own rules, and the same checks read them.
- A project owns its copy of this graph, and its copy can differ from the template.
