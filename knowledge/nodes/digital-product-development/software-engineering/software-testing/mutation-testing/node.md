---
id: mutation-testing
kind: densho:Concept
title: Mutation testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf
  - https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf
  - https://arxiv.org/pdf/2102.11378
  - https://homes.cs.washington.edu/~rjust/publ/practical_mutation_testing_tse_2021.pdf
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=130
broader:
  - software-testing
related:
  - code-coverage
---

## Definition

A fault-based technique that measures how well a test set detects faults. Jia and Harman describe the process: small syntactic changes seed faults into the program, and each changed copy is a mutant. A test set kills a mutant when a test gives a different result on the mutant than on the original program. The mutation score is the ratio of killed mutants to the mutants that are not equivalent to the original. Petrović and colleagues at Google separate mutation analysis, which measures a test suite, from mutation testing, which uses each surviving mutant as the goal of a new test.

## Directives

- Make each mutant with `1` small syntactic change to the program. ^one-change-per-mutant
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf#page=3
- Use only the ABS, AOR, LCR, ROR, and UOI mutation operators. ^selective-mutation-operators
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf#page=6
- Before you run the mutants, check that each test passes on the original program. ^tests-pass-before-mutation
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf#page=4
- Generate mutants only for the changed lines of a change that the tests cover. ^mutate-changed-covered-lines
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=3
  - sources: https://arxiv.org/pdf/2102.11378#page=1
- Generate at most `1` mutant for each line. ^one-mutant-per-line
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=2
- Do not generate mutants in logging code, test code, or code that controls only non-functional properties, such as memory reservation. ^skip-arid-code
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=3
- Show each surviving mutant in the code review of the change. ^mutants-in-code-review
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=2
- Add a test for each surviving mutant that is productive. ^kill-productive-mutants
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://arxiv.org/pdf/2102.11378#page=2
  - sources: https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf#page=4
- Do not add a test that kills a mutant through an assertion on an implementation detail, not on the specification. ^skip-unproductive-mutants
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://homes.cs.washington.edu/~rjust/publ/practical_mutation_testing_tse_2021.pdf#page=2
- Exclude each equivalent mutant from the mutation score. ^exclude-equivalent-mutants
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf#page=4
- Compute the mutation score as the killed mutants divided by the mutants that are not equivalent. ^compute-mutation-score
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://web.eecs.umich.edu/~weimerw/2020-481F/readings/mutation-testing.pdf#page=4
- Report the surviving mutants of each change, not a mutation score of the whole code base. ^report-change-mutants
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=2
- Use the feedback of the developers on each shown mutant to suppress the kinds that they mark as not useful. ^suppress-by-feedback
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=1
  - sources: https://arxiv.org/pdf/2102.11378#page=2
- Use mutation testing to check whether the tests assert on the code that coverage marks as covered. ^mutation-after-coverage
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/4203.pdf#page=1
  - sources: https://arxiv.org/pdf/2102.11378#page=1

## Notes

Mutation testing rests on 2 hypotheses that Jia and Harman describe. The competent programmer hypothesis states that programmers write code close to the correct version, so real faults are small. The coupling effect states that a test set that detects each simple fault also detects most complex faults. In the studies that they cite, tests that killed each first-order mutant also killed over `99%` of the second-order and third-order mutants.

The process has 4 steps: generate the mutants with mutation operators, run the tests on the original program, run the tests on each mutant, and add tests for the mutants that survive. An equivalent mutant changes the code but not its behavior, so no test can kill it. The detection of equivalent mutants is undecidable in general, and it costs human effort.

A full mutation analysis is costly in machines and in human attention. Selective mutation uses a few operators: the 5 key operators of Offutt and colleagues kept a mutation score of `99.5%`. Google implements AOR, LCR, ROR, SBR, and UOI. It leaves out ABS, because ABS acted on values that are never negative in its code, and it states that this reason does not apply in general. Google makes the technique practical at scale with 3 limits:

- It mutates only the changed lines that the tests cover, during code review.
- It generates at most 1 mutant for each line.
- It skips arid code, where each mutant would be unproductive.

An unproductive mutant is equivalent to the original, or a test that kills it does not improve the suite. Such a test asserts on an implementation detail, such as the initial capacity of a collection, and not on the specification. At Google, developers first marked `85%` of the shown mutants as unproductive. Suppression based on their feedback raised the share of productive mutants from `15%` to `89%`.

Code coverage shows which lines the tests execute. Mutation testing shows whether the tests detect a change in those lines.
