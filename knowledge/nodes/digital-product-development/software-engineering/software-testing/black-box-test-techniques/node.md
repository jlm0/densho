---
id: black-box-test-techniques
kind: densho:Concept
title: Black-box test techniques
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=126
  - https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf
broader:
  - software-testing
---

## Definition

Techniques that select test cases from the specified behavior of the test object, without reference to its internal structure. The ISTQB Foundation Level syllabus names 4: equivalence partitioning, boundary value analysis, decision table testing, and state transition testing. SWEBOK v4 calls them specification-based techniques, and adds combinatorial testing, such as pairwise testing. Each technique defines its coverage items, and its coverage is the share of those items that the tests exercise.

## Directives

- Build each black-box test from the specified behavior of the test object, not from its code. ^test-the-specified-behavior
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39
- Define the equivalence partitions of each input, output, and configuration value of the test object. ^define-equivalence-partitions
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=126
- Define the partitions of a value range from the specification, not from evenly spaced points of the range. ^partitions-from-the-specification
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=25
- Make the partitions of each data element non-empty and without overlap. ^partitions-without-overlap
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39
- Test at least `1` value from each equivalence partition, including each invalid partition. ^test-each-partition
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=40
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=127
- If a test object has more than `1` input, test each partition of each input in at least `1` test. ^each-choice-coverage
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=40
- Use boundary value analysis only for ordered partitions. ^boundaries-of-ordered-partitions
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=40
- Test each boundary value of an ordered partition and its closest neighbor in the next partition. ^test-each-boundary
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=40
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=127
- For each boundary, test the boundary value and both of its neighbors. ^prefer-three-value-boundaries
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=40
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=26
- When you test the robustness of a program, include values outside its input domain in the boundary tests. ^test-outside-the-domain
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=127
- If a requirement maps combinations of conditions to different outcomes, write a decision table for it. ^decision-table-for-combinations
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=127
- Write each condition and each action of the system as a row of the decision table. ^decision-table-rows
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
- Write each combination of conditions as a column of the decision table, with its actions. ^decision-table-columns
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
- When you simplify a decision table, delete each column that holds an infeasible combination of conditions. ^delete-infeasible-columns
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
- Test each feasible column of the decision table, unless the test budget covers only part of the table. ^test-each-column
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
- If the test budget covers only part of a decision table, test the minimized table in order of risk. ^choose-columns-by-risk
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
- Record each gap and each contradiction in the requirements that the decision table shows. ^record-requirement-gaps
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
- If events move the test object between states, write a state table of its states and transitions. ^state-table-for-history
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=41
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=127
- Test each valid transition of the state table at least once. ^valid-transitions-coverage
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=42
- Test at most `1` invalid transition in each test case. ^one-invalid-transition-per-test
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=42
- In mission-critical or safety-critical software, test each valid transition and each invalid transition of the state table. ^all-transitions-for-critical-software
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=42
- If an exhaustive test is too costly, test at least each pair of values with a covering array. ^pairwise-covering-array
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=7
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=127
- In mission-critical software, do not limit the combinatorial tests to pairs of values. ^beyond-pairs-for-critical-software
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=7
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=11
- Limit each parameter of a combinatorial test to `10` values or fewer. ^limit-values-per-parameter
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=26
- Define each invalid combination of values as a constraint of the covering array. ^constraints-for-invalid-combinations
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=22
- Do not delete a test with an invalid combination from a covering array, unless other tests cover its valid combinations. ^keep-covering-array-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf#page=22
- Measure the coverage of each technique as the percent of its coverage items that the tests exercise. ^record-technique-coverage
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=40
- Keep each black-box test when the implementation changes and the required behavior stays the same. ^keep-tests-across-implementations
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39

## Notes

Each technique has its own coverage items:

| Technique                 | Coverage items                                                              |
| ------------------------- | --------------------------------------------------------------------------- |
| Equivalence partitioning  | The partitions, valid and invalid                                           |
| 2-value boundary analysis | Each boundary value and its closest neighbor in the next partition          |
| 3-value boundary analysis | Each boundary value and both of its neighbors                               |
| Decision table testing    | The feasible columns                                                        |
| State transition testing  | All states, the valid transitions, or all transitions with invalid ones     |
| Combinatorial testing     | Each combination of `t` parameter values, such as each pair when `t` is `2` |

The ISTQB syllabus ranks the state transition criteria. Valid transitions coverage is the most widely used, and it implies all states coverage. All transitions coverage implies both, and the syllabus sets it as the minimum for mission-critical and safety-critical software. 3-value boundary analysis can find defects that 2-value analysis misses, such as `x = 10` in place of `x <= 10`.

NIST SP 800-142 states the interaction rule from fault studies: most failures come from 1 parameter or the interaction of 2, and fewer come from 3 or more. In the studies, tests of all 4-way to 6-way combinations found each fault. Pairwise testing can miss `10%` to `40%` or more of the faults of a system. A covering array holds each `t`-way combination in few tests. A constraint keeps an invalid combination out of the array. The tool still covers each valid combination that a deletion of tests would lose.

Black-box tests do not depend on the code, so they stay useful when the implementation changes and the required behavior stays the same. White-box tests check the structure, and code coverage holds their rules. The 2 kinds find different defects. Property-based testing generates the input values at random, and model-based testing generates the tests from a model, such as a state machine.
