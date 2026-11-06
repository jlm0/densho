# Node format

> **In the library:** the scanner at the front desk. It reads one card at a time and rejects a badly filled one, with the line that is wrong. It does not know whether the books a card names exist.

**Status:** Built.

Each node is one Markdown file with YAML front matter. The parser in `engine/parser/` reads it into the models described in [Schema](schema.md).

## Where nodes live

Each node is a file with the name `node.md`, in its own folder. The root node is `knowledge/node.md`. Other knowledge nodes go under `knowledge/`, skills go under `skills/`, and policies go under `governance/policies/`.

A folder can also hold a generated `AGENTS.md`. The parser skips a Markdown file that holds the marker of a [generated file](runtime-files.md#hand-written-files), and any other Markdown file with another name fails with `file-name`.

The folder path is only for navigation. Identity and relationships come from `id` and the edges, so a file can move without changing what it means.

Any other Markdown file, and any symbolic link, in these folders is an error, so a misnamed node cannot escape the checks.

## Example

```markdown
---
id: test-driven-development
kind: ka:Concept
title: Test-driven development
status: accepted
origin: template
knowledge_type: domain
broader: [software-testing]
pointers:
  - kind: ka:PathPointer
    target: pytest-usage
    trigger: You edit a test file.
    paths: ["tests/**"]
---

## Definition

Write a failing test first, then the code that passes it.

## Directives

- Write a failing test before you change behavior. ^write-test-first
  - scope: subtree
  - status: accepted
  - origin: template
  - sources: https://example.com/testing

## References

Any other text is the body of the node.
```

## Front matter

The front matter holds every field except the definition, the directives, and the body, which live in the Markdown. It accepts plain YAML only: no tags, anchors, aliases, merge keys, or `...` lines. A file then has one reading, and each value has one source.

## Sections

The sections come in this order: `## Definition`, `## Directives`, then any other text, which becomes the body. Text after the directives needs its own heading, such as `## Notes`. A loose paragraph there fails, because it could be a directive that lost its bullet.

A line that looks like a section name but is not that exact top-level heading is an error, so a directive cannot turn into prose by accident. `## Directive`, `## **Directives**`, and `> ## Directives` all fail.

For the same reason, the parser rejects:

- an unclosed code fence
- a code fence that holds a section name the file does not otherwise have
- raw HTML blocks and HTML comments, because a reader of the rendered file cannot see them
- control characters, and a YAML escape such as `"\ud800"` that gives a character no file can hold
- Markdown nested deeper than a Markdown parser can read reliably

## Directives

Each directive is one bullet of one line that ends with a space and `^id`. The directive text is Markdown. Its other fields are sub-bullets, one `key: value` each. Repeat a key to add another value to a list field such as `sources`.

A value is plain text, so put one that holds Markdown syntax in backticks:

```markdown
- sources: `tests/**/x*`
```

`mdformat` runs on each commit and can escape characters. Metadata values keep their meaning through that. The source of the directive text can change, for example to `src/\*_test.py`, but it still renders the same.

## Check your nodes

```sh
uv run ka parse knowledge skills governance
```

Each problem prints as `path:line: code: message`. The git hook runs the same command on each commit.

The parser reports every problem it can in a file. Three things stop it early: a control character, front matter it cannot read, and an unknown `kind`, which stops the field checks because the kind sets which fields apply.

## What the parser does not check

The parser checks each file on its own. It does not check that a reference such as `broader` names a node that exists. [Graph checks](graph-checks.md) do that, and they run only after every file parses.
