# Improvement loop

> **In the library:** the suggestion box. A visitor's complaint becomes a written request, a librarian decides on each one, and a request that would help every branch goes back to the original library.

**Status:** Built.

Knowledge that grows only when someone sits down to write it falls behind the work. This layer turns the corrections you already give an agent into small proposals, puts each one in front of you for a decision, and sends the ones that would help any project back to the template. It is three preset skills and one directive on the root. A fourth preset, `evaluate-knowledge`, tests whether the rules you accepted help, and proposes to deprecate the ones that don't: see [Evaluation](evaluation.md).

| Skill               | Who starts it                         | What it does                                                                                 |
| ------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------- |
| `propose-knowledge` | The agent when you correct it, or you | Turns one correction or repeated note into one small proposal that cites it                  |
| `review-proposals`  | You, with `/review-proposals`         | Walks the queue branch by branch, explains each proposal and its effect, and names conflicts |
| `sync-template`     | You, with `/sync-template`            | Pulls template changes, and prepares a rule of yours as a proposal to the template           |

The sources sit in `knowledge/skills/`, so they are nodes like any other: proposed until you accept them, checked on each commit, and open to the same loop. Every project receives all three, whatever disciplines it takes, because they draw only on the governance. `review-proposals` and `sync-template` have `invocation: person`, so their `SKILL.md` carries `disable-model-invocation: true` and the agent can't start them on its own. Claude Code also leaves a skill like that out of its skill listing.

## How the loop runs

1. You correct the agent, a review finds a problem, or the same mistake happens twice.
2. Claude Code's auto memory writes a note right away, so the next session has it.
3. `propose-knowledge` turns the correction or the note into one proposal in a node file.
4. You read the queue with `/review-proposals`, and you accept with `knowledge/.ka/ka accept`.
5. `knowledge/.ka/ka runtime` writes the generated files, and the hook checks them.
6. `/sync-template` offers a rule that would hold in any project to the template.

Nothing in the loop accepts anything for you. Every proposal arrives as `proposed`, and only you move it on.

In the template repo itself, the skills say to use `uv run ka` wherever they name `knowledge/.ka/ka`.

## The root trigger

A skill on its own doesn't start reliably, so the root holds one directive that tells the agent when to use it:

```text
When a person corrects your work, propose the change with `propose-knowledge`.
```

It has `scope: node`, so it sits in `AGENTS.md` and isn't copied into every skill and reference page. Like everything the template ships, it starts as `proposed`, so it doesn't bind the agent until you accept it:

```sh
knowledge/.ka/ka accept propose-corrections
```

Until then, start the skill yourself after a correction, with `/propose-knowledge`.

## What a correction becomes

`propose-knowledge` sorts each signal before it writes anything:

| Signal                                              | What you get                                                       |
| --------------------------------------------------- | ------------------------------------------------------------------ |
| A choice for one task, or a habit of one person     | Nothing. Auto memory keeps it.                                     |
| A fact about the project that stays true            | An edit of a definition, or a line under `## References` in a node |
| The same steps a second time                        | A step in a skill, or a new skill                                  |
| An "always" or a "never", or the same mistake twice | A directive                                                        |
| A "not here" for a rule that applies                | An exception, with your reason                                     |

It writes the smallest change that does the job: an addition or an edit, never a rewrite of a whole node, because repeated rewrites of a context lose detail. Workspace knowledge goes in nodes with `origin: project`. If the project has none yet, the first proposal adds a domain node for the project and a pointer from the root. A rule for every task goes on the root with `scope: node`.

Before it proposes, it reads every `rejected` entity. If you already turned the same idea down, it stops and shows you the reason you gave. It also stops when an open proposal or an accepted rule already says the same thing.

A body edit and a new step in a skill need no review, so they're in force once you commit them. For those, the skill shows you the diff first.

### The citation

Each proposal cites the signal that gave it, in a `## Signals` section at the end of the node body:

```markdown
## Signals

- `use-pnpm`: 2026-11-06, rule. The agent ran `npm install`. The person said that the project always uses `pnpm`.
```

The citation paraphrases the signal and holds no name or email. It doesn't go in `sources`, because `sources` names the evidence for a rule and decides its `basis`. A body change needs no review, so the line reopens nothing, and the skill removes it once you decide.

### Auto memory

Claude Code's auto memory is the inbox. It's on by default, and it writes notes to `~/.claude/projects/<project>/memory/`, outside the repo, for one person on one machine. When a note becomes a proposal, the skill adds a `Proposal: <id>` line to the note.

Each run of the skill starts by tidying up. A note whose proposals you have all accepted or rejected leaves auto memory, with its line in `MEMORY.md`. The citation of every decided proposal leaves its node, whoever wrote it. A personal preference never becomes a proposal, so it stays in auto memory, and the two stores don't compete. A citation of the class `eval` stays while its directive is accepted, because it proposes a deprecation.

## Review the queue

Commit the proposals first, because `ka accept` reads them from the last commit. Then run `/review-proposals`. It lists each branch with its count of nodes, directives, and exceptions, and asks where to start. A branch is the discipline that a node's `broader` chain reaches, or the project's own domain for workspace knowledge. The governance, the skills, and the root each form a branch of their own.

For each proposal it tells you:

- What it tells an agent, in one sentence
- Its effect: where a directive applies, which generated files hold it after acceptance, and what an exception stops
- Its signal, or for template knowledge its `basis` and sources
- Each conflict: two proposals that ask for opposite things, a proposal that contradicts a rule already in force, one that repeats a rejected entity, an exception against a rule you accept in the same round, or a proposal that rests on another one still waiting
- What it recommends

An accepted directive with an `eval` line in `## Signals` joins the queue as a proposal to deprecate it. If you agree, the skill sets it to `deprecated` and removes the eval targets that name it. If you don't, it removes the line.

Then it records your decision:

| Decision | What happens                                                                                                                        |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Accept   | It writes the `knowledge/.ka/ka accept` command with the names you approved, and you run it. The agent doesn't run it for you.      |
| Reject   | It asks for your reason, then writes `status: rejected` and `rejection_reason` in your words, since there's no `ka reject` command. |
| Later    | Nothing changes. The proposal stays `proposed`.                                                                                     |

It then runs `knowledge/.ka/ka runtime`, fixes what the checks report, shows you `git diff`, and asks before it commits. The commit records who decided, and the next run of `propose-knowledge` tidies up the notes and citations of what you decided.

## Send a rule to the template

A rule you accepted in your project may hold for every project. `/sync-template` looks through the rules you accepted for ones that name no path, command, product, or value of your own, fall in a discipline the template covers, and aren't already stated or rejected in the template. You pick which ones go.

For each one, the skill clones the template into a folder outside your project, writes the rule in general words into the node that covers it, as domain knowledge with `status: proposed`, and runs the template's checks in that clone. Then it stops. The change sits uncommitted in the clone, and you commit it and send it the way the template takes changes. The skill doesn't push, and it doesn't open a pull request. A template maintainer reviews the change like any other proposal.

If no practice area of the template covers the rule, the skill tells you to add one with [`author-domain`](seed-knowledge.md#add-a-discipline) and writes nothing. When a later pull brings the rule back as template knowledge, the skill asks whether to deprecate your own copy.

[Migration and reconciliation](migration-and-reconciliation.md#pull-template-changes) covers the pull itself.

## What it does not check yet

- Whether a proposal cites its signal. No check reads `## Signals`, so only the skill's own rule and a reviewer keep a name out of a citation.
- Whether a signal lands in the right class. The skill decides, and you see the result in the diff.
- Whether the agent follows the root trigger, even after you accept it.
- The notes of other people. Auto memory lives with one person on one machine, so the tidy-up reaches only the notes of whoever runs the skill.
- Whether a rule sent to the template really holds for every project. The template's reviewer decides.

## What only a real session can show

The skills have been followed step by step in temporary projects, with memory notes planted for the test, by the agent that wrote them. Only real sessions can confirm:

- That an agent picks `propose-knowledge` when you correct it, with the root trigger and without it.
- How auto memory behaves when `AGENTS.md` already holds the same rule. The Claude Code docs say that auto memory skips what `CLAUDE.md` already says.
- That an agent finds the right node for a proposal in a large tree.
- How the review works with a person who answers live, and with a queue of hundreds of entities after a fresh install.
