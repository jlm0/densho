---
id: define-brand-voice
kind: densho:Skill
title: Define the voice of a brand
status: proposed
origin: template
knowledge_type: domain
description: Define the voice traits and the tone guidance of a brand from its personality and its readers. Use when you define or change the voice of a brand.
invocation: agent
uses:
  - brand-voice
  - tone-of-voice-dimensions
  - brand-personality
pointers:
  - kind: densho:TextPointer
    target: brand-voice
    trigger: You name the voice traits or write the tone guidance for a type of message.
  - kind: densho:TextPointer
    target: tone-of-voice-dimensions
    trigger: You place the tone on the four dimensions or test it with users.
  - kind: densho:TextPointer
    target: brand-personality
    trigger: You describe the personality that the voice expresses.
---

## Inputs

- The positioning statement and the identity prism of the brand, if the brand has them
- The readers: who they are, and the emotional states in which they meet the content
- Samples of the current content: product copy, error messages, email, and marketing

## Procedure

1. Read each directive that this skill lists.
2. Describe the personality of the brand in human traits. Use the five dimensions of Aaker as the vocabulary.
3. Place the tone of the brand on each of the four tone dimensions. Mark the default point and the range on each scale. Then choose the tone words and the anti-tone words.
4. Write the voice traits. Give each trait a one-sentence explanation and a trait to avoid.
5. List the types of message that the brand sends, and the emotional state of the reader for each one.
6. For each voice trait, list the reader states that increase it and the states that reduce it.
7. Write the tone guidance for each type of message, with one example message in the voice.
8. Rewrite three samples of the current content in the voice, and compare each one with its original.
9. Plan a test with users: they choose tone words for the samples, or rate them on each dimension.

## Output

A voice and tone guide with the personality, the tone profile, the voice traits with their explanations and the traits to avoid, the tone words and the anti-tone words, and the tone guidance for each type of message with its example. Add the test plan of step 9.

## Validation

Check the guide against each directive from the first step of the procedure, and report each one it misses. Each piece of tone guidance names a type of message and a reader state. Each example message fits the tone profile.
