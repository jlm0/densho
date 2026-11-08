---
id: review-code-change
kind: densho:Skill
title: Review a code change
status: proposed
origin: template
knowledge_type: domain
description: Review a code change for its design, its behavior, its tests, and its security. Use when a code change is ready for review.
invocation: agent
skill_type: lens
uses:
  - code-review
  - test-pyramid
  - software-security
  - access-control
  - injection
pointers:
  - kind: densho:TextPointer
    target: code-review
    trigger: You judge whether the change is ready to merge.
  - kind: densho:TextPointer
    target: software-testing
    trigger: You judge the tests of the change.
  - kind: densho:TextPointer
    target: software-security
    trigger: The change handles a password, a session, an error, or a connection.
  - kind: densho:TextPointer
    target: access-control
    trigger: The change reads or changes data for a user.
  - kind: densho:TextPointer
    target: injection
    trigger: The change passes input to a query, a command, or an output.
---

## Directives

- If you review only part of a change, state which parts you reviewed. ^state-the-reviewed-parts
  - scope: node
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html

## Inputs

- The change: its diff and its description
- The code around the change, and the style guide of the project if it has one
- The result of the tests on the change, if the project ran them

## Procedure

1. Read each directive that this skill lists.
2. Read the description, and state the purpose of the change in one sentence.
3. Check that the change has one purpose and a size that a reviewer reads in one session.
4. Read each human-written line. Check the design, the behavior on edge cases and under concurrency, and each part that the change does not need.
5. Check that each change in behavior has a test, and that each test fails when its code breaks.
6. Check each input, each access check, and each secret that the change touches.
7. Check the names, the comments, the style, and the docs.
8. Write each finding with the directive that it breaks, its label, and the change that you recommend.
9. Approve the change, or ask for changes, from the directives on the health of the code.

## Output

A list of findings and a decision. Each finding names the file and the line, the directive that it breaks, its label, and the change that you recommend. The decision approves the change or asks for changes.

## Validation

Each finding names a directive from the first step of the procedure. A finding with no directive is an opinion, so label it `Optional:` or `FYI:`.
