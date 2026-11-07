# Language checks

> **In the library:** the copy editor. A book can sit on the right shelf and still have rules that nobody can apply the same way twice, so the editor checks how each sentence is written.

**Status:** Built.

This layer checks the text that agents act on: directives, pointer triggers, and skill descriptions. The grammar and the vocabularies are data in `knowledge/governance/language/`, and the code is in `engine/language/`.

The checks judge form only. A rule can pass every check and still be a bad rule, so meaning stays a matter for review. See [what a pass does not mean](#what-a-pass-does-not-mean).

## Run the checks

```sh
uv run densho language
```

The command reads `knowledge/` in the current folder, or in a folder you name after `language`. It also lints each rule in `knowledge/governance/language/grammar.yaml` as a directive. Each problem prints as `path:line: code: message`, and any problem makes the command exit with status 1. A node that fails to parse stops the checks, as it does for the [graph checks](graph-checks.md).

The git hook runs the same command when a commit touches `knowledge/`, `engine/`, or `uv.lock`. A commit that changes only docs or tests skips it. So does a commit that only deletes files, so a branch vocabulary left behind by a deleted node fails on the next run, not on that commit.

## Directives

A directive is one instruction in one sentence:

```text
Run `pytest` before you commit.
Do not commit a secret.
If a test fails, stop the release.
In `tests/`, use a fixture for each database.
Prefer a small fixture over a large mock.
```

The grammar has these rules:

- Write each rule as one sentence that ends with a period, in 20 words or fewer. A code span counts as one word.
- Start with an approved verb, `Do not`, `Prefer`, a condition, or a scope. Follow `Do not` with an approved verb.
- After a condition or a scope, put a comma before the directive.
- Write one directive, with at most one condition and one `unless`.
- Do not use a modal, a hedge, a vague qualifier, or a reason marker. The [vocabulary](#vocabularies) lists them.
- Put each command, path, and literal value in backticks. A number counts as a literal value, so write `` `30` `` and not 30.
- Do not repeat a rule anywhere in the tree, or a rule in `grammar.yaml`. If a second node needs a rule, use `also_attached_to`.

## Pointer triggers

A trigger tells an agent when to follow a pointer. It states a condition, so it reads as a plain clause with a subject and a present-tense verb:

```text
You edit a test file.
The build fails.
`pytest` fails.
A file is open.
```

A trigger does not start with `When` or `If`, and it does not give an instruction. It has no second condition, so `You edit a file when the build fails.` fails. It is one sentence of 20 words or fewer, and it follows the same vocabulary, literal, and STE rules as a directive.

## Skill descriptions

An agent reads a description to choose a skill, and the harness may cut it short, so each description has a fixed shape and a length limit:

```text
Review a pull request for correctness. Use when a pull request changes code.
```

The first sentence starts with an approved verb and says what the skill does. The second starts with `Use when` and follows the trigger grammar. Each sentence has at most 20 words.

Three limits apply:

| Limit                 | Value            | Why                                                                                                     |
| --------------------- | ---------------- | ------------------------------------------------------------------------------------------------------- |
| One description       | 400 characters   | Leaves room for about 20 skills in the listing. A project can change it in `grammar.yaml`.              |
| Most it can be raised | 1,536 characters | Claude Code cuts each listing entry at this length, so the engine refuses a higher limit.               |
| The whole listing     | 8,000 characters | IDs and descriptions together. Claude Code budgets 1% of the context window, about this on 200K tokens. |

The 8,000 is an estimate at four characters per token. Claude Code drops the descriptions of the least-used skills when a listing overflows, and the names stay.

## What fails

| Code                 | What fails                                                                       |
| -------------------- | -------------------------------------------------------------------------------- |
| `sentence`           | No capital at the start, no single period at the end, or more than one sentence  |
| `word-count`         | Too many words in a sentence, or a text over 2,000 characters                    |
| `opening`            | A rule that does not start the way the grammar allows, or a missing comma        |
| `imperative`         | A sentence that reads as a statement, such as `Test files pass.`                 |
| `second-directive`   | A second action joined to the first, such as `Run the tests and stop the build.` |
| `condition-count`    | Too many condition clauses in a rule, or any second condition in a trigger       |
| `unless-count`       | Too many uses of `unless` in a rule                                              |
| `prohibited`         | A term that the vocabulary prohibits for this node                               |
| `literal`            | A word that looks like a command, a path, or a value, outside backticks          |
| `duplicate-rule`     | The same rule text as an earlier rule, ignoring case and spacing                 |
| `ste`                | A hard finding from the STE linter, such as a semicolon or a phrasal verb        |
| `trigger-form`       | A trigger that is not a present-tense clause that starts with its subject        |
| `description-form`   | A description without its two sentences, in their order                          |
| `description-length` | A description over the limit for one description                                 |
| `listing-budget`     | A listing over the budget. The problem points at the skill that crosses it.      |
| `vocabulary-branch`  | A branch vocabulary whose file name is not the ID of a node                      |
| `language-profile`   | A grammar or vocabulary file that cannot be read or breaks its format            |

## Vocabularies

`knowledge/governance/language/vocabulary.yaml` is the base vocabulary for every node:

```yaml
approved_verbs: [add, apply, approve]
prohibited:
  modal: [can, should]
  hedge: [usually]
```

`approved_verbs` lists the verbs that can open a directive or a description. The check applies only to that opening verb, not to every verb in the sentence. The list is this project's own, not the ASD-STE100 dictionary.

`prohibited` groups terms by a label that you choose, and the label appears in the message. A term can be a phrase. A single word also matches its inflected forms when it is used as a verb, so `utilize` catches `utilized`.

A branch of the tree can extend this. Add `knowledge/governance/language/branches/<node-id>.yaml`, in the same format, and it applies to that node and to every node under it through `broader`:

- A branch only adds. It can approve a verb or prohibit a term, but it cannot lift a prohibition from above.
- A prohibition wins over an approval, so a branch can forbid a verb that the base approves.
- A node with several `broader` parents gets the vocabulary of each of them.
- A skill has no `broader` edge, so it takes the vocabulary of each node in `uses` instead, along with its own branch file. That gives its text the same language as the knowledge it draws on.
- A directive uses the vocabulary of the node that holds it, even when `also_attached_to` attaches it elsewhere.

## What a pass does not mean

A check can decide form. It cannot decide meaning. Each rule in `knowledge/governance/language/grammar.yaml` lists the checks that enforce it, and `review: true` marks a rule that needs a human review as well:

| Rule                                         | A check catches                   | Review still decides                                  |
| -------------------------------------------- | --------------------------------- | ----------------------------------------------------- |
| One directive in each rule                   | A second verb joined to the first | Whether the sentence truly holds one directive        |
| At most one condition                        | A second condition clause         | A condition inside a phrase, such as `before a merge` |
| No modal, hedge, or vague qualifier          | The terms on the list             | Any vague wording that is not on the list             |
| No reason or explanation                     | Markers such as `because`         | A reason with no marker                               |
| Literals in backticks                        | Words with the shape of a literal | A plain word that is a command, such as `pytest`      |
| Do not repeat a rule                         | Exact repeats                     | The same rule in other words                          |
| No violation of ASD-STE100                   | The hard findings of the linter   | Whether the text follows the standard's intent        |
| An observable condition, a concrete object   | Nothing                           | All of it                                             |
| `Prefer` only for a default with a deviation | Nothing                           | All of it                                             |

## How it works

Each text goes through two stages. The first reads its Markdown, replaces each code span with a placeholder, and runs the form checks with regular expressions and the word lists. The second uses spaCy with the `en_core_web_sm` model to find the subject, the verbs, and the condition clauses, and to match the prohibited terms. Structure checks run only on a text that passed the form checks, so one broken sentence gives one clear report.

The STE findings come from a vendored copy of `ste-lint.py` in `engine/vendor/`, kept byte for byte with its license. Its advisory findings, passive voice and the present perfect, do not fail a check. The grammar's word limit replaces its sentence limit.

spaCy loads only when there is text to check, and the rules in `grammar.yaml` count as text. It adds about half a second to the run. A commit that touches none of the paths above does not run the hook.

The model is statistical, so it can misread a sentence, and the checks lean toward letting a sentence through, because a false failure blocks a commit:

- It often reads the last word of `The build passes.` as a plural noun. The check accepts that shape when the sentence has a determiner, which means a fragment such as `The test files.` also passes.
- It can read the opening verb as a noun, so `Group fields by task.` looks like a group that fields something. A one-word subject therefore makes a statement only when the verb can't be read as a plural noun. The check asks the WordNet noun list that ships in the spaCy model. So `Build fails.` fails, because no noun is spelled `fails`, but `Place labels near the field.` passes. A verb that is also a noun still slips through: `Build passes.` passes.
- It can make a later word the main word of the sentence, as in `` Limit progressive disclosure to `2` levels. `` The check then reports a second action only if a comma, a colon, `then`, `and`, or `or` stands before that word, and the word reads as a verb in its base form. After an opening condition such as `If a test fails,`, it starts from the directive verb, not from the verb of the condition.
- A noun in a list can still read as a second action. `Give a pause or stop control to each audio.` fails, because the model reads `stop` as a verb. Reword the list, or split the rule.

If a good sentence still fails a structure check, reword it.

## How it fits

Governance rules are directives too, so a node under `knowledge/governance/` goes through these checks like any other, and so does each rule in `grammar.yaml`. That makes the system recursive: the rules for writing rules follow their own rules. The `language-rules` [policy](governance-workflow.md#the-policies) names these files as its sources.

## What it does not check yet

- Meaning. No automated semantic review exists yet. See the table above.
- Verbs other than the opening verb of a directive or a description
- A command with no mark of one, such as the word `pytest` outside backticks
- The `reason` of a directive exception. See [directive semantics](directive-semantics.md).
- A rule repeated in other words
