---
id: twelve-factor-app
kind: ka:Concept
title: Twelve-factor app
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://12factor.net/
  - https://12factor.net/config
  - https://12factor.net/disposability
broader:
  - software-architecture
related:
  - software-supply-chain
---

## Definition

A method by Adam Wiggins for building software-as-a-service apps. It names twelve factors: one codebase, explicit dependencies, config in the environment, backing services as attached resources, separate build and run stages, stateless processes, port binding, concurrency through processes, disposability, parity between development and production, logs as event streams, and admin tasks as one-off processes.

## Directives

- Keep each config value that differs between deploys out of the source code. ^config-out-of-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/config
- Declare each dependency of an app in a dependency manifest. ^declare-each-dependency
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/dependencies
- Do not call a system tool that the app does not declare as a dependency. ^no-implicit-system-tool
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/dependencies
- Store each persistent state in a backing service, not in the memory or the disk of a process. ^stateless-processes
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/processes
- Write the logs of each process to `stdout` as an unbuffered stream. ^logs-to-stdout
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/logs
- Stop each process cleanly when it receives `SIGTERM`. ^graceful-shutdown
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/disposability
- Use the same type and version of each backing service in development and in production. ^same-backing-services
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://12factor.net/dev-prod-parity

## Notes

The config test of the method: the codebase could become public at any moment, and no credential would leak. A clean stop differs by process. A web process stops listening, finishes its current requests, and exits. A worker returns its current job to the queue.
