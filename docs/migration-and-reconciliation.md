# Migration and reconciliation

> **In the library:** the moving crew. It catalogs a collection that already exists into the system, and it later brings new arrivals from the original library to a branch that has gone its own way.

**Status:** Planned. Nothing on this page exists yet.

## What it does

This layer will add a company-level skill with two jobs:

- **Migration** converts the knowledge of an existing project into this architecture.
- **Reconciliation** pulls template changes into a project that has drifted.

## How it works

Migration is how a real project adopts the system: its existing rules and docs become nodes that pass the checks. Reconciliation reads the template's change history and uses stable IDs to find each node, even if the project moved its file, which a [plain pull](template-packaging.md#a-node-that-you-moved-or-deleted) can't do. The project decides what to pull, and a pulled change goes through the project's own [governance workflow](governance-workflow.md).

## How it fits

This skill depends on the [template packaging](template-packaging.md) for the change history in `.ka/history.jsonl`, the template commit in `.copier-answers.yml`, and the list of differences from `ka history --drift`.

## Not settled yet

- Where the skill lives
- How reconciliation helps with a node that a project and the template both changed. Today, [a pull](template-packaging.md#a-node-that-both-sides-changed) leaves conflict markers for a person to resolve.
