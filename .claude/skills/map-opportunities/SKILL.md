---
name: map-opportunities
description: "Map the customer needs, the solutions, and the assumption tests under one product outcome. Use when a team chooses the next customer need that it works on."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Map the opportunities of an outcome

If compaction cuts this skill, invoke the skill again.

## Directives

No directive is in force at this node.

## Inputs

- The outcome of the team, with its direction and its target
- The target customer and the value that the product offers them
- Notes from `3` or more story-based customer interviews
- The current tree, if the team has one

## Procedure

1. Read each directive that this skill lists.
2. Check the inputs. If the outcome or the interview notes are missing, stop and ask the person for them. Do not invent an opportunity.
3. Put the outcome at the root of the tree.
4. Read each interview note, and write each need, pain point, and desire that the story shows.
5. Group the opportunities under the moments of the customer experience. Order each branch from broad parent opportunities to narrow child opportunities.
6. Choose one target opportunity. Compare the candidates on their size, their effect on the market position, their fit with the company strategy, and their importance to customers.
7. Generate solutions for the target opportunity, and choose `3` of them to compare.
8. List the assumptions of each chosen solution across the desirability, viability, feasibility, usability, and ethical types.
9. Choose the riskiest assumptions. For each one, write a test and the result that counts as a pass.

## Output

The tree as a nested list, from the outcome to the assumption tests, with the target opportunity marked. Each opportunity names the interview it came from. A table of the assumption tests gives the assumption, its type, the test, and the result that counts as a pass.

## Validation

Check the tree against each directive from the first step of the procedure, and report each one it misses. Each opportunity traces to an interview note. Each solution sits under the target opportunity.

## References

- You list the assumptions of a solution or plan a test. Read [Assumption testing](../../references/assumption-testing.md).
- You read interview notes for the needs and the jobs of customers. Read [Jobs to be done](../../references/jobs-to-be-done.md).
- You place the outcome, an opportunity, or a solution in the tree. Read [Opportunity solution tree](../../references/opportunity-solution-tree.md).
- You sort the assumptions of a solution by the risk that they carry. Read [Four product risks](../../references/product-risks.md).
