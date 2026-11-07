---
id: model-based-testing
kind: densho:Concept
title: Model-based testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf
  - https://researchcommons.waikato.ac.nz/handle/10289/6393
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=128
broader:
  - software-testing
---

## Definition

A way to test that derives the test cases from a model of the system under test or of its environment. Utting, Pretschner, and Legeard give this definition in their taxonomy of model-based testing approaches. The ISTQB Model-Based Tester syllabus names the parts: the model, the test selection criteria that choose the tests from the model, the generated testware, and the test adaptation layer that connects the abstract tests to the real interfaces. SWEBOK v4 lists the approach as scenario-based testing.

## Directives

- Choose the focus of each model from its test objective, such as a state machine for responses in each state. ^model-from-the-test-objective
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=21
- Keep in each model only the details that its test objectives need. ^model-abstraction-level
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=23
- Prefer `2` focused models over `1` model that covers each aspect of the system. ^focused-models
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=23
- Link each model element to the requirements that it covers. ^link-model-to-requirements
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=24
- Before the team builds models, write the modeling guidelines. ^modeling-guidelines
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=25
- Write the test model apart from the system design model, with a different author. ^independent-test-model
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=25
- Add model elements for unusual scenarios and error situations to the test model. ^model-error-situations
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=25
- After each increment of the model, run its generated tests again. ^iterate-model-and-tests
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=23
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=26
- Combine test selection criteria, such as requirements coverage and model coverage, to fit the test objectives. ^combine-selection-criteria
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=29
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=31
- Record each test selection criterion and the reason for it. ^record-selection-criteria
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=31
- If the number of generated tests exceeds the test budget, limit the test selection criteria. ^narrow-criteria-against-explosion
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=15
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=31
- Change the model, not the generated tests. ^model-is-the-master
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=31
- Before you change a model work product, check the impact on the model, the selection criteria, and the adaptation layer. ^model-change-impact
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=34
- If only the interface of the test object changes, update only the test adaptation layer. ^interface-change-in-adapter
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=34
- Set the precondition of each generated test script at the start of the script. ^set-script-preconditions
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=35
- Check the syntax, the meaning, and the fit of each model with reviews, tool checks, and model simulation. ^check-model-quality
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=15
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=23
- Define measurable objectives for model-based testing before you choose a tool. ^objectives-before-tools
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=15
- Do not use model-based testing in place of the black-box test techniques. ^model-based-testing-complements
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CT-MBT_-_Syllabus_Version_v1.1.pdf#page=15

## Notes

The ISTQB syllabus names 3 subjects of a model, and a model often combines them:

- A system model describes the system as it is intended to be, such as a state machine.
- An environment model, or usage model, describes the use of the system, such as a Markov chain.
- A test model describes the test cases and their expected results.

A model has 3 quality characteristics. Syntactic quality means that the model follows the rules of its language. Semantic quality means that its content is correct. Pragmatic quality means that it suits the test objective and the generator. The common mistakes are the wrong level of detail and one model that tries to cover everything.

The test selection criteria choose a subset of the tests that a model can generate. The families are model coverage, such as each state and transition, requirements coverage, data coverage with equivalence partitions and boundary values, random or stochastic walks, scenarios and patterns, and project information such as risk. The model is the master, and the tests are derived work products. A small change of the model can change the whole selection.

A model that the system design reuses without change gives verification tests only, and it copies each error of the design into the tests. The syllabus recommends separate models by different authors. A test adaptation layer turns the abstract tests into executable scripts. A change of the interface alone touches only that layer.

Model-based testing is used mostly at the system, system integration, and acceptance levels. It supports the black-box test techniques and does not replace them. Property-based testing uses a state machine model in a similar way for code with side effects.
