---
name: map-opportunities
description: "Map the customer needs, the solutions, and the assumption tests under one product outcome. Use when a team chooses the next customer need that it works on."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Map the opportunities of an outcome

If compaction cuts this skill, invoke the skill again.

## Directives

From [Digital product development](../../references/digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Product strategy](../../references/product-strategy.md):

- State the user problem of each feature in one sentence. ^state-user-problem
- Write the success measure of each feature before you build the feature. ^write-success-measure

From [Jobs to be done](../../references/jobs-to-be-done.md):

- In a jobs interview, ask for the story of a real decision, not for the reason behind it. ^ask-for-the-story
- List each solution that people use for a job as a competitor, not only similar products. ^job-competitors
- Describe the functional, social, and emotional sides of each job. ^job-dimensions

From [Assumption testing](../../references/assumption-testing.md):

- State each assumption as a condition for the success of the idea. ^assumption-as-condition
- Define the result that counts as a pass before you run an assumption test. ^define-the-pass-first
- List the desirability, viability, feasibility, usability, and ethical assumptions of each idea before the team builds it. ^list-assumptions-by-type
- Do not choose a solution from the result of one assumption test. ^no-choice-from-one-test
- Test one assumption in each assumption test, not the whole idea. ^one-assumption-per-test
- Start with the assumptions that the idea depends on most and that have the least evidence. ^riskiest-assumptions-first

From [Opportunity solution tree](../../references/opportunity-solution-tree.md):

- Compare `3` solutions for the target opportunity before you choose one. ^compare-three-solutions
- Do not use effort to choose a target opportunity. ^no-effort-in-opportunity-choice
- Give each opportunity solution tree one outcome at its root. ^one-outcome-at-the-root
- Set one outcome for each product team. ^one-outcome-per-team
- Take each opportunity from a customer interview, not from the ideas of the team. ^opportunities-from-interviews
- Write each opportunity as a need, a pain point, or a desire of the customer. ^opportunity-is-a-need
- Put a product outcome at the root of each tree, not a business outcome or a traction metric. ^prefer-a-product-outcome
- If an opportunity has only one possible solution, replace it with the need behind that solution. ^solution-in-disguise
- Generate solutions for the target opportunity only, not across the whole tree. ^solutions-for-the-target

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
