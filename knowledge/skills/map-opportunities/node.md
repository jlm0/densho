---
id: map-opportunities
kind: densho:Skill
title: Map the opportunities of an outcome
status: proposed
origin: template
knowledge_type: domain
description: Map the customer needs, the solutions, and the assumption tests under one product outcome. Use when a team chooses the next customer need that it works on.
invocation: agent
uses:
  - opportunity-solution-tree
  - jobs-to-be-done
  - assumption-testing
  - product-risks
pointers:
  - kind: densho:TextPointer
    target: opportunity-solution-tree
    trigger: You place the outcome, an opportunity, or a solution in the tree.
  - kind: densho:TextPointer
    target: jobs-to-be-done
    trigger: You read interview notes for the needs and the jobs of customers.
  - kind: densho:TextPointer
    target: assumption-testing
    trigger: You list the assumptions of a solution or plan a test.
  - kind: densho:TextPointer
    target: product-risks
    trigger: You sort the assumptions of a solution by the risk that they carry.
---

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
