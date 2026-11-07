---
id: ai-evaluations
kind: densho:Concept
title: AI evaluations
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
broader:
  - software-testing
---

## Definition

A set of graded test cases that measures how an AI feature performs against its success criteria. Anthropic's guide starts from success criteria that are specific and measurable, and then builds evaluations that mirror the real distribution of tasks, edge cases included. It prefers automated grading, such as an exact match, a code-graded check, or an LLM-graded check, and more test cases with automated grading over fewer test cases that a person grades.
