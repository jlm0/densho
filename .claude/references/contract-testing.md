<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Contract testing

## Directives

No directive is in force at this node.

## Definition

A test that checks that a test double still behaves like the external service that it stands for. Martin Fowler describes contract tests as checks that each call against a test double returns the same results as a call to the external service. Ian Robinson's consumer-driven contracts invert the direction: each consumer states what it expects of a provider, and the contract of the provider is the union of these expectations. The Pact docs define contract testing as a check of each application in isolation against a shared contract for the messages between them.

## Notes

A contract test has 2 sides. The consumer side runs the API client of the consumer against a mock provider and records each interaction. The provider side replays each recorded interaction against the real provider and checks the response. Each interaction is independent, and a provider state sets up the data that it needs.

Ian Robinson names 3 kinds of contract:

- A provider contract is closed, complete, and authoritative. It lists each function that the provider offers.
- A consumer contract is open and incomplete. It lists only what one consumer uses, and there is one for each consumer.
- A consumer-driven contract is the union of the consumer contracts. It is complete for the current consumers, but not authoritative.

Robinson states the limits of the pattern: it works inside one company or a closed group of known services, it does not always reduce the coupling, and it shows the coupling that was hidden.

Martin Fowler describes contract tests for an external service that a different team maintains. Those tests run on the schedule of the external service, and a failure starts a task and need not break the build. The Pact docs use the same name for tests between 2 services that communicate, and these run in the build of each side.

The interface contract of software design describes the whole API, such as an OpenAPI description. A consumer contract checks the part that a consumer uses, by example. Test doubles are what a contract test keeps faithful. The test pyramid places contract tests next to the narrow integration tests that use those doubles.
