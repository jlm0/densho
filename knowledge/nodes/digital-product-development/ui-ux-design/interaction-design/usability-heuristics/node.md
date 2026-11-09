---
id: usability-heuristics
kind: densho:Concept
title: Usability heuristics
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/ten-usability-heuristics/
broader:
  - interaction-design
related:
  - accessibility
---

## Definition

The ten general principles for interaction design that Jakob Nielsen published in 1994. They are broad rules of thumb, not specific guidelines, and a heuristic evaluation checks an interface against them:

01. Visibility of system status
02. Match between the system and the real world
03. User control and freedom
04. Consistency and standards
05. Error prevention
06. Recognition rather than recall
07. Flexibility and efficiency of use
08. Aesthetic and minimalist design
09. Help users recognize, diagnose, and recover from errors
10. Help and documentation

## Directives

- Show a busy indicator while an operation takes more than `1` second. ^show-busy-state
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/response-times-3-important-limits/
- Show a percent-done indicator for each operation that takes more than `10` seconds. ^percent-done-indicator
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/response-times-3-important-limits/
- Give a visible control to stop each operation that takes more than `10` seconds. ^stop-long-operation
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/response-times-3-important-limits/
- Tell the user before the product takes an action with consequences for them. ^tell-before-consequences
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
  - sources: https://www.nngroup.com/articles/visibility-system-status/
- Do not remove an item that a user saved without a message that states why. ^explain-removed-items
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/visibility-system-status/
- Give each modal view and each multi-step process a visible control that exits it. ^visible-exit
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
  - sources: https://www.nngroup.com/articles/user-control-and-freedom/
  - sources: https://developer.apple.com/design/human-interface-guidelines/modality
- Give an undo for each change that a user makes to their content or settings. ^undo-each-change
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
  - sources: https://www.nngroup.com/articles/user-control-and-freedom/
- Ask for confirmation before an action that destroys user work and has no undo. ^confirm-destructive-action
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/confirmation-dialog/
- Do not ask for confirmation of a routine action that has an undo. ^no-routine-confirmation
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/confirmation-dialog/
  - sources: https://developer.apple.com/design/human-interface-guidelines/alerts
- Name the object and the effect of the action in each confirmation dialog. ^specific-confirmation
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/confirmation-dialog/
- Label each button of a confirmation dialog with its action, not with `Yes`, `No`, or `OK`. ^action-labels-in-dialogs
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/confirmation-dialog/
  - sources: https://developer.apple.com/design/human-interface-guidelines/alerts
- Do not make a destructive button the default button of a dialog. ^no-destructive-default
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/confirmation-dialog/
  - sources: https://developer.apple.com/design/human-interface-guidelines/buttons
- Ask for confirmation before a view with unsaved changes closes. ^confirm-unsaved-close
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://developer.apple.com/design/human-interface-guidelines/modality
- Do not use placeholder text as the only label of a field. ^no-placeholder-as-label
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/form-design-placeholders/
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Show on each screen the information that the user needs from an earlier screen. ^no-recall-across-screens
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Give a visible control for each action that a shortcut or a gesture starts. ^visible-path-for-shortcuts
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
  - sources: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Give each frequent action an accelerator, such as a keyboard shortcut. ^accelerators-for-frequent-actions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Write each error message in the words of the user, with no error code. ^plain-error-message
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: error-messages
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
  - sources: https://www.nngroup.com/articles/error-message-guidelines/
- Show each error message next to the element that caused it. ^error-near-source
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: error-messages
  - sources: https://www.nngroup.com/articles/error-message-guidelines/
- Keep the input of the user in each field that shows an error. ^keep-input-after-error
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: error-messages
  - sources: https://www.nngroup.com/articles/error-message-guidelines/
- Do not show an error for an empty field before the user submits the form. ^no-early-error
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: error-messages
  - sources: https://www.nngroup.com/articles/error-message-guidelines/
- Do not use words that blame the user, such as `invalid` or `illegal`, in an error message. ^no-blame-in-errors
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: error-messages
  - sources: https://www.nngroup.com/articles/error-message-guidelines/
- Show a warning that does not block the task in a different style from an error. ^warning-differs-from-error
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - also_attached_to: error-messages
  - sources: https://www.nngroup.com/articles/error-message-guidelines/
- Put each help text next to the field or the step that it explains. ^help-in-context
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/
- Write each help topic as a list of concrete steps. ^help-lists-steps
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/ten-usability-heuristics/

## Notes

The directives follow the order of the heuristics. Rules for heuristic 4 also live in Platform conventions, and heuristic 8 is the rule on the UI/UX design node that shows only what the task needs. The time limits come from the response time limits of Nielsen: `0.1` second feels instant, `1` second keeps the flow of thought, and `10` seconds keeps attention on the task.
