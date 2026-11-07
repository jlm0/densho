<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Expand and contract

## Directives

No directive is in force at this node.

## Definition

A way to make a breaking change to an interface in 3 phases. Martin Fowler also calls it parallel change. In the expand phase, the interface supports both the old and the new version. In the migrate phase, each client moves to the new version. In the contract phase, the old version is removed. Many database refactorings follow the same pattern.

## Comes from

The output of each node in this list is an input of this node.

- [Data modeling](data-modeling.md)
