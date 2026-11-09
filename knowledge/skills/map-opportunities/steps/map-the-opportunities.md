---
title: Map the opportunities
pages:
  - target: opportunity-solution-tree
    trigger: You place the outcome, an opportunity, or a solution in the tree.
  - target: jobs-to-be-done
    trigger: You describe the progress that customers seek from a product.
  - target: research-synthesis
    trigger: You turn the notes of an interview into needs, pain points, and desires.
directives:
  - one-outcome-at-the-root
  - product-outcome-at-root
  - opportunity-is-a-need
  - solution-in-disguise
  - opportunities-from-interviews
  - job-dimensions
  - job-competitors
branches:
  - condition: If you write the questions of a customer interview
    directives:
      - ask-for-the-story
missing_rules:
  - No directive of product discovery states its inputs, such as the notes of the weekly customer interviews.
---

## Procedure

1. Collect the outcome of the team, with its direction and its target.
2. Collect the notes of `3` or more story-based customer interviews.
3. If the team has an opportunity solution tree, collect it.
4. If the outcome or the interview notes are missing, ask the person for them.
5. Put the outcome at the root of the tree.
6. Read each interview note.
7. Write each need, pain point, and desire that the story of the note shows.
8. Group the opportunities under the moments of the customer experience.
9. Order each branch from broad parent opportunities to narrow child opportunities.

## Output

The opportunity space of the tree: the outcome at the root, and the opportunities under it, each with its interview note.
