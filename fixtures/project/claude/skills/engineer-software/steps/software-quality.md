<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software quality

This file is step 7 of 8 of the skill `engineer-software`. If compaction cuts this file, read it again.

## Directives

From [Code review](../../../references/code-review.md):

- Approve a change once it improves the overall health of the code, unless it adds an unwanted feature. ^approve-on-improvement
- When a reviewer asks what code does, make the code clearer instead of replying only in the review. ^clarify-the-code
- Write each review comment about the code, not about its author. ^comment-on-the-code
- Write each code comment to explain why the code exists, not what it does. ^comments-explain-why
- State the problem and the reason for the approach in each change description. ^explain-each-change
- State the reason for each review comment. ^explain-each-comment
- Write the first line of each change description as a short imperative sentence. ^imperative-first-line
- Label each optional review comment with `Nit:`, `Optional:`, or `FYI:`. ^label-comment-severity
- Limit each change to one self-contained purpose. ^one-purpose-per-change
- Read each human-written line of a change before you approve it. ^read-every-line
- Do not approve a change that makes the health of the code worse. ^reject-worse-code
- Keep a refactor or a reformat in a separate change from a change in behavior. ^separate-refactors
- Split a change of `1000` or more changed lines, unless a tool generated it. ^split-large-change
- Check that each test in a change fails when the code under test breaks. ^tests-fail-on-breakage
- When a change affects how to build, test, or release the code, update the docs in the same change. ^update-docs-with-change

## Inputs

- The change, with its requirements and its tests

The output of each node in this list is an input of this step:

- [Software configuration management](software-configuration-management.md)

## Procedure

1. Run the skill `review-code-change` on the change.

The rest of the procedure of this step is missing.

## Output

The review of the change, the cause of each defect, and the decision to accept the work or not.

The output of this step is an input of each node in this list:

- [Documentation](../../../references/documentation.md)
- [Software operations](software-operations.md)

## Exit gate

Check the review and the acceptance against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Software operations](software-operations.md).

## References

- You verify a change against its acceptance scenarios. Read [Acceptance testing](../../../references/acceptance-testing.md).
- You review a change or prepare a change for review. Read [Code review](../../../references/code-review.md).
- You decide whether a change is complete. Read [Definition of done](../../../references/definition-of-done.md).
- You test a user journey without a script. Read [Exploratory testing](../../../references/exploratory-testing.md).
- You look for the cause of a bug or an incident. Read [Root cause analysis](../../../references/root-cause-analysis.md).
- A change adds a capability for a future need. Read [YAGNI](../../../references/yagni.md).
