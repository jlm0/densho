<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Mutation testing

## Directives

No directive is in force at this node.

## Definition

A fault-based technique that measures how well a test set detects faults. Jia and Harman describe the process: small syntactic changes seed faults into the program, and each changed copy is a mutant. A test set kills a mutant when a test gives a different result on the mutant than on the original program. The mutation score is the ratio of killed mutants to the mutants that are not equivalent to the original. Petrović and colleagues at Google separate mutation analysis, which measures a test suite, from mutation testing, which uses each surviving mutant as the goal of a new test.

## Notes

Mutation testing rests on 2 hypotheses that Jia and Harman describe. The competent programmer hypothesis states that programmers write code close to the correct version, so real faults are small. The coupling effect states that a test set that detects each simple fault also detects most complex faults. In the studies that they cite, tests that killed each first-order mutant also killed over `99%` of the second-order and third-order mutants.

The process has 4 steps: generate the mutants with mutation operators, run the tests on the original program, run the tests on each mutant, and add tests for the mutants that survive. An equivalent mutant changes the code but not its behavior, so no test can kill it. The detection of equivalent mutants is undecidable in general, and it costs human effort.

A full mutation analysis is costly in machines and in human attention. Selective mutation uses a few operators: the 5 key operators of Offutt and colleagues kept a mutation score of `99.5%`. Google makes the technique practical at scale with 3 limits:

- It mutates only the changed lines that the tests cover, during code review.
- It generates at most 1 mutant for each line.
- It skips arid code, where each mutant would be unproductive.

An unproductive mutant is equivalent to the original, or a test that kills it does not improve the suite. Such a test asserts on an implementation detail, such as the initial capacity of a collection, and not on the specification. At Google, developers first marked `85%` of the shown mutants as unproductive. Suppression based on their feedback raised the share of productive mutants from `15%` to `89%`.

Code coverage shows which lines the tests execute. Mutation testing shows whether the tests detect a change in those lines.
