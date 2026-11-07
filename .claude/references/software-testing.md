<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software testing

## Directives

No directive is in force at this node.

## Definition

The dynamic validation that a system under test gives the expected behavior on a finite set of test cases, selected from a domain of executions that is usually infinite. SWEBOK v4 gives this definition. The ISTQB Foundation Level syllabus adds static testing, and splits the test process into planning, monitoring and control, analysis, design, implementation, execution, and completion. Here, testing turns the contracts of software design into automated tests, and construction writes the code that passes them.

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
- Syntax testing, cause-effect graphing, domain-specific testing, and test tools stay out. Decision tables cover the logic of cause-effect graphs.

## Comes from

The output of each node in this list is an input of this node.

- [Software design](software-design.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software construction](software-construction.md)

## References

- You test the output of an AI model or an AI feature. Read [AI evaluations](ai-evaluations.md).
- You choose the test inputs for a behavior from its specification. Read [Black-box test techniques](black-box-test-techniques.md).
- You measure the code coverage of a test suite. Read [Code coverage](code-coverage.md).
- A test uses a test double for another service. Read [Contract testing](contract-testing.md).
- A test runs the whole deployed system through its user interface or its public API. Read [End-to-end testing](end-to-end-testing.md).
- A test connects the code to a database, a file system, a queue, or another service. Read [Integration testing](integration-testing.md).
- You generate tests from a model of the system under test. Read [Model-based testing](model-based-testing.md).
- You check whether the tests detect a change in the covered code. Read [Mutation testing](mutation-testing.md).
- You test the response time, the throughput, or the capacity of a system under load. Read [Performance testing](performance-testing.md).
- You write a test that generates its own input values. Read [Property-based testing](property-based-testing.md).
- You run the existing tests again after a change to the code. Read [Regression testing](regression-testing.md).
- A test replaces a dependency with a stub, a mock, or a fake. Read [Test doubles](test-doubles.md).
- You write the code for a new behavior. Read [Test-driven development](test-driven-development.md).
- You choose the level of a new test. Read [Test pyramid](test-pyramid.md).
- You write a test for one function, one class, or one module. Read [Unit testing](unit-testing.md).
