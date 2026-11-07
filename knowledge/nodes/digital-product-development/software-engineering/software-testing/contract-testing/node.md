---
id: contract-testing
kind: densho:Concept
title: Contract testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/ContractTest.html
  - https://martinfowler.com/articles/consumerDrivenContracts.html
  - https://docs.pact.io/
  - https://docs.pact.io/consumer
  - https://docs.pact.io/provider
broader:
  - software-testing
related:
  - test-doubles
---

## Definition

A test that checks that a test double still behaves like the external service that it stands for. Martin Fowler describes contract tests as checks that each call against a test double returns the same results as a call to the external service. Ian Robinson's consumer-driven contracts invert the direction: each consumer states what it expects of a provider, and the contract of the provider is the union of these expectations. The Pact docs define contract testing as a check of each application in isolation against a shared contract for the messages between them.

## Directives

- Write each HTTP contract as a set of interactions, each with an expected request and a minimal expected response. ^contract-as-interactions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/getting_started/how_pact_works
- Describe each precondition of an interaction as a provider state, not as an earlier interaction. ^provider-states
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/getting_started/how_pact_works
- In a consumer contract, state only the parts of the provider contract that the consumer uses. ^consumer-states-what-it-uses
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/consumerDrivenContracts.html#ConsumerContracts
  - sources: https://docs.pact.io/
- Build the contract of a provider from the union of the expectations of its consumers. ^provider-contract-from-consumers
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/consumerDrivenContracts.html#Consumer-drivenContracts
- Check with a contract test that each call to a test double returns the same result as the real service. ^double-matches-the-service
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/ContractTest.html
- Write the consumer side of a contract as unit tests of the API client of the consumer. ^consumer-tests-the-client
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#use-pact-for-isolated-unit-tests
- Send each call from a consumer to a provider through a client that the contract tests cover. ^calls-through-the-tested-client
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#ensure-all-calls-to-the-provider-go-through-classesfunctions-that-have-been-tested-with-pact
- Verify each contract against a local instance of the provider, not against a deployed instance. ^verify-against-local-provider
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/provider#verify-your-pacts-against-a-locally-running-instance-of-the-provider
- Run the verification of the consumer contracts in the build of the provider. ^verify-in-provider-build
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/provider#ensure-that-pact-verify-runs-as-part-of-your-ci-build
  - sources: https://martinfowler.com/bliki/ContractTest.html
- In a provider verification, limit the stubs to code that runs after the provider parses and validates the request. ^stub-below-request-parsing
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/provider#only-stub-layers-beneath-where-contents-of-the-request-body-are-extracted
- Before a consumer or a provider deploys, check that its version passed verification with each version in the target environment. ^can-i-deploy
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/pact_broker/can_i_deploy
  - sources: https://docs.pact.io/consumer#use-can-i-deploy
- Record the version and the environment of each deployment of a consumer or a provider. ^record-each-deployment
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/pact_broker/can_i_deploy
- Do not use a contract test to test the functions of the provider. ^contract-not-functional
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#use-pact-for-contract-testing-not-functional-testing-of-the-provider
- Include a scenario only if its absence hides a consumer bug or a misunderstanding of the provider response. ^scenario-must-catch-something
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#use-pact-for-contract-testing-not-functional-testing-of-the-provider
- Assert only on the fields that affect the consumer when they change. ^assert-consumer-fields-only
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#only-make-assertions-about-things-that-will-affect-the-consumer-if-they-change
- Prefer type matching over exact matching for the fields of a response. ^loose-response-matching
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#choose-the-right-type-of-matching-for-the-situation
- If a stub holds a snapshot of a response, make the contract test check its data format, not its values. ^check-format-not-data
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/ContractTest.html
- Do not use contract tests to test the user interface of a consumer. ^no-contract-tests-through-ui
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#avoid-using-pact-for-tests-that-involve-the-ui
- In a write interaction, prefer the updated resource in the response over a fixture shared with a read. ^expect-written-values-back
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#beware-of-garbage-in-garbage-out-with-putpostpatch
- Run the contract tests of an external service at the pace of its changes, such as once a day. ^external-contract-test-pace
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/ContractTest.html
- Prefer the test instance of an external service over its production instance for the contract tests. ^external-contract-test-instance
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/ContractTest.html
- If a contract test of an external service fails, open a task to bring the test doubles back in line. ^fix-doubles-on-contract-failure
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/ContractTest.html
- Tell the owners of an external service when a change to its contract breaks a contract test. ^tell-the-service-owners
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/bliki/ContractTest.html
- Reject a consumer expectation that falls outside the business function of the provider. ^reject-out-of-mandate-expectations
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/consumerDrivenContracts.html#Liabilities
- If the consumers of an API are unknown, do not use consumer-driven contracts. ^cdc-needs-known-consumers
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://martinfowler.com/articles/consumerDrivenContracts.html#Liabilities
  - sources: https://docs.pact.io/faq/convinceme#but-our-company-develops-apis-before-consumers-eg-apidocument-driven-design
- Do not treat a shared OpenAPI description as a contract test, unless a tool checks each side against it. ^openapi-is-not-a-contract-test
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/faq/convinceme#but-i-use-swaggeropenapi
- In the broader tests of the consumer, use the contract or shared fixtures as the stubs of the provider. ^stub-from-the-contract
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://docs.pact.io/consumer#avoid-using-pact-for-tests-that-involve-the-ui

## Notes

A contract test has 2 sides. The consumer side runs the API client of the consumer against a mock provider and records each interaction. The provider side replays each recorded interaction against the real provider and checks the response. Each interaction is independent, and a provider state sets up the data that it needs.

Ian Robinson names 3 kinds of contract:

- A provider contract is closed, complete, and authoritative. It lists each function that the provider offers.
- A consumer contract is open and incomplete. It lists only what one consumer uses, and there is one for each consumer.
- A consumer-driven contract is the union of the consumer contracts. It is complete for the current consumers, but not authoritative.

Robinson states the limits of the pattern: it works inside one company or a closed group of known services, it does not remove coupling, and it shows the coupling that was hidden.

Martin Fowler first used contract tests for an external service that another team owns. Those tests run on the schedule of the external service, and a failure starts a task and need not break the build. The Pact docs use the same name for tests between services in one system, and these run in the build of each side.

The interface contract of software design describes the whole API, such as an OpenAPI description. A consumer contract checks the part that a consumer uses, by example. Test doubles are what a contract test keeps faithful. The test pyramid places contract tests next to the narrow integration tests that use those doubles.
