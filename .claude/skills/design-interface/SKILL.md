---
name: design-interface
description: "Design a new or changed screen or flow, from its structure and behavior to its layout and components. Use when you create or change a user interface: a screen, a form, a settings page, or a flow. Do not use it for a review (`review-interface`), a brand (`design-brand`), or interface copy alone (`design-content`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Design a user interface

## Run the skill

1. Run the steps in their order.
2. If the output of a step exists already, skip the step.
3. If a step has a step file, read the step file.
4. Follow each directive of the step.
5. If you need the definition or the notes of a page, read the page.
6. After each step, check its output against each directive of the step.
7. Before you start the next step, correct each part of the output that breaks a directive.

## 1. Frame the task

1. Name the user, the task, and the target platform.
2. List each screen and each flow that the task creates or changes.
3. Collect the content and the functions of the product.
4. If the project has usage data or a task analysis, collect who uses each option and how frequently.
5. Collect the brand guidelines of the project.
6. Collect the design tokens and the components that the product has.
7. If a screen exists, list what the change keeps on it.
8. List each branch heading of steps `2` to `5` that matches the design.

Pages:

- You design for a specific operating system or with its components. Read [Platform conventions](../../references/platform-conventions.md).
- You design an app for an Apple device. Read [Apple Human Interface Guidelines](../../references/apple-human-interface-guidelines.md).
- You design for Android or with Material components. Read [Material Design](../../references/material-design.md).

Directives:

No directive of this step is in force.

Output: The user, the task, the platform, the screens, the inputs, and the branch headings that match the design.

## 2. Organize the content and the functions

Step file: [steps/information-architecture.md](steps/information-architecture.md)

1. List the content and the functions that the task needs.
2. Sort the content and the functions into groups.
3. If the task needs new categories, ask the person for a card sort with `research-users`.
4. Name each group, each screen, and each function.
5. Add each name to the controlled vocabulary.
6. Define how people move between the screens.
7. State whether the product needs search.

Missing rule: No directive covers what a search indexes, how it shows its results, or a query with no result.

Output: The organization system, the labeling system, the navigation system, and the search system of the content and the functions of the product.

## 3. Define the behavior of each screen

Step file: [steps/interaction-design.md](steps/interaction-design.md)

1. Sort the options by how frequently people use them.
2. Split the options into a first screen and a secondary screen.
3. Choose a control for each option.
4. State the result of each action and the screen that comes next.
5. Define the undo of each change to user content or settings.
6. Define the exit and the back path of each modal view and each multi-step process.
7. Set the order of the keyboard focus on each screen.
8. Set the size and the position of each target.

Missing rule: No directive covers the empty state of a screen or a list.

Missing rule: No directive covers a transition or an animation, because motion design has no node.

Output: A design that states which controls appear on each screen, in what order, and what happens after each action.

## 4. Lay out and style each screen

Step file: [steps/visual-design.md](steps/visual-design.md)

1. Group the options on each screen.
2. Name each group.
3. Name the element that a viewer sees first, then second, then third.
4. Compare that order with the order of importance for the task.
5. Apply the brand guidelines.
6. Mark each sentence and label that a glyph, an image, or a grouping replaces.
7. Check the layout at the narrowest screen width.

Output: The layout, the type, the color, the imagery, and the spacing of each screen.

## 5. Specify the components and the tokens

Step file: [steps/design-systems.md](steps/design-systems.md)

1. Map each element of each screen to a component that the system holds.
2. If an element has no component, build a new component for it.
3. Map each color, size, and space to a design token.
4. State the name, the role, and each state of each custom control.
5. Test each template with real content.

Missing rule: No directive covers how to record a new component in the design system, with its states and its rules for use.

Output: The design tokens and the components that the screens use, with the rules for their use.

## Exit checklist

Check each line before you report the design as done.

- [ ] Steps `1` to `5` each have their output.
- [ ] Each screen holds only the content and the controls that the task needs.
- [ ] Each screen has one primary action, or it is a settings screen.
- [ ] Each action has a stated result, and each change has an undo or a confirmation.
- [ ] Each text and each control meets its contrast ratio.
- [ ] Each screen works at `320` CSS pixels wide and at a text size of `200` percent.
- [ ] Each color, size, and space comes from a token.
- [ ] Each branch heading from step `1` has its directives checked.
- [ ] The report names each directive that the design misses, and each missing rule that the design reached.

## Output

- The outputs of steps 1 to 5, as one design for each screen and each flow
- A list of each directive that the design misses, with the reason

For the code of the design, run `engineer-software`.
