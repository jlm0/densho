<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test pyramid

## Directives

No directive is in force at this node.

## Definition

A model for the mix of automated tests in a suite. Unit tests form the wide base. Service tests, which act through an API or a service layer, form the middle. Tests through the user interface form the narrow top. A test higher in the pyramid covers more of the system, runs slower, and breaks more often for reasons that are not a fault.

## Notes

Software Engineering at Google gives a rough mix of `80%` unit tests, `15%` integration tests, and `5%` end-to-end tests, by count. The mix of each team varies.
