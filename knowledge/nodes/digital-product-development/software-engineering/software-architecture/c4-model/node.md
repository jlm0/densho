---
id: c4-model
kind: densho:Concept
title: C4 model
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://c4model.com/
  - https://c4model.com/abstractions
  - https://c4model.com/abstractions/container
  - https://c4model.com/diagrams/notation
broader:
  - software-architecture
---

## Definition

A set of abstractions and diagrams for software architecture by Simon Brown. People use software systems. A software system holds containers, a container holds components, and code implements each component. A container is an application or a data store that must run for the system to work. It is not a Docker container. The four core diagrams follow the same levels: the system context, the containers, the components, and the code.

## Directives

- Give each architecture diagram a title that states its type and its scope. ^diagram-title
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://c4model.com/diagrams/notation
- Give each architecture diagram a key for its shapes, colors, borders, and lines. ^diagram-key
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://c4model.com/diagrams/notation
- Label each element of an architecture diagram with its type and a short description. ^label-diagram-elements
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://c4model.com/diagrams/notation
- Label each line in an architecture diagram with the purpose of its relationship. ^label-diagram-lines
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://c4model.com/diagrams/notation
- Name the technology of each container and each component in an architecture diagram. ^name-diagram-technology
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://c4model.com/diagrams/notation

## Notes

The C4 model sets no notation. Each line shows a relationship in one direction. A label such as `Uses` says too little, so the label names what flows or what depends.
