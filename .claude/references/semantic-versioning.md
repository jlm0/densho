<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Semantic versioning

## Directives

No directive is in force at this node.

## Definition

A version number of the form `MAJOR.MINOR.PATCH` that states how a release changes the public API. The major version counts incompatible changes, the minor version counts compatible additions, and the patch version counts compatible bug fixes. Major version `0` is for initial development, and its public API is not stable. The specification is Semantic Versioning `2.0.0`.

## Notes

An increment of the major version resets the minor and the patch versions to `0`. An increment of the minor version resets the patch version to `0`. If a minor release breaks compatibility by mistake, release a new minor version that restores compatibility, and leave the faulty release as it is.

## Comes from

The output of each node in this list is an input of this node.

- [Build pipeline](build-pipeline.md)
