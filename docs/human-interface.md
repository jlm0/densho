# Human interface

> **In the library:** the reading room, where people browse and review the same books the visitors use.

**Status:** Built.

This layer gives a person two commands. `ka view` writes a site that shows the tree, what applies at each node, and everything that waits for review. `ka accept` changes `status` to `accepted` on what the person approves. The code is in `engine/knowledge_architecture/interface/`.

Nothing here is a new source of knowledge. The site reads the same compiled graph as the [runtime files](runtime-files.md), so a person and an agent see one version of each node. A node is still a Markdown file that any editor can open and Git can review.

## Read the knowledge

```sh
uv run ka view
```

```text
Open build/view/index.html in a browser.
27 pages, 27 written, 0 removed, 0 problems
```

The command runs every check, then writes one static site to `build/view/`, which git ignores. Open `index.html` from disk. The site needs no server and no network, runs no script, and holds no absolute path, so a copy in another folder has the same bytes.

| Page              | What it shows                                                                                                                                                                    |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `index.html`      | What is in force, how much waits for review, the tree that `broader` makes, and the skills                                                                                       |
| `review.html`     | Each `proposed` entity grouped by node, in tree order, so that you can read a whole branch at once                                                                               |
| `nodes/<id>.html` | The definition and status of one node, what applies there and the route that gave it, its directives, exceptions, pointers with their triggers, edges, body, and generated files |

A node page keeps directives apart by state. `In force` holds what binds an agent today. `In force only after acceptance` holds what a proposal would add, and `Stopped here after acceptance` names what a proposed exception would stop.

The site draws no graph picture. The tree shows `broader`, and `related`, `informs`, and the other edges appear as links on each node page. To change a node, use an editor, and the git hook checks the result.

A node with two parents appears twice in the tree. The second row links to the node and says that it is listed above. A rejected tree removes the old pages, so you can't read a site that no longer matches a valid tree by accident.

## Accept what you approve

The site only reads. To accept something, run a command in a terminal:

1. Run `uv run ka view`, then read `build/view/review.html`.
2. Run `uv run ka accept` with the names you approve. Each group in the queue prints the command.
3. Read `git diff`. It changes one word on each status line.
4. Run `uv run ka runtime`, because an accepted directive now reaches the generated files.
5. Stage the files and commit them. The command writes no commit.

```sh
uv run ka accept visual-grouping group-related-fields
uv run ka accept --subtree visual-design --dry-run
```

```text
knowledge/.../visual-grouping/node.md:5: node visual-grouping is now accepted
knowledge/.../visual-grouping/node.md:32: directive group-related-fields is now accepted
This command wrote no commit. Read git diff, run uv run ka runtime, stage the files, and commit them.
2 entities accepted, 0 not proposed, 0 problems
```

| What to accept                                  | The name                   |
| ----------------------------------------------- | -------------------------- |
| One node, without its directives                | `<node-id>`                |
| One directive                                   | `<directive-id>`           |
| One exception                                   | `<node-id>:<directive-id>` |
| A node, everything under it, and what they hold | `--subtree <node-id>`      |

`--subtree` follows `broader`. It doesn't follow `uses`, so a skill is outside each branch and only the subtree of the root reaches it. You can repeat the option and mix it with names.

`--dry-run` runs every check and lists what the command would accept, and it writes nothing.

An entity that isn't `proposed` is left alone and counted in the summary. A subtree skips each one. A `deprecated` entity that you name fails with `not-proposed`, because the [workflow](governance-workflow.md) doesn't allow that jump.

The command writes nothing unless the whole request can pass:

- The tree passes every check before the change, and the directive checks and the size and link checks of the [runtime files](runtime-files.md#codes) pass on the result.
- The last commit holds each entity, with the same reviewed fields. A reviewer approves the text that the last commit holds, so a change in the working tree has to go in its own commit first. A change to a field that needs no review, such as `title`, can stay.
- Each change is the status word and nothing else. A line ending, a quote, a comment, and a missing last line ending stay as they were.

It writes no runtime file, and it doesn't stage anything.

## Who runs it

A person runs this command. No check proves who ran it.

The root of the graph says that an agent can propose a node, a directive, or an exception, and that only a person accepts one. The command can't tell a person from an agent, because both run the same process on the same files. The rule rests on the people in a project, and on a reviewer who reads `git log -p`. [What a check can and cannot prove](governance-workflow.md#what-a-check-can-and-cannot-prove) covers the rest.

There is no button in the site, on purpose. A page that writes would need a server, and it would make acceptance easier to do without reading.

## In a project

A project runs the same commands through `.ka/ka`, and needs no Python:

```sh
.ka/ka view
.ka/ka accept --subtree visual-design
.ka/ka runtime
```

The review queue and the next-step line name the command that fits the folder. They use `.ka/ka` if the file exists, and `uv run ka` if it doesn't.

A project gets these commands at install, or at its next [template pull](template-packaging.md#pull-a-template-change) if it installed earlier. A `.gitignore` of your own needs `build/`, or the site shows up as untracked files.

## Text in a node is not trusted

A node can arrive from a pull or from an agent, so the site treats each value as hostile:

- Jinja escapes every value. Only Markdown output, the marker, and the style sheet skip that step.
- Markdown runs with raw HTML turned off, so a `<script>` shows up as text.
- A link must start with `http:`, `https:`, or `mailto:`. Anything else, including a relative path and a scheme with a hidden tab such as `java&#9;script:`, stays as its source text.
- An image stays as text, so a page can't send a request to another host.
- Each page sets a content security policy that allows only its own style block, so a script can't run even if an escape fails.

## Codes

| Code            | What it reports                                                                                          |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| `unknown-id`    | `ka accept`: no entity has this name, or no node has this ID in `--subtree`                              |
| `not-proposed`  | `ka accept`: you named a `deprecated` entity, or the last commit holds it as `deprecated`                |
| `uncommitted`   | `ka accept`: the last commit doesn't hold the entity, or a field that needs review differs from it       |
| `no-history`    | `ka accept`: there is no last commit to compare with, or a merge is in progress                          |
| `status-line`   | `ka accept`: the command can't change this status alone, for example on a line that holds a similar word |
| `not-generated` | `ka view`: a path under `build/view/` holds a file without the marker, a folder, or a symbolic link      |
| `write`         | Either command: a file or a permission blocks a write. `ka accept` reports only what it did write        |

`ka view` also reports every code from the checks it runs, and so does `ka accept`. Exit status 1 means a problem, and exit status 2 means that `ka accept` got no name.

## Use it from code

```python
from pathlib import Path

from knowledge_architecture.interface import accept_entities, render_site, write_view

write_view(Path())
accept_entities(Path(), ["group-related-fields"], ["visual-design"], dry_run=True)
```

`render_site` takes parsed nodes and returns each page as bytes, and it writes nothing. `write_view` runs the checks first.

## What it does not check yet

- Whether the site you read is current. A page holds what the node files held when `ka view` last ran. `ka accept` reads the tree, not the page, so a command you copy from an old page can accept text you haven't read.
- That a person read anything before running `ka accept`.
- A failure partway through a write. The command changes each file in turn, so a disk or permission failure can leave some files changed. It stops at the first failure and lists what changed, and `git diff` shows the same.
