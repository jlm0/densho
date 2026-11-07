---
id: brand-voice
kind: densho:PracticeArea
title: Brand voice
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://styleguide.mailchimp.com/voice-and-tone/
  - https://atlassian.design/foundations/content/voice-tone
  - https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human
broader:
  - brand-design
informs:
  - visual-identity
pointers:
  - kind: densho:TextPointer
    target: tone-of-voice-dimensions
    trigger: You set, describe, or test the tone of the content of a brand.
---

## Definition

Voice is the personality of a brand in words, and it stays the same wherever the brand speaks. Tone is how that voice adapts to the reader, the moment, and the topic. Mailchimp, Atlassian, and Microsoft each describe their voice as a few named traits, and each changes the tone with the emotional state of the reader.

## Directives

- Describe the brand voice in `3` or `4` traits. ^voice-trait-count
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://styleguide.mailchimp.com/voice-and-tone/
  - sources: https://atlassian.design/foundations/content/voice-tone
  - sources: https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human
- Name a trait to avoid for each voice trait, such as direct but not curt. ^trait-to-avoid
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://styleguide.mailchimp.com/voice-and-tone/
  - sources: https://www.nngroup.com/articles/tone-of-voice-dimensions/
- Match the tone of each message to the emotional state of the reader. ^tone-matches-reader
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://styleguide.mailchimp.com/voice-and-tone/
  - sources: https://atlassian.design/foundations/content/voice-tone
  - sources: https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human
- For each voice trait, list the emotional states of the reader that increase the trait and that reduce it. ^trait-by-reader-state
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atlassian.design/foundations/content/voice-tone
- Write the tone guidance for each type of message, such as an error, a success, or an onboarding step. ^tone-by-message-type
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atlassian.design/foundations/content/voice-tone
- Do not add a joke to an error message. ^no-joke-in-errors
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://atlassian.design/foundations/content/voice-tone
- Remove each joke that makes a message less clear. ^clarity-over-jokes
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://styleguide.mailchimp.com/voice-and-tone/

## Notes

Mailchimp names four traits: plainspoken, genuine, translators, and dry humor. Atlassian names three: bold, optimistic, and practical with a wink. Microsoft names three: warm and relaxed, crisp and clear, and ready to lend a hand. Each guide explains what each trait means in practice. Mailchimp sets its humor trait against the excess that it avoids: weird but not inappropriate, and smart but not snobbish. NN/g gives the same pattern for tone words: authoritative without being pedantic.

Atlassian sets each trait against the state of the reader. A user who is confident gets more boldness. A user who is new, confused, or afraid gets less. The wink suits a success message or a social moment, and a user who is blocked by an error gets plain, practical help. Mailchimp puts clarity before entertainment and warns that forced humor is worse than none.

A project states its own traits in its brand definition. The tone dimensions give the scales on which to place them.
