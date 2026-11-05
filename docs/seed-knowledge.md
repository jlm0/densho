# Seed knowledge

> **In the library:** the first real books. Until they arrive, every check has only ever run on test samples.

**Status:** Planned. Nothing on this page exists yet. `knowledge/` holds only the root node, and `skills/` is empty.

## What it does

This layer will add the first domain, with its concepts and directives, as real nodes that pass every check. A project that copies the template receives this knowledge.

## How it works

The nodes will follow the taxonomy from domain to discipline to practice area to concept. Branch depth can vary, because the hierarchy expresses real classification and does not force every branch to the same number of levels. Directives can attach at any of those levels.

Each knowledge node here carries `knowledge_type: domain` and `origin: template`, and it starts as `proposed` like everything new. A project adds its own knowledge next to it with `knowledge_type: workspace` and `origin: project`.

## How it fits

This is the first test of the [schema](schema.md), the [format](node-format.md), and the checks on real content. The [compiled outputs](compiled-outputs.md) and [runtime files](runtime-files.md) then have something to build from.

## Not settled yet

- Which domain comes first
- Which skills the template ships as its preset
