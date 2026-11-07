---
id: infrastructure-engineering
kind: densho:PracticeArea
title: Infrastructure engineering
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/InfrastructureAsCode.html
  - https://12factor.net/
broader:
  - software-construction
pointers:
  - kind: densho:TextPointer
    target: infrastructure-as-code
    trigger: You create or change a server, a network, or an environment.
  - kind: densho:TextPointer
    target: twelve-factor-app
    trigger: You configure, deploy, or run a service.
---

## Definition

The definition and the upkeep of the environments where software runs: servers, networks, and the configuration of each service. Here, the infrastructure lane defines each environment in code and shapes each service so that it deploys the same way in each environment.
