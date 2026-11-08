---
id: ai-evaluations
kind: densho:Concept
title: AI evaluations
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=142
broader:
  - software-testing
---

## Definition

A test of an AI system: the test gives the system an input, and applies grading logic to its output to measure success. Anthropic's engineering post on evals for AI agents gives this definition, and names the parts: a task with defined inputs and success criteria, a trial for each attempt, a grader that scores the result, the transcript of each trial, and the outcome in the environment. Anthropic's guide on success criteria starts from criteria that are specific and measurable, and builds evals that mirror the real distribution of tasks. SWEBOK v4 lists the testing of AI and machine learning systems as an emerging area, with offline testing before deployment and online testing after it.

## Directives

- Define each success criterion of an AI feature as a named metric, a threshold, and its test set. ^specific-success-criteria
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#define-your-success-criteria
- Set each success target from a benchmark, a prior experiment, or expert knowledge. ^achievable-success-targets
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#define-your-success-criteria
- Define success criteria for each dimension of the feature, such as task fidelity, consistency, latency, and price. ^multidimensional-success-criteria
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#common-success-criteria
- Make the eval tasks match the real distribution of tasks, including the edge cases. ^real-task-distribution
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#eval-design-principles
- Start the eval suite with `20` to `50` tasks from manual checks, common user tasks, and failure reports from production. ^tasks-from-real-failures
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- Make each eval task specific enough that `2` domain experts give it the same verdict. ^unambiguous-eval-tasks
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- State in the task description each condition that the grader checks. ^grader-checks-in-the-task
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- Write a reference solution for each eval task that passes each grader. ^reference-solutions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- Include tasks that require a behavior and tasks that prohibit it in each eval suite. ^balanced-eval-suites
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- Make the agent in the eval behave like the agent in production. ^production-like-agent
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- Start each trial from a clean environment with no state from other trials. ^isolated-trials
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- Run more than `1` trial of each eval task. ^multiple-trials
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#the-structure-of-an-evaluation
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#how-to-think-about-non-determinism-in-evaluations-for-agents
- If the product requires consistent behavior on each attempt, measure `pass^k`, not `pass@k`. ^pass-power-k-for-consistency
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#how-to-think-about-non-determinism-in-evaluations-for-agents
- If the product accepts `1` success in `k` attempts, measure `pass@k`. ^pass-at-k-for-one-success
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#how-to-think-about-non-determinism-in-evaluations-for-agents
- Use a code-based grader for each eval result, unless the result has valid variations that no code check matches. ^code-graders-first
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#grade-your-evaluations
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- If an eval result has valid variations that no code check matches, use an LLM grader, not a human grader. ^llm-grader-for-complex-judgment
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#grade-your-evaluations
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- Choose more test cases with automated grading, not fewer test cases with human grading. ^volume-over-hand-grading
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#eval-design-principles
- Check the outcome of each trial, not the order of its tool calls. ^check-the-outcome
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- For a task with more than `1` component, give partial credit for each component. ^partial-credit
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- Give each LLM grader a rubric that states each pass condition, and a fixed scale, such as `correct` or `incorrect`. ^rubrics-for-llm-graders
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#tips-for-llm-based-grading
- Use a separate LLM grader for each dimension of a task. ^one-llm-grader-per-dimension
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- Give each LLM grader an option to return `Unknown` when it lacks information. ^unknown-option-for-llm-graders
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- Make each LLM grader reason before it gives a score. ^reasoning-before-grades
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#tips-for-llm-based-grading
- Use a different model for the LLM grader than the model that generated the output. ^separate-grader-model
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#example-evals
- Before you use an LLM grader at scale, compare its grades with the grades of human experts. ^compare-llm-graders-with-experts
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
  - sources: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests#grade-your-evaluations
- Make each grader reject a result that exploits a loophole in place of a solution of the task. ^bypass-resistant-graders
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#design-the-eval-harness-and-graders
- In an eval of a coding agent, check correctness with unit tests and code quality with an LLM rubric. ^tests-for-coding-agents
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#evaluating-coding-agents
- Read a sample of the transcripts before you accept an eval score. ^read-transcripts
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#maintain-and-use-the-eval-long-term
- If a frontier model fails each of `100` trials of a task, check the task and its graders for defects. ^zero-pass-rate-is-a-broken-task
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- If a grader rejects a valid solution or `2` domain experts disagree on a task verdict, change the eval. ^fix-unfair-evals
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#maintain-and-use-the-eval-long-term
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
- Monitor each capability eval for saturation. ^monitor-eval-saturation
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#maintain-and-use-the-eval-long-term
- Keep the capability evals and the regression evals in separate suites. ^separate-capability-and-regression
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#capability-vs-regression-evals
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#why-build-evaluations
- Treat each decrease in the pass rate of a regression eval as a defect. ^regression-eval-pass-rate
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#capability-vs-regression-evals
- After the agent launches, move each capability eval that reaches a `100%` pass rate into the regression suite. ^graduate-capability-evals
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#capability-vs-regression-evals
- Write the evals for a planned capability before the agent performs it. ^evals-before-capabilities
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#maintain-and-use-the-eval-long-term
- Add the failures that users report to the eval suite as tasks, first those with the highest impact. ^failures-into-eval-tasks
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#collect-tasks-for-the-initial-eval-dataset
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#conclusion
- Run the automated evals on each change of the agent and on each model upgrade. ^evals-on-each-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#how-evals-fit-with-other-methods-for-a-holistic-understanding-of-agents
- Combine the automated evals with production monitoring and periodic human review. ^combine-evaluation-methods
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#how-evals-fit-with-other-methods-for-a-holistic-understanding-of-agents
- Assign an owner to the infrastructure of the eval suites. ^owner-for-eval-infrastructure
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents#maintain-and-use-the-eval-long-term
- Before you deploy a model, test it offline against its required conditions, such as with cross-validation. ^offline-tests-before-deployment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=142
- After you deploy a model, test it online to check how it interacts with the behavior of its users. ^online-tests-after-deployment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=142

## Notes

Anthropic names 3 types of grader:

- A code-based grader is the fastest and the most reliable, and it scales. It includes string matches, binary tests, static analysis, and checks of the tool calls. It is brittle to valid variations of an answer.
- A model-based grader, or LLM grader, is fast, flexible, and suitable for complex judgment. It needs calibration with human graders.
- A human grader is the most flexible and gives high quality, but it is slow and expensive. Anthropic uses human graders to calibrate LLM graders.

A task can combine graders. Its score can be weighted, binary, or a hybrid of the 2.

Agent behavior varies between runs, so 1 trial gives a noisy result. `pass@k` is the chance of at least 1 success in k trials, and it rises with k. `pass^k` is the chance that each of k trials succeeds, and it falls with k. With a `75%` success rate per trial, `pass^3` is about `42%`. A tool where 1 success is enough uses `pass@k`. A customer-facing agent uses `pass^k`.

A capability eval asks what the agent can do well, and starts at a low pass rate. A regression eval asks whether the agent still handles the tasks that it handled before. A capability eval at `100%` gives no signal for improvement. After the agent launches, a capability eval with a high pass rate can move to the regression suite.

Grading defects can hide a capable agent. Anthropic reports a benchmark where a model first scored `42%`. A researcher found rigid grading, ambiguous tasks, and tasks that no run could reproduce exactly. After the fixes and a less constrained scaffold, the score rose to `95%`. With frontier models, a pass rate of `0%` across many trials is most often a sign of a broken task, not of an incapable agent.

Automated evals are 1 layer among several: production monitoring, A/B tests, user feedback, transcript review, and human studies. Each layer catches failures that the others miss.
