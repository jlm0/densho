<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Black-box test techniques

## Directives

No directive is in force at this node.

## Definition

Techniques that select test cases from the specified behavior of the test object, without reference to its internal structure. The ISTQB Foundation Level syllabus names 4: equivalence partitioning, boundary value analysis, decision table testing, and state transition testing. SWEBOK v4 calls them specification-based techniques, and adds combinatorial testing, such as pairwise testing. Each technique defines its coverage items, and its coverage is the share of those items that the tests exercise.

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
