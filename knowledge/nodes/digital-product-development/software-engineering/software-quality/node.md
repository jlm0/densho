---
id: software-quality
kind: densho:PracticeArea
title: Software quality
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.computer.org/education/bodies-of-knowledge/software-engineering
  - https://www.iso.org/standard/78176.html
broader:
  - software-engineering
informs:
  - software-operations
  - documentation
pointers:
  - kind: densho:TextPointer
    target: code-review
    trigger: You review a change or prepare a change for review.
  - kind: densho:TextPointer
    target: yagni
    trigger: A change adds a capability for a future need.
  - kind: densho:TextPointer
    target: root-cause-analysis
    trigger: You look for the cause of a bug or an incident.
  - kind: densho:TextPointer
    target: acceptance-testing
    trigger: You verify a change against its acceptance scenarios.
  - kind: densho:TextPointer
    target: exploratory-testing
    trigger: You test a user journey without a script.
  - kind: densho:TextPointer
    target: definition-of-done
    trigger: You decide whether a change is complete.
---

## Definition

The degree to which software meets its requirements and the needs of the people who use it. SWEBOK `v4` makes software quality a knowledge area. ISO/IEC 25010 sets the product quality model: the characteristics against which a team specifies and evaluates the quality of software. Here, quality covers the review of a change, the search for the cause of each defect, and the acceptance of the work.
