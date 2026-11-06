<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Error budget

## Directives

No directive is in force at this node.

## Definition

The amount of unreliability that a service can have in a period and still meet its SLO. The budget is `100%` minus the SLO. An SLO of `99.9%` gives a budget of `0.1%` of requests in the window. While budget remains, a team releases changes. When the budget is spent, the team stops releases and puts its work into reliability.

## Notes

The policy names the actions when the budget is spent, who takes them, and the escalation path for a disagreement. Product, development, and the team that runs production approve it. The freeze ends when the service is back within its SLO.
