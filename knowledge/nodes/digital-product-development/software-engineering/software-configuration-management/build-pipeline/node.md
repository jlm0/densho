---
id: build-pipeline
kind: densho:Concept
title: Build pipeline
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://martinfowler.com/articles/continuousIntegration.html
  - https://martinfowler.com/bliki/DeploymentPipeline.html
broader:
  - software-configuration-management
informs:
  - semantic-versioning
---

## Definition

The automated build that runs on each change to a repository. Martin Fowler's continuous integration makes the build self-testing, and each push to the mainline triggers a build. A deployment pipeline breaks the build into stages. Early stages find most problems and give fast feedback. Later stages give slower and more thorough probing.
