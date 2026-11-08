# Node format

> **In the library:** the scanner at the front desk. It reads one card at a time and rejects a badly filled one, with the line that is wrong. It does not know whether the books a card names exist.

**Status:** Built.

Each node is one Markdown file with YAML front matter. The parser in `engine/parser/` reads it into the models described in [Schema](schema.md).

## Where nodes live

Each node is a file with the name `node.md`, in its own folder. The root node is `knowledge/node.md`. Other knowledge nodes go under `knowledge/nodes/`, skills go under `knowledge/skills/`, and policies go under `knowledge/governance/policies/`.

No generated file sits beside a node. The [runtime files](runtime-files.md) go to `AGENTS.md` and `.claude/`, so a Markdown file with another name under `knowledge/` fails with `file-name`, even when it holds the generated marker.

The folder path is only for navigation. Identity and relationships come from `id` and the edges, so a file can move without changing what it means.

Any other Markdown file, and any symbolic link, in these folders is an error, so a misnamed node cannot escape the checks.

A skill folder can also hold a `scripts/` folder. The parser skips every file in it, whatever its name, so a script can be a Markdown file and still pass. The exemption covers only a skill's own `scripts/`. One beside any other node still fails `file-name`. A symbolic link in it still fails, and a file that git ignores, such as a cache, is left out. The [runtime files](runtime-files.md#skill-scripts) copy the folder next to the generated `SKILL.md`.

A flow skill folder also holds a `steps/` folder, described [below](#step-files).

The parser also skips `knowledge/evals/`, which holds the [eval tasks](evaluation.md#the-eval-tasks). The exemption covers only that folder. A folder named `evals` anywhere else is checked like any other.

## Example

```markdown
---
id: test-driven-development
kind: densho:Concept
title: Test-driven development
status: accepted
origin: template
knowledge_type: domain
broader: [software-testing]
pointers:
  - kind: densho:PathPointer
    target: pytest-usage
    trigger: You edit a test file.
    paths: ["tests/**"]
---

## Definition

Write a failing test first, then the code that passes it.

## Directives

- Write a failing test before you change behavior. ^write-test-first
  - scope: subtree
  - basis: practitioner
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

## Step files

A flow skill names its steps in `steps`, and each step gets a file at `steps/<step-id>.md` in the skill's folder:

```text
knowledge/skills/design-interface/
├── node.md
└── steps/
    ├── information-architecture.md
    ├── interaction-design.md
    ├── visual-design.md
    └── design-systems.md
```

A step file is plain Markdown with no front matter. It holds four sections in this order, and each one needs text:

| Section     | What it holds                                        |
| ----------- | ---------------------------------------------------- |
| `Inputs`    | What the step starts from                            |
| `Procedure` | The numbered actions of the step                     |
| `Output`    | What the step hands to the next step                 |
| `Exit gate` | What must hold before the flow goes to the next step |

A step with no procedure from a source says so in one line, `The procedure of this step is missing.`, and a partial one ends with `The rest of the procedure of this step is missing.` The file holds no directives. They stay in the nodes, and the [runtime files](runtime-files.md#flow-skills) put each one in the right file.

The parser reads each Markdown file in a skill's `steps/` folder as a step file and fails it with `step-file` if it sits in a subfolder, its name isn't a lowercase ID with `.md`, a section is missing, out of order, or empty, or text comes before the first section. It also fails a `## Definition` or a `## Directives` heading. The [graph checks](graph-checks.md#skills-and-steps) match the files to `steps`.

A step file needs no review, the same as the body of a node, and the history records a digest of the step files of each skill.

## Check your nodes

```sh
uv run densho parse knowledge
```

Each problem prints as `path:line: code: message`. The git hook runs the same command on each commit.

The parser reports every problem it can in a file. Three things stop it early: a control character, front matter it cannot read, and an unknown `kind`, which stops the field checks because the kind sets which fields apply.

## What the parser does not check

The parser checks each file on its own. It does not check that a reference such as `broader` names a node that exists. [Graph checks](graph-checks.md) do that, and they run only after every file parses.
