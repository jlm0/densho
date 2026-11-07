<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Code coverage

## Directives

No directive is in force at this node.

## Definition

A measure of the degree to which a test suite exercises the code of a system. Ivanković and colleagues give this definition in "Code Coverage at Google". The ISTQB Foundation Level syllabus treats it as the target of the white-box test techniques: statement coverage is the share of the executable statements that the tests exercise, and branch coverage is the share of the branches. SWEBOK v4 names stronger criteria, such as condition, MC/DC, path, and data flow coverage.

## Notes

The coverage criteria form a ladder. Branch coverage subsumes statement coverage: a test set with `100%` branch coverage also has `100%` statement coverage, but not the other way round. SWEBOK v4 names stronger control flow criteria, such as condition, decision, and MC/DC coverage, and path coverage at the top. Loops make full path coverage infeasible, so the weaker criteria limit the loop iterations. Data flow criteria follow each variable from its definition to its use.

Coverage shows which code ran, not whether a test checked its result. A test can execute a line without an assertion on it. A statement with a data-dependent defect, such as a division by zero, can run without a failure. Code that does not implement a requirement has no line to cover, so white-box testing misses defects of omission. Mutation testing checks whether the tests detect a change in the covered code.

The Google Testing Blog gives rough guidelines: `60%` is acceptable, `75%` is commendable, and `90%` is exemplary. It states that a project-wide target above `90%` is most likely not worth the cost, while a target of `99%` for each commit is reasonable. Software Engineering at Google warns that a fixed target such as `80%` turns into a ceiling. The 2 Google sources differ on the scope of the measure. The book measures coverage only from small tests, to avoid inflation. The blog adds the coverage of the integration and end-to-end tests, and warns that part of it is incidental.
