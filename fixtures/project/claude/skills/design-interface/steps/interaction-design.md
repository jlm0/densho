<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Interaction design

This file is step 2 of 4 of the skill `design-interface`. If compaction cuts this file, read it again.

## Directives

From [Fitts's law](../../../references/fitts-law.md):

- Make the text label of each icon button part of its target area. ^label-in-target
- Show the options of a menu next to the control that opens it. ^menu-near-its-control
- Place controls that users press in sequence close to each other. ^sequence-targets-close
- Leave visible space between each pair of adjacent targets. ^space-between-targets
- Place the submit button of a form next to its last field. ^submit-near-last-field
- Make the visible area of each target as large as its active area. ^visible-target-matches-active

From [Hick's law](../../../references/hicks-law.md):

- Mark the recommended option when a step asks the user to choose between options of equal rank. ^mark-recommended-option
- Show a new user the features of a product one at a time. ^show-features-one-at-a-time

From [Progressive disclosure](../../../references/progressive-disclosure.md):

- Keep each disclosure control visible on the first screen. ^keep-disclosure-control-visible
- Name the hidden content in the label of each disclosure control. ^label-disclosure-control
- Limit progressive disclosure to `2` levels. ^limit-disclosure-levels
- Move each advanced or rarely used option to a secondary screen. ^move-advanced-options
- Give the secondary options one route from the first screen. ^one-route-to-secondary-options
- Show each frequently used option on the first screen. ^show-frequent-options-first

From [Usability heuristics](../../../references/usability-heuristics.md):

- Give each frequent action an accelerator, such as a keyboard shortcut. ^accelerators-for-frequent-actions
- Label each button of a confirmation dialog with its action, not with `Yes`, `No`, or `OK`. ^action-labels-in-dialogs
- Make the back button close a full-screen overlay. ^back-closes-overlay
- Make each back control return to the previous screen, not to the start of the flow. ^back-one-step
- Ask for confirmation before an action that destroys user work and has no undo. ^confirm-destructive-action
- Ask for confirmation before a view with unsaved changes closes. ^confirm-unsaved-close
- Show each error message next to the element that caused it. ^error-near-source
- Do not remove an item that a user saved without a message that states why. ^explain-removed-items
- Put each help text next to the field or the step that it explains. ^help-in-context
- Write each help topic as a list of concrete steps. ^help-lists-steps
- Do not disable the back button of the browser. ^keep-browser-back
- Keep the input of the user in each field that shows an error. ^keep-input-after-error
- Do not use words that blame the user, such as `invalid` or `illegal`, in an error message. ^no-blame-in-errors
- Do not make a destructive button the default button of a dialog. ^no-destructive-default
- Do not show an error for an empty field before the user submits the form. ^no-early-error
- Do not use placeholder text as the only label of a field. ^no-placeholder-as-label
- Show on each screen the information that the user needs from an earlier screen. ^no-recall-across-screens
- Do not ask for confirmation of a routine action that has an undo. ^no-routine-confirmation
- Show a percent-done indicator for each operation that takes more than `10` seconds. ^percent-done-indicator
- Write each error message in the words of the user, with no error code. ^plain-error-message
- Show a busy indicator while an operation takes more than `1` second. ^show-busy-state
- Name the object and the effect of the action in each confirmation dialog. ^specific-confirmation
- Give a visible control to stop each operation that takes more than `10` seconds. ^stop-long-operation
- Tell the user before the product takes an action with consequences for them. ^tell-before-consequences
- Give an undo for each change that a user makes to their content or settings. ^undo-each-change
- Use the words of the users in each label and message, not internal terms. ^use-the-words-of-users
- Give each modal view and each multi-step process a visible control that exits it. ^visible-exit
- Give a visible control for each action that a shortcut or a gesture starts. ^visible-path-for-shortcuts
- Show a warning that does not block the task in a different style from an error. ^warning-differs-from-error

## Inputs

- The options of each screen, with what each one changes
- Who uses each option, and how frequently, from usage data or task analysis if the project has it

The output of each node in this list is an input of this step:

- [Evaluative research](../../../references/evaluative-research.md)
- [Information architecture](information-architecture.md)

## Procedure

1. Rank the options by how frequently people use them.
2. Split the options into a first screen and a secondary screen.
3. Choose a control for each option.

The rest of the procedure of this step is missing.

## Output

A design that states which controls appear on each screen, in what order, and what happens after each action.

The output of this step is an input of each node in this list:

- [Visual design](visual-design.md)

## Exit gate

Check the design against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Visual design](visual-design.md).

## References

- You choose the size or the position of a button, a link, or a menu. Read [Fitts's law](../../../references/fitts-law.md).
- You choose the number of options in a menu, a step, or a first screen. Read [Hick's law](../../../references/hicks-law.md).
- You choose which options appear first. Read [Progressive disclosure](../../../references/progressive-disclosure.md).
- You design feedback, an exit, a confirmation, an error message, or help. Read [Usability heuristics](../../../references/usability-heuristics.md).
