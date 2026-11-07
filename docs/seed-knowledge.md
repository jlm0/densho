# Seed knowledge

> **In the library:** the first real books. They give every check real text to read, and they give a new project something to start from.

**Status:** Built.

A project that [installs the template](template-packaging.md) receives this knowledge. It is ordinary content: one domain, fourteen domain skills, and a few language terms, and it goes through the same checks and the same workflow as anything a project adds. Each install also gets the three preset skills of the [improvement loop](improvement-loop.md) and the [eval](evaluation.md) skill, which aren't part of any discipline, and the eval tasks of the disciplines it takes. Nothing in it binds an agent until a person accepts it.

## What ships

The domain is Digital Product Development, under `knowledge/nodes/digital-product-development/`. All four disciplines are there, each with its own practice areas and concepts. They differ in depth, because branch depth follows real classification and does not have to match:

```text
Digital product development
├── Product strategy
│   ├── Strategy
│   │   └── Kernel of a strategy
│   ├── Discovery
│   │   ├── Jobs to be done
│   │   ├── Opportunity solution tree
│   │   ├── Four product risks
│   │   ├── Assumption testing
│   │   └── Product opportunity assessment
│   ├── Positioning
│   │   └── Components of positioning
│   ├── Prioritization
│   │   ├── RICE scoring
│   │   ├── Kano model
│   │   ├── Cost of delay
│   │   └── MoSCoW prioritization
│   └── Measurement
│       ├── North star metric
│       ├── HEART framework
│       └── Objectives and key results
├── Brand design
│   ├── Brand strategy
│   │   ├── Brand identity prism
│   │   ├── Brand equity pyramid
│   │   ├── Brand positioning statement
│   │   ├── Brand personality
│   │   └── Distinctive brand assets
│   ├── Voice and tone
│   │   └── Tone of voice dimensions
│   ├── Visual identity
│   │   ├── Logo
│   │   ├── Color roles
│   │   └── Type scale
│   └── Brand systems
│       ├── Brand guidelines
│       └── Brand architecture
├── UI/UX design
│   ├── Information architecture
│   │   └── Categorization
│   ├── Interaction design
│   │   ├── Progressive disclosure
│   │   ├── Navigation
│   │   ├── Usability heuristics
│   │   ├── Fitts's law
│   │   └── Hick's law
│   ├── Visual design
│   │   ├── Information hierarchy
│   │   ├── Visual grouping
│   │   └── Visual communication
│   ├── Accessibility
│   ├── Responsive design
│   ├── Platform conventions
│   │   ├── Apple Human Interface Guidelines
│   │   └── Material Design
│   └── Design systems
│       ├── Design tokens
│       └── Atomic design
└── Software engineering
    ├── Security
    │   ├── Access control
    │   ├── Injection
    │   ├── Secrets management
    │   └── Software supply chain
    ├── Testing
    │   └── Test pyramid
    ├── Delivery
    │   ├── Trunk-based development
    │   ├── Conventional Commits
    │   ├── Semantic versioning
    │   └── Software delivery metrics
    ├── Architecture
    │   ├── C4 model
    │   ├── Architecture decision record
    │   └── Twelve-factor app
    ├── Reliability
    │   ├── Service level objective
    │   ├── Error budget
    │   └── Postmortem
    └── Code review
```

Directives sit at every level of the taxonomy. A pointer on the root reaches the domain, and pointers lead from there down the tree, so every node is four hops or fewer from the root.

The hierarchy is not the only structure. `informs`, `depends_on`, and `related` record links across branches, such as Product strategy informing the other three disciplines. Those edges state a relationship and carry no directive, so one accessibility rule also attaches to Visual design and Brand design with `also_attached_to`.

## The skills

| Skill                       | Use it when                                                     | What it draws on                                                                                                                          |
| --------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `design-settings-interface` | You design or change a settings screen                          | Progressive disclosure, Information hierarchy, Visual grouping, Brand and Responsive design, and 17 accessibility rules through `applies` |
| `review-screen-hierarchy`   | A screen design is ready for review                             | Information hierarchy, Visual grouping, Visual communication, and two contrast rules through `applies`                                    |
| `review-usability`          | A flow is ready for a usability review                          | Usability heuristics, Fitts's law, Hick's law, Navigation, and Platform conventions                                                       |
| `audit-accessibility`       | A screen, a component, or a flow needs an accessibility check   | Accessibility, and the Reflow and Consistent Navigation rules through `applies`                                                           |
| `review-code-change`        | A change is ready for review                                    | Code review, Testing, Security, Access control, and Injection                                                                             |
| `write-decision-record`     | You make or change a decision about the structure of a system   | Architecture decision record                                                                                                              |
| `write-strategy`            | You write the strategy of a product, a team, or a company       | Strategy and Kernel of a strategy                                                                                                         |
| `map-opportunities`         | A team chooses the next customer need that it works on          | Opportunity solution tree, Jobs to be done, Assumption testing, and Four product risks                                                    |
| `write-positioning`         | You write or change the positioning of a product                | Positioning and Components of positioning                                                                                                 |
| `prioritize-work`           | You set the order of the work of a team                         | Prioritization, RICE scoring, Cost of delay, Kano model, and MoSCoW prioritization                                                        |
| `define-success-metrics`    | You decide how to measure the success of a product or a feature | Measurement, HEART framework, North star metric, and Objectives and key results                                                           |
| `define-brand-voice`        | You define or change the voice of a brand                       | Voice and tone, Tone of voice dimensions, and Brand personality                                                                           |
| `write-brand-guidelines`    | You write or update brand guidelines                            | Brand strategy, Visual identity, Voice and tone, Brand systems, seven of their concepts, and three contrast rules through `applies`       |
| `audit-brand-consistency`   | You review the touchpoints of a brand for consistency           | Visual identity, Logo, Color roles, Type scale, Distinctive brand assets, Voice and tone, and Brand guidelines                            |

`design-settings-interface` takes a subset of Accessibility. The whole node holds 61 rules and would bring the skill close to its [size limit](runtime-files.md#why-a-skill-holds-a-copy), while rules such as captions, flashing content, and sign-in have nothing to check on a settings screen. A skill source names knowledge and does not copy it. Its body holds only the inputs, the procedure, the output, and how to validate the result. The [generated skill file](runtime-files.md#why-a-skill-holds-a-copy) holds the directives in force. To see every rule a skill carries, with each proposal labeled:

```sh
uv run densho directives --at design-settings-interface
```

`design-settings-interface` also steps out of one inherited rule, because a settings screen has no single primary action. That [exception](directive-semantics.md#stepping-out) is a proposal too, so a reviewer decides whether it stands.

## Accept what you received

Every node, directive, and exception here is `proposed`, so the seed is checked but not in force. `densho directives --at` labels each one as a proposal, and code that asks what is in force gets nothing back until a person reviews it:

```sh
uv run densho governance --pending
```

Or run `uv run densho view` and read `build/view/review.html`, which groups the list by node. Then run `uv run densho accept` on what you want, and commit a change that holds only `status` and the generated files. You can do that in one batch. The [human interface](human-interface.md#accept-what-you-approve) has the steps.

## Make it your own

The knowledge is yours to change:

- To add a concept, add a `node.md` under `knowledge/nodes/` with `status: proposed` and `origin: project`, name its parent in `broader`, and give some node a pointer to it.
- To give a domain node project values, such as your brand colors, add a workspace node that names it in `implements`.
- To add a rule, follow the grammar in [language checks](language-checks.md). If it opens with a verb the vocabulary doesn't approve, add the verb to `knowledge/governance/language/vocabulary.yaml`, or to `knowledge/governance/language/branches/<node-id>.yaml` if only one branch needs it.
- To remove a branch, delete its nodes, each reference to them, and any branch vocabulary named after them. The [graph checks](graph-checks.md) list what still points at a deleted node. An accepted entity goes through [deprecation first](governance-workflow.md#remove-something).

## Add a discipline

The four disciplines were written with the procedure that the `author-domain` skill now holds, and you can use it to add another discipline or a practice area to your copy of the template. It lives in `global-skills/`, like the migration skill, so a project doesn't receive it. Installing it is your choice. From a clone of this repo:

```sh
cp -R global-skills/author-domain ~/.claude/skills/
```

Then ask an agent to add the discipline, and give it an outline: the practice areas, the frameworks, and the skills you expect. The agent opens each source before it cites it, keeps a source log with the version of each page and the facts it supports, and writes each rule in its own words. A framework that only a book describes gets cited through a page the agent could open, such as an article by the author, with the book named in the log. A framework with no page to support it is left out and reported. Each new entity is `proposed`, `origin: template`, and has a `basis` that fits its source.

A new discipline also needs a line in the `disciplines` question of `copier.yml`, so that an install can offer it, and the skill adds it.

## Language terms

Two branches add terms in `knowledge/governance/language/branches/`. `ui-ux-design.yaml` approves `design` as an opening verb and prohibits vague words such as `intuitive` and `clean`, which say how a screen should feel without saying what to do. `software-engineering.yaml` approves `revoke` and `increment`, the verb that Semantic Versioning uses for a version number.

## Sources

A `sources` value names a page that was read when the rule was written. Where a framework has versions, the rule cites the version that was current then:

- UI/UX design: the Web Content Accessibility Guidelines 2.2 and their Understanding pages, the WCAG evaluation methodology WCAG-EM 2.0, Nielsen Norman Group articles, Laws of UX, the Interaction Design Foundation, Wertheimer's 1923 paper on perceptual grouping and a 2012 review of Gestalt research, and MDN
- Platform conventions: the Apple Human Interface Guidelines, the Android design guides, and the Material Components for Android docs
- Design systems: the Design Tokens Format Module 2025.10 and its glossary, and Brad Frost's *Atomic Design*
- Security: the OWASP Top 10:2025, the OWASP Application Security Verification Standard 5.0.0, and the OWASP Secrets Management Cheat Sheet
- Testing: the test pyramid pages on martinfowler.com, and the testing chapter of *Software Engineering at Google*
- Delivery: trunkbaseddevelopment.com, the DORA guides, Conventional Commits 1.0.0, and Semantic Versioning 2.0.0
- Architecture: the C4 model site, Michael Nygard's post on architecture decision records, and The Twelve-Factor App
- Reliability: the Google SRE book and workbook
- Code review: Google's engineering practices guide
- Brand design: Kevin Lane Keller's working paper on brand equity for the Marketing Science Institute, a peer-reviewed article on Kapferer's brand identity prism, publisher excerpts of Alice Tybout's chapter in *Kellogg on Branding in a Hyper-Connected World* and of Alina Wheeler's *Designing Brand Identity*, Jennifer Aaker on brand personality, Jenni Romaniuk of the Ehrenberg-Bass Institute on distinctive brand assets, Nielsen Norman Group on tone of voice, the voice guides of Mailchimp, Atlassian, and Microsoft, the logo guidance of Atlassian, Apple, and GitHub, the GitHub color page, the Material Components theming docs, and Tim Brown on modular scales
- Product strategy: Richard Rumelt's article on bad strategy, Marty Cagan's articles on SVPG, Teresa Torres on Product Talk, the Christensen Institute and Tony Ulwick on jobs to be done, April Dunford, Intercom's article on RICE, Noriaki Kano's 1984 paper and Daniel Zacarias's guide to it, Joshua Arnold on cost of delay, DSDM on MoSCoW, Nielsen Norman Group, Amplitude, the HEART paper from Google, and What Matters with Google's OKR playbook

Several product strategy and brand frameworks come from books, such as *Good Strategy/Bad Strategy*, *Inspired*, *Continuous Discovery Habits*, *Obviously Awesome*, *The New Strategic Brand Management*, and *Designing Brand Identity*. A rule cites a page that was read: an article by the author, a publisher excerpt of the book, or, for Kapferer, a peer-reviewed article that describes his model.

A rule with no `sources` is a judgment call, so read it with more care.

Each directive also states its `basis`, the kind of source behind it. In the domain and the skills:

| `basis`        | Directives | Where they come from                                                                                                                                                                                                                                                                                                                  |
| -------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard`     | 111        | WCAG 2.2, the Design Tokens Format Module, the OWASP Top 10 and ASVS, Conventional Commits, and Semantic Versioning                                                                                                                                                                                                                   |
| `research`     | 47         | The Gestalt grouping research, Fitts's law, and Hick's law, mostly through Nielsen Norman Group articles, the DORA research, the HEART paper from Google, and the Ehrenberg-Bass Institute's research on distinctive brand assets                                                                                                     |
| `practitioner` | 290        | Named methods and authors: Nielsen Norman Group, WCAG-EM, Apple, Android and Material Components, Brad Frost, MDN, an OWASP cheat sheet, martinfowler.com, Google, Paul Hammant, Simon Brown, Michael Nygard, Adam Wiggins, the voice guides of Mailchimp, Atlassian, and Microsoft, and the product strategy and brand authors above |
| `judgment`     | 5          | No source                                                                                                                                                                                                                                                                                                                             |

Every governance directive is `judgment`, because the policies come from this project's own design and cite nothing.

The Design Tokens format counts as `standard` even though it is a W3C Community Group report rather than a W3C Recommendation, and its node says so. WCAG-EM is a W3C Group Note, so it counts as `practitioner`.

## How it fits

This is the first real content for the [schema](schema.md), the [format](node-format.md), and the checks. The [compiled outputs](compiled-outputs.md), the [runtime files](runtime-files.md), and the [human interface](human-interface.md) read it. While a seed directive is `proposed`, only `uv run densho build --proposals`, `uv run densho runtime --proposals`, and the site hold it, and each marks it as not in force.

## What it does not check yet

- Whether a rule is right. The checks read form and structure, and a reviewer reads meaning.
- Whether a value in `sources` exists, says what the rule says, or still says it
- The definitions and the body text. The [language checks](language-checks.md) read only directives, triggers, and skill descriptions.
- A `conflicts_with` pair on real content. No seed directive declares one, because no two seed rules truly conflict.
