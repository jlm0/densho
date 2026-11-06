<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Service level objective

## Directives

No directive is in force at this node.

## Definition

A target value or range for a service level indicator (SLI). An SLI is a measure of one aspect of the service that users get, such as latency, the error rate, or availability. A service level agreement (SLA) is a contract that adds a consequence, such as a refund, when the service misses its SLO. A target with no consequence is an SLO, not an SLA.

## Notes

A mean hides the slow tail of a latency distribution. The `99th` percentile shows a likely worst case, and the `50th` percentile shows the typical case. Start with a loose target and tighten it over time, not with a strict target that you relax later.
