---
id: infrastructure-as-code
kind: densho:Concept
title: Infrastructure as code
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/bliki/InfrastructureAsCode.html
broader:
  - infrastructure-engineering
---

## Definition

The definition of computing and network infrastructure through source code that a team treats like any other software. Martin Fowler names its practices: define all configuration in definition files, let the code document the system, keep all of the code in source control, and test the systems and the processes continuously. Nobody adjusts a server by hand, because each hand change risks a snowflake server.
