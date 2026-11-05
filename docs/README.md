# Overview

Agent instructions usually live in long prose files that repeat themselves, are hard to apply consistently, and get no automated checks. Governed knowledge treats that material like code. Each piece of knowledge is a small file with a stable ID and a declared place in a graph, and each rule is one short sentence in a restricted grammar. Automated checks refuse anything that breaks the structure, language, or change rules, and the rules for writing rules pass those same checks.

The goal is one source of truth that people can read and review, that agents load piece by piece as a task needs it, and that any project can copy and make its own. It can't make a model obey, but it does control what the agent can find and how it finds it.

## The library

Think of the system as a library, where each node is a book. The first two layers define and read one book. The next four make the library trustworthy, one stocks it, and the rest deliver it to agents, projects, and people.

| Layer                                                           | In the library                                | Status  |
| --------------------------------------------------------------- | --------------------------------------------- | ------- |
| [Schema](schema.md)                                             | The design of the catalog card                | Built   |
| [Node format](node-format.md)                                   | The scanner that rejects a badly filled card  | Built   |
| [Graph checks](graph-checks.md)                                 | The walk through the whole building           | Built   |
| [Language checks](language-checks.md)                           | The copy editor                               | Built   |
| [Directive semantics](directive-semantics.md)                   | The rules about which signs cover which rooms | Built   |
| [Governance workflow](governance-workflow.md)                   | The acquisitions policy                       | Built   |
| [Seed knowledge](seed-knowledge.md)                             | The first real books                          | Built   |
| [Compiled outputs](compiled-outputs.md)                         | The printed catalog                           | Built   |
| [Runtime files](runtime-files.md)                               | The signs that lead visitors to the shelf     | Planned |
| [Template packaging](template-packaging.md)                     | The library in a box                          | Planned |
| [Migration and reconciliation](migration-and-reconciliation.md) | The moving crew                               | Planned |
| [Human interface](human-interface.md)                           | The reading room                              | Planned |

A `Built` page explains how to use what exists today. A `Planned` page describes what a layer will do. Unless the page says otherwise, nothing on it exists yet.

## Terms

| Term      | In the library                                  | What it is                                                 |
| --------- | ----------------------------------------------- | ---------------------------------------------------------- |
| Node      | A book                                          | One Markdown file of knowledge                             |
| Pointer   | A "see also" note that says when to go there    | A route to another node, with the trigger for following it |
| Directive | A sign with one house rule                      | One short instruction with its own ID                      |
| Skill     | A reading list for one job                      | A reusable capability that draws on any branch             |
| Agent     | A visitor who goes only where the signs lead it | The AI tool that does the work                             |
