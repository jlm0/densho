---
id: software-testing
kind: densho:PracticeArea
title: Software testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=117
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
  - https://martinfowler.com/articles/practical-test-pyramid.html
  - https://abseil.io/resources/swe-book/html/ch11.html
broader:
  - software-engineering
informs:
  - software-construction
pointers:
  - kind: densho:TextPointer
    target: test-driven-development
    trigger: You write the code for a new behavior.
  - kind: densho:TextPointer
    target: test-pyramid
    trigger: You choose the level of a new test.
  - kind: densho:TextPointer
    target: unit-testing
    trigger: You write a test for one function, one class, or one module.
  - kind: densho:TextPointer
    target: integration-testing
    trigger: A test connects the code to a database, a file system, a queue, or another service.
  - kind: densho:TextPointer
    target: end-to-end-testing
    trigger: A test runs the whole deployed system through its user interface or its public API.
  - kind: densho:TextPointer
    target: test-doubles
    trigger: A test replaces a dependency with a stub, a mock, or a fake.
  - kind: densho:TextPointer
    target: contract-testing
    trigger: A test uses a test double for another service.
  - kind: densho:TextPointer
    target: black-box-test-techniques
    trigger: You choose the test inputs for a behavior from its specification.
  - kind: densho:TextPointer
    target: property-based-testing
    trigger: You write a test that generates its own input values.
  - kind: densho:TextPointer
    target: model-based-testing
    trigger: You generate tests from a model of the system under test.
  - kind: densho:TextPointer
    target: code-coverage
    trigger: You measure the code coverage of a test suite.
  - kind: densho:TextPointer
    target: mutation-testing
    trigger: You check whether the tests detect a change in the covered code.
  - kind: densho:TextPointer
    target: regression-testing
    trigger: You run the existing tests again after a change to the code.
  - kind: densho:TextPointer
    target: performance-testing
    trigger: You test the response time, the throughput, or the capacity of a system under load.
  - kind: densho:TextPointer
    target: ai-evaluations
    trigger: You test the output of an AI model or an AI feature.
---

## Definition

The dynamic validation that a system under test gives the expected behavior on a finite set of test cases, selected from a domain of executions that is usually infinite. SWEBOK v4 gives this definition. The ISTQB Foundation Level syllabus adds static testing, and splits the test process into planning, monitoring and control, analysis, design, implementation, execution, and completion. Here, testing turns the contracts of software design into automated tests, and construction writes the code that passes them.

## Directives

- Use the interface contract and the UI contract of each part as the test basis of its tests. ^contracts-as-test-basis
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
- Split each test into its setup, its action, and its verification. ^setup-action-verification
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#TestStructure
- Define the expected result of each test before you run it. ^expected-result-for-each-test
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=121
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=19
- Review the specification for ambiguities, gaps, and contradictions before you write its tests. ^review-the-test-basis
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=27
- During test analysis, check the testability of the test basis and the test object. ^check-testability
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=19
- Write a defect report for each defect that test analysis finds in the test basis, unless you fix it directly. ^report-test-basis-defects
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=20
- Link each test case to each element of the test basis that it covers. ^trace-tests-to-the-basis
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=20
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=21
- Write the tests of each behavior before construction writes its code. ^tests-before-code
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=26
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=27
- Include a test that reproduces the bug in each bug fix. ^test-before-bug-fix
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#strive_for_unchanging_tests
  - sources: https://martinfowler.com/bliki/TestPyramid.html
- Test each unit through its public interface, unless a property checks the invariant of its representation. ^test-public-interface
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#WhatToTest
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#test_via_public_apis
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=18
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39
  - sources: https://research.chalmers.se/publication/517894/file/517894_Fulltext.pdf#page=23
- Run static analysis of the source code before the dynamic tests. ^static-analysis-first
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=27
- Run the automated component tests on each commit in continuous integration. ^tests-in-continuous-integration
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=27
- Commit the automated tests with the source code that they test. ^commit-tests-with-code
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=27
- Set the test levels, the test techniques, and the coverage targets from the product risk analysis. ^product-risk-sets-scope
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=53
- Use the observed defect clusters as an input to the product risk analysis. ^defect-clusters-into-risk
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=18
- Select the tests with test techniques, priorities, and risks, not with exhaustive testing. ^no-exhaustive-testing
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=18
- Choose the level of each new test with the test pyramid. ^choose-level-with-the-pyramid
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=50
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=51
- Choose the inputs of each test with a test technique. ^choose-inputs-with-a-technique
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=18
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=39
- Combine the black-box test techniques with code coverage. ^combine-functional-and-structural
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=132
- Do not write a test for code without conditional logic, such as a plain getter or setter. ^skip-trivial-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/practical-test-pyramid.html#WhatToTest
- Do not treat a passing test suite as proof that the code has no defects. ^passing-tests-are-not-proof
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=17
- If the existing tests stop finding new defects, add new tests. ^refresh-worn-out-tests
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=18
- Do not put a conditional or a loop in an example-based test, unless the loop polls for an asynchronous result. ^no-logic-in-tests
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests
  - sources: https://abseil.io/resources/swe-book/html/ch14.html#speeding_up_tests
- Do not treat an automatic rerun of a flaky test as a fix of its cause. ^no-rerun-for-flaky-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#flaky_tests_are_expensive
- If the oracle gives no verdict, record the result as inconclusive, not as a pass. ^inconclusive-results
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=121
- Write a defect report for each anomaly of a test run after you analyze its cause. ^report-each-defect
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=19
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=56
- Record the test object, steps, expected and actual results, and severity of each test failure in its defect report. ^defect-report-contents
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=57
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=56
- Define the entry criteria and the exit criteria of each test level in the test plan. ^entry-and-exit-criteria
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=49
- Before you end a test level, measure its coverage of the product risks, the requirements, and the acceptance criteria. ^measure-exit-coverage
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=53
- If no time or budget remains, end the testing early only with the risk acceptance of the stakeholders. ^accepted-risk-for-early-exit
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=49
- In Agile development, use the exit criteria of the tests as the Definition of Done of each releasable item. ^exit-criteria-as-definition-of-done
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=49
- After test completion, add a backlog item for each unresolved defect. ^backlog-item-for-open-defects
  - scope: node
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=19

## Notes

The ISTQB syllabus states 7 principles of testing:

- Testing shows the presence of defects, not their absence.
- Exhaustive testing is impossible, except in trivial cases.
- Early testing saves time and money.
- Defects usually cluster in a small number of components.
- Tests wear out: the same tests find fewer new defects each time.
- Testing depends on its context.
- A system without known defects can still fail the needs of its users.

An error of a person produces a defect, and a defect that runs can cause a failure. A test oracle decides whether a test passes or fails. When the oracle cannot decide, the result is inconclusive.

The testing quadrants of Brian Marick group the tests in 2 dimensions. A test faces the business or the technology, and it supports the team or critiques the product. Unit and component integration tests support the team from the technology side, and they run in continuous integration. Functional tests and examples support the team from the business side. Exploratory, usability, and acceptance tests critique the product from the business side. Performance tests and other non-functional tests critique the product from the technology side. In the whole team approach, each member of the team shares the responsibility for quality.

A flaky test passes and fails on the same code. Software Engineering at Google reports that as a suite approaches a flaky rate of `1%`, its tests begin to lose value.

The coverage of this practice area follows 2 anchors: the ISTQB Certified Tester Foundation Level syllabus `v4.0.1` and chapter 5 of SWEBOK `v4`.

- The directives of this practice area cover the principles, the test activities, traceability, shift left, product risk, the oracle, the defect report, and the exit gate.
- The concepts cover the test levels, the test mix, test-driven development, test doubles, contract testing, black-box test techniques, property-based testing, model-based testing, code coverage, mutation testing, regression testing and flaky tests, performance testing, and AI evaluations.
- Other practice areas hold acceptance testing, exploratory testing, code review, and the definition of done (software quality). They also hold security and privacy testing (software security), usability testing (user research), requirements traceability and specification by example (software requirements), and configuration management.
- Test management stays out: planning, estimation, monitoring, roles, and staffing. The tree holds no node for it.
- Experience-based techniques, such as error guessing and checklists, stay with exploratory testing in software quality.
- The non-functional types other than performance stay out. The sources give no rules that an agent can apply alone.
- Syntax testing, cause-effect graphing, domain-specific testing, and test tools stay out. SWEBOK names cause-effect graphing as a technique related to decision tables.
