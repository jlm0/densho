<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Property-based testing

## Directives

No directive is in force at this node.

## Definition

A way to test code by stating general properties that the code must hold, and by checking them on generated test cases. John Hughes describes it in "How to Specify It!": the tool generates the cases, usually at random, and reports a minimized failing case when a property does not hold. Claessen and Hughes introduced the approach with QuickCheck in 2000, and joined 2 older ideas: specifications as test oracles, and random testing. David MacIver adds that the person designs the property, and the tool only fuzzes it.

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
