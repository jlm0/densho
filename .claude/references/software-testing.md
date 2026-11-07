<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software testing

## Directives

No directive is in force at this node.

## Definition

The automated checks that show that code does what it claims, and that keep it doing so as the code changes. A test runs the code with known inputs and compares the result with an expected result.

## Notes

A flaky test passes and fails on the same code. Software Engineering at Google reports that a suite loses the trust of engineers when about `1%` of its runs are flaky.

## Comes from

The output of each node in this list is an input of this node.

- [Software design](software-design.md)

## Goes to

The output of this node is an input of each node in this list.

- [Software construction](software-construction.md)

## References

- You test the output of an AI model or an AI feature. Read [AI evaluations](ai-evaluations.md).
- A test uses a test double for another service. Read [Contract testing](contract-testing.md).
- A test runs the whole deployed system through its user interface or its public API. Read [End-to-end testing](end-to-end-testing.md).
- A test connects the code to a database, a file system, a queue, or another service. Read [Integration testing](integration-testing.md).
- A test replaces a dependency with a stub, a mock, or a fake. Read [Test doubles](test-doubles.md).
- You write the code for a new behavior. Read [Test-driven development](test-driven-development.md).
- You choose the level of a new test. Read [Test pyramid](test-pyramid.md).
- You write a test for one function, one class, or one module. Read [Unit testing](unit-testing.md).
