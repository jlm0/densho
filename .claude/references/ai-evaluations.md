<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# AI evaluations

## Directives

No directive is in force at this node.

## Definition

A test of an AI system: the test gives the system an input, and applies grading logic to its output to measure success. Anthropic's engineering post on evals for AI agents gives this definition, and names the parts: a task with defined inputs and success criteria, a trial for each attempt, a grader that scores the result, the transcript of each trial, and the outcome in the environment. Anthropic's guide on success criteria starts from criteria that are specific and measurable, and builds evals that mirror the real distribution of tasks. SWEBOK v4 lists the testing of AI and machine learning systems as an emerging area, with offline testing before deployment and online testing after it.

## Notes

Anthropic names 3 types of grader:

- A code-based grader is the fastest and the most reliable, and it scales. It includes string matches, binary tests, static analysis, and checks of the tool calls. It is brittle to valid variations of an answer.
- A model-based grader, or LLM grader, is fast, flexible, and suitable for complex judgment. It needs calibration with human graders.
- A human grader is the most flexible and gives high quality, but it is slow and expensive. Anthropic keeps systematic human studies for the calibration of LLM graders.

A task can combine graders. Its score can be weighted, binary, or a hybrid of the 2.

Agent behavior varies between runs, so 1 trial gives a noisy result. `pass@k` is the chance of at least 1 success in k trials, and it rises with k. `pass^k` is the chance that each of k trials succeeds, and it falls with k. With a `75%` success rate per trial, `pass^3` is about `42%`. A tool where 1 success is enough uses `pass@k`. A customer-facing agent uses `pass^k`.

A capability eval asks what the agent can do well, and starts at a low pass rate. A regression eval asks whether the agent still handles the tasks that it handled before. A capability eval at `100%` gives no signal for improvement. After the agent launches, a capability eval with a high pass rate can move to the regression suite.

Grading defects can hide a capable agent. Anthropic reports a benchmark where a model first scored `42%`. A researcher found rigid grading, ambiguous tasks, and tasks that no run could reproduce exactly. After the fixes and a less constrained scaffold, the score rose to `95%`. With frontier models, a pass rate of `0%` across many trials is most often a sign of a broken task, not of an incapable agent.

Automated evals are 1 layer among several: production monitoring, A/B tests, user feedback, transcript review, and human studies. Each layer catches failures that the others miss.
