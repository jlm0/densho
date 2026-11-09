---
id: code-coverage
kind: densho:Concept
title: Code coverage
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://storage.googleapis.com/gweb-research2023-media/pubtools/5172.pdf
  - https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
  - https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=42
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=128
  - https://abseil.io/resources/swe-book/html/ch11.html#a_note_on_code_coverage
broader:
  - software-testing
---

## Definition

A measure of the degree to which a test suite exercises the code of a system. Ivanković and colleagues give this definition in "Code Coverage at Google". The ISTQB Foundation Level syllabus treats it as the target of the white-box test techniques: statement coverage is the share of the executable statements that the tests exercise, and branch coverage is the share of the branches. SWEBOK v4 names further criteria, such as condition, MC/DC, path, and data flow coverage.

## Directives

- Measure branch coverage, not only statement coverage. ^measure-branch-coverage
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=43
- In safety-critical or mission-critical code, use a coverage criterion more rigorous than branch coverage. ^stronger-criteria-for-critical-code
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=42
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=129
- Measure the coverage automatically for each change in code review and for each project. ^measure-coverage-automatically
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/5172.pdf#page=8
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/5172.pdf#page=3
- Show the coverage of each changed line in the code review of the change. ^coverage-in-code-review
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://storage.googleapis.com/gweb-research2023-media/pubtools/5172.pdf#page=1
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Use the coverage report to find the code that no test executes. ^find-untested-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- In a code review, review the risk of each changed line that no test executes. ^review-uncovered-lines
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Set the coverage target of a code base at `90%` or less, by its business impact, change rate, and lifetime. ^target-by-impact-and-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- If the team sets a coverage goal for each commit, set its lower threshold at `90%` or more. ^per-commit-coverage-floor
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Make the coverage of the changed lines of each commit meet its per-commit coverage goal. ^cover-changing-code
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- When you change a file with coverage below the target of its code base, raise its coverage. ^raise-coverage-on-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Exclude each infeasible path from the target of path coverage. ^exclude-infeasible-paths
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=121
- Block a change when it drops the coverage below the gate that the team chose. ^coverage-gate
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Treat a coverage target as a floor, not as a ceiling. ^target-is-a-floor
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#a_note_on_code_coverage
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Do not treat a high coverage percent as proof that the tests check the behavior. ^coverage-is-not-quality
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://abseil.io/resources/swe-book/html/ch11.html#a_note_on_code_coverage
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=42
- Do not add a copied test or a test without an assertion only to reach a coverage target. ^no-tests-for-the-number
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Do not treat full code coverage as proof that the code implements each requirement. ^coverage-misses-omissions
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf#page=43

## Notes

Branch coverage subsumes statement coverage: a test set with `100%` branch coverage also has `100%` statement coverage, but not the other way round. SWEBOK v4 also names condition, decision, and MC/DC coverage, and calls path coverage the strongest control flow criterion. Loops make full path coverage infeasible, so the less stringent criteria limit the loop iterations. Data flow criteria follow each variable from its definition to its use.

Coverage shows which code ran, not whether a test checked its result. A test can execute a line without an assertion on it. A statement with a data-dependent defect, such as a division by zero, can run without a failure. Code that does not implement a requirement has no line to cover, so white-box testing can miss defects of omission. Mutation testing checks whether the tests detect a change in the covered code.

The Google Testing Blog gives rough guidelines: `60%` is acceptable, `75%` is commendable, and `90%` is exemplary. It states that a project-wide target above `90%` is most likely not worth the cost, while a target of `99%` for each commit is reasonable. Software Engineering at Google warns that a fixed target such as `80%` turns into a ceiling. The 2 Google sources differ on the scope of the measure. The book measures coverage only from small tests, to avoid inflation. The blog adds the coverage of the integration and end-to-end tests, and warns that part of it is incidental.
