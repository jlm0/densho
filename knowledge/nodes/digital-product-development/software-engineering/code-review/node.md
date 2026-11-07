---
id: code-review
kind: densho:PracticeArea
title: Code review
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://google.github.io/eng-practices/review/reviewer/standard.html
  - https://google.github.io/eng-practices/review/reviewer/looking-for.html
  - https://google.github.io/eng-practices/review/reviewer/comments.html
  - https://google.github.io/eng-practices/review/developer/small-cls.html
  - https://google.github.io/eng-practices/review/developer/cl-descriptions.html
broader:
  - software-engineering
related:
  - trunk-based-development
---

## Definition

The reading of a change by a person other than its author before the change merges. A change is one commit or one pull request that a reviewer reads as a unit. The review keeps the overall health of the code improving over time. It checks the design, the behavior, the complexity, the tests, the names, the comments, the style, and the docs of the change.

## Directives

- Approve a change once it improves the overall health of the code, unless it adds an unwanted feature. ^approve-on-improvement
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/standard.html
- Do not approve a change that makes the health of the code worse. ^reject-worse-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/standard.html
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Read each human-written line of a change before you approve it. ^read-every-line
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Check that each test in a change fails when the code under test breaks. ^tests-fail-on-breakage
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Write each review comment about the code, not about its author. ^comment-on-the-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/comments.html
- State the reason for each review comment. ^explain-each-comment
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/comments.html
- Label each optional review comment with `Nit:`, `Optional:`, or `FYI:`. ^label-comment-severity
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/comments.html
  - sources: https://google.github.io/eng-practices/review/reviewer/standard.html
- When a reviewer asks what code does, make the code clearer instead of replying only in the review. ^clarify-the-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/comments.html
- Limit each change to one self-contained purpose. ^one-purpose-per-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/developer/small-cls.html
- Split a change of `1000` or more changed lines, unless a tool generated it. ^split-large-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/developer/small-cls.html
- Keep a refactor or a reformat in a separate change from a change in behavior. ^separate-refactors
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/developer/small-cls.html
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Write the first line of each change description as a short imperative sentence. ^imperative-first-line
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
- State the problem and the reason for the approach in each change description. ^explain-each-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
- Write each code comment to explain why the code exists, not what it does. ^comments-explain-why
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- When a change affects how to build, test, or release the code, update the docs in the same change. ^update-docs-with-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://google.github.io/eng-practices/review/reviewer/looking-for.html

## Notes

The source is the code review guide of Google engineering practices, which calls a change a CL. About `100` changed lines is a reasonable size for one change. A small cleanup, such as the rename of a local variable, can stay in a change in behavior. With Conventional Commits, the type comes first, and the imperative summary follows the colon.
