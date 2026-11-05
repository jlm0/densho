# Template packaging

> **In the library:** the library in a box. A new town gets a full copy, runs it as its own from then on, and can read what changed at the original.

**Status:** Planned. Nothing on this page exists yet. Today you start a project by copying the repo.

## What it does

This layer will install the template into a new project, record which template commit the project started from, and keep a change history that agents can read.

## How it works

A project receives one copy, and from then on it owns that copy. It can change and grow anything it received, so drift from the template is expected. Nothing pins a project to a template version, and nothing forces it to pull a change.

Two fields support that. A stable `id` lets the change history name a node after a project moves its file, and `origin` tells template knowledge apart from project knowledge.

## How it fits

This layer takes the checked knowledge, the checks, and the [runtime files](runtime-files.md) to other projects. The [migration and reconciliation skill](migration-and-reconciliation.md) uses the change history that it records.

## Not settled yet

- The tool that installs the template and records its commit
- How the engine reaches a project
- How an install into a repo with history brings its knowledge in as `proposed`, as the [governance workflow](governance-workflow.md#knowledge-from-the-template) requires
