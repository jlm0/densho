---
id: visual-grouping
kind: densho:Concept
title: Visual grouping
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.nngroup.com/articles/gestalt-proximity/
  - https://www.nngroup.com/articles/gestalt-similarity/
  - https://www.nngroup.com/articles/common-region/
  - https://www.nngroup.com/articles/principle-closure/
  - http://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/
broader:
  - visual-design
related:
  - information-hierarchy
---

## Definition

Showing which elements belong together. People see elements as one group, with a shared function or trait, through the grouping principles of Gestalt psychology:

- Proximity: elements close together read as one group, and elements far apart read as separate groups.
- Similarity: elements that share a color, a shape, a size, or a type style read as related, even when they are apart.
- Common region: elements inside one boundary, such as a border or a background, read as one group. Research added this principle in 1992.
- Closure: people fill in the gaps of an incomplete shape and see the whole.
- Connectedness: elements joined by a line or a shared edge read as one group.

Max Wertheimer described proximity, similarity, and common fate in 1923. Common region and connectedness came later. Proximity can override similarity, and a boundary can override proximity.

## Directives

- Place related elements closer to each other than to other elements. ^place-related-elements-close
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-proximity/
  - sources: http://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm
- Place each label closer to its field than to any other field. ^place-label-near-field
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-proximity/
- Group the related fields of each form. ^group-related-fields
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-proximity/
- Do not group unrelated controls. ^no-unrelated-group
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-proximity/
- Separate two groups with whitespace, not with a divider line, unless the space between them is fixed. ^space-not-divider
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/common-region/
- If the space between two groups is fixed, put each group inside a border or a background. ^boundary-for-fixed-space
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/common-region/
- Place each heading closer to the text below it than to the text above it. ^heading-near-its-section
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-proximity/
- Give each text link in an interface the same color. ^one-link-color
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-similarity/
- Do not give text that is not a link the color of the links. ^no-link-color-on-plain-text
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-similarity/
- Give elements with the same function the same visual style. ^same-style-same-function
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-similarity/
- Do not give a decorative element the color or the shape of a control. ^no-decoration-like-control
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/gestalt-similarity/
- Put the image, the title, and the details of each item in a grid inside one container. ^contain-item-parts
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/common-region/
- Give a sticky header a background or a border that separates it from the content under it. ^separate-sticky-header
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/common-region/
- Show the selected tab and its panel inside one shared boundary. ^tab-joins-panel
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/common-region/
- Show part of the next item at the edge of each carousel. ^show-partial-next-item
  - scope: subtree
  - basis: research
  - status: proposed
  - origin: template
  - sources: https://www.nngroup.com/articles/principle-closure/
