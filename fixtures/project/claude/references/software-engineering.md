<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software engineering

## Directives

From [Digital product development](digital-product-development.md):

- Name the user and the task of each feature before you design or build the feature. ^name-user-and-task

From [Secrets management](secrets-management.md):

- Do not commit a secret to a repository. ^no-secret-in-repository
- If a secret reaches a repository, revoke the secret. ^revoke-exposed-secret

From [Software engineering](software-engineering.md):

- Write a test for each change in behavior, unless the changed code has no conditional logic. ^test-each-behavior-change

## Definition

The design, construction, testing, and operation of software. It turns product and interface decisions into a system that keeps working as it changes. Its practice areas follow the knowledge areas of the Guide to the Software Engineering Body of Knowledge (SWEBOK) `v4`, in the order of the work: requirements, architecture, design, testing, construction, configuration management, quality, and operations. Security runs across each step.

## References

- You design the structure of a system or change it. Read [Software architecture](software-architecture.md).
- You make a commit, a branch, or a build. Read [Software configuration management](software-configuration-management.md).
- You write the code of a service, a client, or its infrastructure. Read [Software construction](software-construction.md).
- You define the interface of an API or a component. Read [Software design](software-design.md).
- You deploy or monitor a service. Read [Software operations](software-operations.md).
- You review, verify, or accept a change. Read [Software quality](software-quality.md).
- You define the requirements of a change. Read [Software requirements](software-requirements.md).
- You write code that handles input, a user account, or a secret. Read [Software security](software-security.md).
- You write a test or fix a bug. Read [Software testing](software-testing.md).
