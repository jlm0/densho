---
name: map-opportunities
description: "Map the needs of customers under a product outcome, and choose the target need and its solutions. Use when you map customer needs and solutions under a product outcome. Do not use it for assumption tests (`test-assumptions`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Map the opportunities of an outcome

## Run the skill

1. Run the steps in their order.
2. If the output of a step exists already, skip the step.
3. If a step has a step file, read the step file.
4. Follow each directive of the step.
5. If a branch heading matches the work, follow each directive under it.
6. If you need the definition or the notes of a page, read the page.
7. After each step, check its output against each directive of the step.
8. Before you start the next step, correct each part of the output that breaks a directive.

## 1. Map the opportunities

Step file: [steps/map-the-opportunities.md](steps/map-the-opportunities.md)

1. Collect the outcome of the team, with its direction and its target.
2. Collect the notes of `3` or more story-based customer interviews.
3. If the team has an opportunity solution tree, collect it.
4. If the outcome or the interview notes are missing, ask the person for them.
5. Put the outcome at the root of the tree.
6. Read each interview note.
7. Write each need, pain point, and desire that the story of the note shows.
8. Group the opportunities under the moments of the customer experience.
9. Order each branch from broad parent opportunities to narrow child opportunities.

Missing rule: No directive of product discovery states its inputs, such as the notes of the weekly customer interviews.

Output: The opportunity space of the tree: the outcome at the root, and the opportunities under it, each with its interview note.

## 2. Choose the target and its solutions

1. Compare the opportunities on size, market effect, fit with the strategy, and importance to customers.
2. Choose `1` target opportunity.
3. Generate solutions for the target opportunity.
4. Choose `3` solutions to compare.

Missing rule: No directive of product discovery states how to compare the opportunities when you choose the target.

Pages:

- You choose the target opportunity or its solutions. Read [Opportunity solution tree](../../references/opportunity-solution-tree.md).

Directives:

- Do not use effort to choose a target opportunity. ^no-effort-in-opportunity-choice
- Generate solutions for the target opportunity only, not across the whole tree. ^solutions-for-the-target
- Compare `3` solutions for the target opportunity before you choose one. ^compare-three-solutions

Output: The target opportunity, marked in the tree, with `3` solutions under it.

## Exit checklist

Check each line before you report the map as done.

- [ ] Steps `1` and `2` each have their output.
- [ ] The root of the tree holds `1` product outcome.
- [ ] Each opportunity names its interview note.
- [ ] Each solution sits under the target opportunity.
- [ ] The report names each directive that the tree misses, and each missing rule that the map reached.

## Output

- The opportunity solution tree as a nested list, from the outcome to the solutions, with the target opportunity marked
- A list of each directive that the tree misses, with the reason

To test the solutions, run `test-assumptions`.
