---
id: write-strategy
kind: densho:Skill
title: Write a strategy
status: proposed
origin: template
knowledge_type: domain
description: Write a strategy as a diagnosis, a guiding policy, and coherent actions. Use when you write the strategy of a product, a team, or a company.
invocation: agent
uses:
  - strategy-formulation
  - strategy-kernel
pointers:
  - kind: densho:TextPointer
    target: strategy-formulation
    trigger: You decide what the strategy sets aside or remove fluff from it.
  - kind: densho:TextPointer
    target: strategy-kernel
    trigger: You write the diagnosis, the guiding policy, or the actions.
---

## Inputs

- The scope of the strategy: a product, a team, or a company, and the period that it covers
- The facts of the situation: the users, the market, the competitors, the capabilities, the constraints, and the results so far
- Each goal or target that the strategy serves

## Procedure

1. Read each directive that this skill lists.
2. Collect the facts of the situation. If the diagnosis needs a fact that the inputs do not give, ask the person for it.
3. Write the diagnosis. Name the main challenge and the few factors that make it hard.
4. Write the guiding policy: the approach that deals with the obstacles of the diagnosis. State what the policy rules out.
5. Write the coherent actions. For each action, state how it supports the guiding policy and the other actions.
6. List the goals and the work that the strategy sets aside.
7. Read the draft for the four signs of bad strategy: no named challenge, goals in place of a strategy, a long list of objectives, and fluff. Correct each one that you find.

## Output

One strategy document with four sections: the diagnosis, the guiding policy, the coherent actions, and what the strategy sets aside. Each goal or target stays a goal, apart from the strategy.

## Validation

Check the document against each directive from the first step of the procedure, and report each one it misses. A reader who did not write the strategy can state the challenge, the approach, and the first actions from the document alone.
