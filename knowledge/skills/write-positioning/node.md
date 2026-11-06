---
id: write-positioning
kind: ka:Skill
title: Write the positioning of a product
status: proposed
origin: template
knowledge_type: domain
description: Write the positioning of a product from its alternatives, unique attributes, value, target customers, and market category. Use when you write or change the positioning of a product.
invocation: agent
uses:
  - product-positioning
  - positioning-components
pointers:
  - kind: ka:TextPointer
    target: product-positioning
    trigger: You separate the positioning from the messaging or the brand story.
  - kind: ka:TextPointer
    target: positioning-components
    trigger: You define the alternatives, the attributes, the value, the customers, or the market category.
---

## Inputs

- The product and its capabilities
- Evidence from the customers who get the most value from the product: interview notes, won deals, and lost deals
- The current positioning, if the product has one

## Procedure

1. Read each directive that this skill lists.
2. Collect the evidence. Find the customers who get the most value from the product, and what they used before it.
3. List the competitive alternatives: what those customers would do if the product did not exist.
4. List the unique attributes: what the product has that the alternatives lack.
5. For each attribute, write the value that it gives to customers. Remove an attribute that gives no value.
6. Describe the target customers by the traits that make them care most about that value.
7. Choose the market category that makes the value obvious to the target customers.
8. Check each component against the others. If a later component changes an earlier one, correct the earlier one and work forward again.

## Output

One positioning document with the five components in order. Each component names the evidence behind it. Mark the positioning as a candidate until the person confirms it with prospects or with the sales team.

## Validation

Check the document against each directive from the first step of the procedure, and report each one it misses. Each value claim traces to a unique attribute, and each unique attribute traces to an alternative that lacks it.
