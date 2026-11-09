---
title: Organize the content and the functions
pages:
  - target: categorization
    trigger: You sort content or functions into groups.
  - target: labeling
    trigger: You name a section, a link, a heading, or a function.
  - target: navigation
    trigger: You design how people move between screens.
  - target: search-system
    trigger: You add or change the search of a product.
  - target: ux-writing
    trigger: You write a label, a message, or an instruction in an interface.
  - target: platform-conventions
    trigger: You design for a specific operating system or with its components.
  - target: accessibility
    trigger: You build a control, a form, a text style, a color choice, or media.
directives:
  - show-what-the-task-needs
  - card-sort-new-categories
  - name-categories-for-users
  - review-card-sort-names
  - define-controlled-vocabulary
  - one-word-one-meaning
  - use-the-words-of-users
  - descriptive-headings-and-labels
  - descriptive-page-title
  - link-purpose
  - consistent-identification
  - keep-navigation-order
  - show-current-location
  - two-ways-to-each-page
  - tabs-for-navigation
  - label-each-tab
branches:
  - condition: If the target is an Apple device
    directives:
      - apple-keep-tabs-enabled
  - condition: If the target is Android
    directives:
      - navigation-bar-destinations
missing_rules:
  - No directive covers what a search indexes, how it shows its results, or a query with no result.
---

## Procedure

1. List the content and the functions that the task needs.
2. Sort the content and the functions into groups.
3. If the task needs new categories, ask the person for a card sort with `research-users`.
4. Name each group, each screen, and each function.
5. Add each name to the controlled vocabulary.
6. Define how people move between the screens.
7. State whether the product needs search.

## Output

The organization system, the labeling system, the navigation system, and the search system of the content and the functions of the product.
