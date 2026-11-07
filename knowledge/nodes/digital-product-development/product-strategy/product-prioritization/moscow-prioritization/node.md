---
id: moscow-prioritization
kind: densho:Concept
title: MoSCoW prioritization
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.agilebusiness.org/resource/what-is-moscow-prioritization/
  - https://www.nngroup.com/articles/prioritization-methods/
broader:
  - product-prioritization
---

## Definition

A method from DSDM that puts each requirement in one of four groups for a fixed timeframe. Must Have requirements form the minimum usable subset that the project guarantees. Without one of them, the solution is not worth deploying, is not legal, is not safe, or is not viable. Should Have requirements are important but have a workaround. Could Have requirements are wanted but have less impact, and they are the first to drop when a deadline is at risk. Won't Have this time requirements are out of scope for the timeframe, and the list of requirements records them.

## Directives

- Keep the `Must Have` items at or below `60%` of the effort of a timeframe. ^must-have-limit
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.agilebusiness.org/resource/what-is-moscow-prioritization/
- Prefer a pool of `Could Have` items of `20%` of the effort of a timeframe. ^could-have-pool
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.agilebusiness.org/resource/what-is-moscow-prioritization/
- Do not mark an item as `Must Have` when a workaround exists. ^no-must-with-workaround
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.agilebusiness.org/resource/what-is-moscow-prioritization/
- Record each `Won't Have` item in the list of requirements. ^record-wont-haves
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.agilebusiness.org/resource/what-is-moscow-prioritization/
- State the timeframe of each MoSCoW priority. ^priority-per-timeframe
  - scope: subtree
  - basis: practitioner
  - status: proposed
  - origin: template
  - sources: https://www.agilebusiness.org/resource/what-is-moscow-prioritization/

## Notes

One requirement can have a priority for the project, another for an increment, and another for a timebox. DSDM accepts more than `60%` Must Have effort only when the estimates are known to be accurate, the approach is well understood, the team performs well, and the environment carries little risk. A workaround counts even when it is manual and painful. Nielsen Norman Group adds that MoSCoW needs a clear time box: without one, each item feels like a Must Have.
