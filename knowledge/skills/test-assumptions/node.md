---
id: test-assumptions
kind: densho:Skill
title: Test the assumptions of an idea
status: proposed
origin: template
knowledge_type: domain
description: "List the assumptions of a product idea, and write a test for the riskiest ones. Use when you plan or read a test of a product idea. Do not use it for a usability test (`research-users`)."
invocation: agent
skill_type: task
uses:
  - assumption-testing
steps:
  - test-the-assumptions
---

## Exit checklist

Check each line before you report the tests as done.

- [ ] Each idea has a test for its riskiest assumption.
- [ ] Each test names `1` assumption and the result that counts as a pass.
- [ ] The report names each directive that the tests miss, and the missing rule that the tests reached.

## Output

- A table of the assumption tests: the idea, the assumption, its type, the test, and the result that counts as a pass
- A list of each directive that the tests miss, with the reason

To order the ideas that pass their tests, run `prioritize-work`.
