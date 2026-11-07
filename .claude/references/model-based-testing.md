<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Model-based testing

## Directives

No directive is in force at this node.

## Definition

A way to test that derives the test cases from a model of the system under test or of its environment. Utting, Pretschner, and Legeard give this definition in their taxonomy of model-based testing approaches. The ISTQB Model-Based Tester syllabus names the parts: the model, the test selection criteria that choose the tests from the model, the generated testware, and the test adaptation layer that connects the abstract tests to the real interfaces. SWEBOK v4 lists the approach as scenario-based testing.

## Notes

The ISTQB syllabus names 3 subjects of a model, and a model often combines them:

- A system model describes the system as it is intended to be, such as a state machine.
- An environment model, or usage model, describes the use of the system, such as a Markov chain.
- A test model describes the test cases and their expected results.

A model has 3 quality characteristics. Syntactic quality means that the model follows the rules of its language. Semantic quality means that its content is correct. Pragmatic quality means that it suits the test objective and the generator. The common mistakes are the wrong level of detail and one model that tries to cover everything.

The test selection criteria choose a subset of the tests that a model can generate. The families are model coverage, such as each state and transition, requirements coverage, data coverage with equivalence partitions and boundary values, random or stochastic walks, scenarios and patterns, and project information such as risk. The model is the master, and the tests are derived work products. A small change of the model can change the whole selection.

A model that the system design reuses without change gives verification tests only, and it copies each error of the design into the tests. The syllabus recommends separate models by different authors. A test adaptation layer turns the abstract tests into executable scripts. A change of the interface alone touches only that layer.

Model-based testing is used mostly at the system, system integration, and acceptance levels. It supports the black-box test techniques and does not replace them. Property-based testing uses a state machine model in a similar way for code with side effects.
