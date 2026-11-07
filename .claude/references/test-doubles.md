<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Test doubles

## Directives

No directive is in force at this node.

## Definition

An object that replaces a production object in a test. Gerard Meszaros named the general term after a stunt double, and his xUnit Test Patterns names 5 kinds by their use: a dummy, a stub, a spy, a mock, and a fake. A test double gives the test control over the indirect inputs of the code under test, or a point to observe its indirect outputs, or a faster stand-in for a slow dependency.

## Notes

The 5 kinds differ by what the test does with the double:

- A dummy fills a parameter list and is never used.
- A stub returns canned answers. It is a control point for the indirect inputs of the code under test.
- A spy is a stub that also records how the code called it. The test checks the record after the action.
- A mock holds the expected calls before the action, and fails when a call does not match. It is an observation point for the indirect outputs.
- A fake has a working implementation with a shortcut that makes it unfit for production, such as an in-memory database.

State verification checks the state or the return value after the action. Behavior verification, or interaction testing, checks the calls that the code made to its dependencies. Martin Fowler names 2 styles of test-driven development after this choice: the classical style uses real objects where it can, and the mockist style uses a mock for each object with interesting behavior. The default tree follows the classical style of Software Engineering at Google: a real implementation first, a fake next, and a stub or a mock last. A mock couples the test to the implementation, so a refactor breaks the test.

The fidelity of a double is how closely it follows the real dependency. A double with low fidelity lets a test pass while the real code fails. Contract testing checks the fidelity of a double against the real service. The test pyramid sets where doubles go: each small test replaces the dependencies that leave its process.
