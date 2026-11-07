---
id: property-based-testing
kind: densho:Concept
title: Property-based testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf
  - https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf
  - https://hypothesis.works/articles/what-is-property-based-testing/
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=128
broader:
  - software-testing
---

## Definition

A way to test code by stating general properties that the code must hold, and by checking them on generated test cases. John Hughes describes it in "How to Specify It!": the tool generates the cases, usually at random, and reports a minimized failing case when a property does not hold. Claessen and Hughes introduced the approach with QuickCheck in 2000, and joined 2 older ideas: specifications as test oracles, and random testing. David MacIver adds that the person designs the property, and the tool only fuzzes it.

## Directives

- Write each property as a statement that holds for each valid input, not for one example. ^properties-not-examples
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=1
  - sources: https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf#page=1
- Do not copy the implementation into a property to compute the expected result. ^no-reimplementation-in-properties
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=5
- If a data type has an invariant, write a validity property that each operation keeps the invariant. ^validity-properties
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=9
- Write a postcondition that relates the result of each call to its arguments. ^postcondition-properties
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=10
- If the expected result is hard to compute, write metamorphic properties that relate the results of `2` related calls. ^metamorphic-properties
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=11
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=130
- If time is limited, write model-based properties and validity properties first. ^model-based-properties-first
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=21
- If the model is costly or resembles the implementation, write metamorphic properties in place of model-based properties. ^metamorphic-when-the-model-is-costly
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=21
- If the code under test has side effects, test sequences of operations against a state machine model. ^state-machine-properties
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=22
- Write the properties against the exported API, unless a property checks the invariant of the representation. ^properties-through-the-api
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=22
- Make each generator able to produce each valid test case. ^complete-generators
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=22
- Test that each generator and each shrinker produce only valid values. ^test-generators-and-shrinkers
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=9
- Use a tool that shrinks each failing case to a minimal counterexample. ^shrink-failing-cases
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=5
- If a precondition rejects most generated inputs, write a generator that produces only valid inputs. ^generators-for-preconditions
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf#page=3
- Check the distribution of the generated cases with labels after each run. ^measure-the-distribution
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf#page=3
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=17
- If a property has a precondition, check the share of trivial cases among the tested cases. ^check-trivial-cases
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf#page=3
- If most generated cases miss the behavior that a property checks, change the generator. ^rebalance-the-generator
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=17

## Notes

Hughes names 5 kinds of property, and a pitfall for each:

- A validity property checks that each operation keeps the invariant of a data type. Validity alone is weak: a function that always returns an empty value keeps the invariant.
- A postcondition relates the result of 1 call to its arguments.
- A metamorphic property relates the results of 2 related calls, such as an insert before and after a union. It needs no expected value, so it solves the oracle problem in many cases.
- An inductive property relates a call to calls with smaller arguments. A complete set of inductive properties gives a proof of correctness.
- A model-based property compares the result of 1 call with the result of a simpler abstract operation on a model.

In the comparison of Hughes, model-based properties found each seeded bug with few properties. Metamorphic properties were almost as effective, but they need more properties.

A generator produces the test cases, and a shrinker turns a failing case into a smaller one. Shrinking gives a counterexample in which each part matters to the failure. The QuickCheck paper shows a common failure: a precondition such as "the list is ordered" skews the generated cases toward short lists, so most tests check almost nothing. A label on each case shows the distribution, and a custom generator corrects it.

Property-based testing is not the same as fuzzing. MacIver defines fuzzing as feeding code data from a large corpus to see whether it fails. A property-based test adds the properties that a person writes, so a failure shows a problem that plain fuzzing does not find. Security fuzzing belongs to software security. Black-box test techniques choose the test values by hand, and property-based testing generates them.
