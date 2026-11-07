---
id: kano-model
kind: densho:Concept
title: Kano model
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.jstage.jst.go.jp/article/quality/14/2/14_KJ00002952366/_article/-char/en
  - https://foldingburritos.com/blog/kano-model/
  - https://www.nngroup.com/articles/prioritization-methods/
broader:
  - product-prioritization
---

## Definition

A model of customer satisfaction from Noriaki Kano and colleagues, published in 1984. It treats quality in two dimensions: how much of a feature a product provides, and how satisfied customers are with it. Must-be features cause dissatisfaction when absent and no satisfaction when present. One-dimensional features, also called performance features, raise satisfaction in step with how much the product provides. Attractive features delight when present and cause no dissatisfaction when absent. Indifferent features change nothing. A Kano survey asks a pair of questions about each feature and maps each pair of answers to a category with an evaluation table. The table also gives reverse and questionable answers. Categories move over time: an attractive feature becomes a performance or a must-be feature as customers come to expect it.

## Directives

- Ask a functional and a dysfunctional question about each feature in a Kano survey. ^kano-question-pair
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://foldingburritos.com/blog/kano-model/
- Use the answers `like`, `expect`, `neutral`, `tolerate`, and `dislike` for each Kano question. ^kano-answers
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://foldingburritos.com/blog/kano-model/
- Write each Kano question about the benefit to the user, not the name of the feature. ^kano-benefit-questions
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://foldingburritos.com/blog/kano-model/
- Group the answers of a Kano survey by customer segment before you set the category of a feature. ^kano-segments
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://foldingburritos.com/blog/kano-model/

## Notes

The functional question asks how the customer feels if the product has the feature. The dysfunctional question asks how the customer feels if it does not. The dysfunctional question states the absence of the feature, not its opposite. Daniel Zacarias takes the most frequent category in a segment as the category of the feature.

The sources disagree on the order of work. Zacarias builds each must-be feature first, then as many performance features as the team can, then a few attractive features. Nielsen Norman Group, which scores items on a simpler two-axis variant, puts performance first. This node sets no order.

The 1984 paper is in Japanese. Its English abstract names the categories and the questionnaire survey. The directives come from a practitioner guide.
