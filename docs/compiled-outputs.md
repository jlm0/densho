# Compiled outputs

> **In the library:** the printed catalog. People keep working with the books, while tools read one complete listing, and a fingerprint shows whether two printings match.

**Status:** Planned. Nothing on this page exists yet.

## What it does

This layer will compile the Markdown source into JSON and RDF, each with a digest. The same source will always produce the same bytes, so a digest shows whether two builds hold the same knowledge.

## How it works

Markdown stays the format people edit. The build reads the nodes through the parser, writes its output to `build/`, and records a digest for it.

| Format | What it is for                                                            |
| ------ | ------------------------------------------------------------------------- |
| JSON   | A complete graph that any tool can read without parsing Markdown          |
| RDF    | The same graph in the SKOS standard for taxonomies, which tools can query |

## How it fits

This layer turns checked source into something other tools can consume. It needs [seed knowledge](seed-knowledge.md) to have real content to compile, and it comes before the [runtime files](runtime-files.md).

## Not settled yet

- Whether the repo commits the build output. Git ignores `build/` today.
