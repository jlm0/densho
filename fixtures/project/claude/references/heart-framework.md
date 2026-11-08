<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# HEART framework

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Product strategy](product-strategy.md):

- State the user problem of each feature in one sentence. ^state-user-problem
- Write the success measure of each feature before you build the feature. ^write-success-measure

From [Product measurement](product-measurement.md):

- Link each metric to the goal that it tracks. ^metric-tracks-a-goal
- Normalize each raw count to a ratio, a percentage, or an average for each user, unless it counts new users. ^prefer-normalized-metrics

From [HEART framework](heart-framework.md):

- State for each HEART category whether the product uses it. ^choose-heart-categories
- Report each engagement metric as an average for each user, not as a total. ^engagement-per-user
- Write the goal of each HEART category before its signals and its metrics. ^goal-before-metric
- Choose signals that change only when the user experience changes. ^specific-signals

## Definition

Five categories of user-centered metrics from Kerry Rodden, Hilary Hutchinson, and Xin Fu at Google, published at CHI 2010. Happiness covers attitudes such as satisfaction and perceived ease of use. Engagement is the level of involvement, such as visits per user per week. Adoption counts the new users in a period. Retention counts the users of one period who still use the product in a later period. Task success covers efficiency, effectiveness, and the error rate. The Goals-Signals-Metrics process states the goals first, then the signals in behavior or attitude that show success, then the metrics to track. HEART adds to the PULSE metrics of product health: page views, uptime, latency, seven-day active users, and earnings.

## Notes

Not every category fits every product. Engagement can mean little in an enterprise tool that people must use for work, while it still matters for one feature. The goals of a feature can differ from the goals of the whole product. Logs and surveys are the usual sources of signals, and failure is sometimes easier to see than success, for example in abandoned tasks or "undo" events.

Gmail measured engagement as the share of active users who visited on five or more days in the last week, and found that it predicted long-term retention.

## Comes from

The output of each node in this list is an input of this node.

- [Objectives and key results](objectives-and-key-results.md)
