# Seed knowledge

> **In the library:** the first real books. They give every check real text to read, and they give a new project something to start from.

**Status:** Built.

A project that [installs the template](template-packaging.md) receives this knowledge. It is ordinary content: one domain, fourteen domain skills, and a few language terms, and it goes through the same checks and the same workflow as anything a project adds. Each install also gets the three preset skills of the [improvement loop](improvement-loop.md) and the [eval](evaluation.md) skill, which aren't part of any discipline, and the eval tasks of the disciplines it takes. Nothing in it binds an agent until a person accepts it.

## What ships

The domain is Digital Product Development, under `knowledge/nodes/digital-product-development/`. All six disciplines are there, each with its own practice areas and concepts. Each discipline follows an established body of work, such as SWEBOK for software engineering and the GOV.UK content design guidance for content design. A number marks a step of the flow inside its discipline. A branch without a number works beside the flow: it applies at every step, like Accessibility, or it hands its output to another discipline, like Product positioning.

```text
Digital product development
├── Product strategy
│   ├── 1 Strategy formulation
│   │   └── Kernel of a strategy
│   ├── 2 Product measurement
│   │   ├── North star metric
│   │   ├── Objectives and key results
│   │   └── HEART framework
│   ├── 3 Product discovery
│   │   ├── Jobs to be done
│   │   ├── Opportunity solution tree
│   │   └── Assumption testing
│   ├── 4 Prioritization
│   │   └── RICE scoring
│   └── Product positioning
│       └── Components of positioning
├── User research
│   ├── 1 Research planning
│   │   ├── Research questions
│   │   └── Method choice
│   ├── 2 Generative research
│   │   ├── Story-based interviews
│   │   └── Contextual inquiry
│   ├── 3 Research synthesis
│   │   ├── Interview snapshots
│   │   └── Affinity mapping
│   └── 4 Evaluative research
│       ├── Usability testing
│       └── System Usability Scale
├── Brand design
│   ├── 1 Brand strategy
│   │   ├── Brand positioning statement
│   │   ├── Brand identity prism
│   │   └── Distinctive brand assets
│   ├── 2 Brand voice
│   │   └── Tone of voice dimensions
│   ├── 3 Visual identity
│   │   ├── Logo
│   │   ├── Color roles
│   │   └── Type scale
│   └── 4 Brand systems
│       ├── Brand guidelines
│       └── Brand architecture
├── Content design
│   ├── 1 Content strategy
│   │   ├── Content audit
│   │   └── Content model
│   ├── 2 Writing
│   │   ├── Plain language
│   │   └── Inverted pyramid
│   ├── 3 UX writing
│   │   ├── Voice and tone in context
│   │   └── Error messages
│   ├── 4 Content governance
│   │   └── Content style guide
│   └── Documentation
│       └── Diátaxis
├── UI/UX design
│   ├── 1 Information architecture
│   │   ├── Organization
│   │   ├── Labeling
│   │   ├── Navigation
│   │   └── Search system
│   ├── 2 Interaction design
│   │   ├── Progressive disclosure
│   │   ├── Usability heuristics
│   │   ├── Fitts's law
│   │   └── Hick's law
│   ├── 3 Visual design
│   │   ├── Information hierarchy
│   │   ├── Visual grouping
│   │   └── Visual communication
│   ├── 4 Design systems
│   │   ├── Design tokens
│   │   └── Atomic design
│   ├── Accessibility
│   ├── Responsive design
│   └── Platform conventions
│       ├── Apple Human Interface Guidelines
│       └── Material Design
└── Software engineering
    ├── 1 Software requirements
    │   ├── Spike
    │   ├── Specification by example
    │   └── Requirements traceability
    ├── 2 Software architecture
    │   ├── Architecture style
    │   ├── Integration style
    │   ├── C4 model
    │   └── Architecture decision record
    ├── 3 Software design
    │   ├── Interface contract
    │   └── UI contract
    ├── 4 Software testing
    │   ├── Test-driven development
    │   ├── Test pyramid
    │   ├── Unit testing
    │   ├── Integration testing
    │   ├── End-to-end testing
    │   ├── Test doubles
    │   ├── Contract testing
    │   ├── Black-box test techniques
    │   ├── Property-based testing
    │   ├── Model-based testing
    │   ├── Code coverage
    │   ├── Mutation testing
    │   ├── Regression testing
    │   ├── Performance testing
    │   └── AI evaluations
    ├── 5 Software construction
    │   ├── Infrastructure engineering
    │   │   ├── Infrastructure as code
    │   │   └── Twelve-factor app
    │   ├── Backend engineering
    │   │   ├── Data modeling
    │   │   └── Expand and contract
    │   ├── Frontend engineering
    │   │   ├── Progressive enhancement
    │   │   └── Core Web Vitals
    │   └── Native engineering
    │       └── Store review guidelines
    ├── 6 Software configuration management
    │   ├── Trunk-based development
    │   ├── Conventional Commits
    │   ├── Build pipeline
    │   └── Semantic versioning
    ├── 7 Software quality
    │   ├── Code review
    │   ├── YAGNI
    │   ├── Root cause analysis
    │   ├── Acceptance testing
    │   ├── Exploratory testing
    │   └── Definition of done
    ├── 8 Software operations
    │   ├── Continuous delivery
    │   ├── Observability
    │   ├── Tracking plan
    │   ├── Service level objective
    │   ├── Error budget
    │   ├── Postmortem
    │   └── Software delivery metrics
    └── Software security
        ├── Threat modeling
        ├── Secure coding
        │   ├── Access control
        │   ├── Injection
        │   ├── Secrets management
        │   └── Software supply chain
        ├── Security review
        ├── Security assessment
        └── Vulnerability management
```

Directives sit at every level of the taxonomy. A pointer on the root reaches the domain, and pointers lead from there down the tree, so every node is five hops or fewer from the root. Branch depth follows real classification and doesn't have to match: Software construction splits into lanes for infrastructure, backend, frontend, and native work, and Secure coding holds four concepts of its own.

The hierarchy is not the only structure. `informs` records the flow of work, and each reference page lists that flow as [Comes from and Goes to](runtime-files.md#the-flow-of-a-node). Each numbered step informs the next one, and so does each concept in a step whose concepts run in order, such as the three concepts of Product discovery. The flow also crosses disciplines where the output of one is an input of another:

- Prioritization informs Software requirements and Information architecture.
- Product positioning informs Brand strategy.
- Research synthesis informs Product discovery, and Evaluative research informs Interaction design.
- Brand voice informs UX writing, and Visual identity informs Design systems.
- Content strategy informs Information architecture.
- Design systems informs Software design, and Platform conventions informs Native engineering.
- Software quality informs Documentation, and Software operations informs Product measurement.

`depends_on` and `related` record other links. A node depends on another only when it has no meaning without it, so no node depends on a node in another discipline.

None of these edges carries a directive. A practice area whose rules apply across the flow attaches each rule to the other nodes with `also_attached_to`:

- Each accessibility rule attaches to UI/UX design, Software testing, and Frontend engineering.
- Each responsive design rule attaches to UI/UX design and Frontend engineering.
- Each security rule attaches to Software construction and Software quality. Six of them, such as the access check on the server, shape a design, so they attach to Software architecture too.

## The skills

| Skill                       | Use it when                                                     | What it draws on                                                                                                                 |
| --------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `design-settings-interface` | You design or change a settings screen                          | Progressive disclosure, Information hierarchy, Visual grouping, Brand design, and Responsive design                              |
| `review-screen-hierarchy`   | A screen design is ready for review                             | Information hierarchy, Visual grouping, and Visual communication                                                                 |
| `review-usability`          | A flow is ready for a usability review                          | Usability heuristics, Fitts's law, Hick's law, Navigation, and Platform conventions                                              |
| `audit-accessibility`       | A screen, a component, or a flow needs an accessibility check   | Accessibility, and the Consistent Navigation rule through `applies`                                                              |
| `review-code-change`        | A change is ready for review                                    | Code review, Test pyramid, Software security, Access control, and Injection                                                      |
| `write-decision-record`     | You make or change a decision about the structure of a system   | Architecture decision record                                                                                                     |
| `write-strategy`            | You write the strategy of a product, a team, or a company       | Strategy formulation and Kernel of a strategy                                                                                    |
| `map-opportunities`         | A team chooses the next customer need that it works on          | Opportunity solution tree, Jobs to be done, and Assumption testing                                                               |
| `write-positioning`         | You write or change the positioning of a product                | Product positioning and Components of positioning                                                                                |
| `prioritize-work`           | You set the order of the work of a team                         | Prioritization and RICE scoring                                                                                                  |
| `define-success-metrics`    | You decide how to measure the success of a product or a feature | Product measurement, HEART framework, North star metric, and Objectives and key results                                          |
| `define-brand-voice`        | You define or change the voice of a brand                       | Brand voice, Tone of voice dimensions, and Brand identity prism                                                                  |
| `write-brand-guidelines`    | You write or update brand guidelines                            | Brand strategy, Visual identity, Brand voice, Brand systems, seven of their concepts, and three contrast rules through `applies` |
| `audit-brand-consistency`   | You review the touchpoints of a brand for consistency           | Visual identity, Logo, Color roles, Type scale, Distinctive brand assets, Brand voice, and Brand guidelines                      |

Most accessibility rules reach a skill through their attachments, not through what the skill lists. Accessibility holds 61 rules. The 38 that apply to any screen, such as contrast, focus, and labels, have `subtree` scope: they reach each node of UI/UX design, and each skill that uses one of those nodes carries them. The other 23, such as captions, flashing content, and sign-in, have `node` scope. They reach only a skill that uses Accessibility, Software testing, or Frontend engineering itself, such as `audit-accessibility`. They stay out of `design-settings-interface`, where they have nothing to check on a settings screen. They also stay out of `review-code-change`, which uses Test pyramid in place of Software testing to stay under the size limit for a skill. A skill source names knowledge and does not copy it. Its body holds only the inputs, the procedure, the output, and how to validate the result. The [generated skill file](runtime-files.md#why-a-skill-holds-a-copy) holds the directives in force. To see every rule a skill carries, with each proposal labeled:

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

The first four disciplines were written with the procedure that the `author-domain` skill now holds, and you can use it to add another discipline or a practice area to your copy of the template. It lives in `global-skills/`, like the migration skill, so a project doesn't receive it. Installing it is your choice. From a clone of this repo:

```sh
cp -R global-skills/author-domain ~/.claude/skills/
```

Then ask an agent to add the discipline, and give it an outline: the practice areas, the frameworks, and the skills you expect. The agent opens each source before it cites it, keeps a source log with the version of each page and the facts it supports, and writes each rule in its own words. A framework that only a book describes gets cited through a page the agent could open, such as an article by the author, with the book named in the log. A framework with no page to support it is left out and reported. Each new entity is `proposed`, `origin: template`, and has a `basis` that fits its source.

A new discipline also needs a line in the `disciplines` question of `copier.yml`, so that an install can offer it, and the skill adds it.

## Language terms

Two branches add terms in `knowledge/governance/language/branches/`. `ui-ux-design.yaml` approves `design` as an opening verb and prohibits vague words such as `intuitive` and `clean`, which say how a screen should feel without saying what to do. `software-engineering.yaml` approves `revoke` and `increment`, the verb that Semantic Versioning uses for a version number.

## Sources

A `sources` value names a page that was read when the rule was written. Where a framework has versions, the rule cites the version that was current then:

- Product strategy: Richard Rumelt's article on bad strategy, Marty Cagan's articles on SVPG, Teresa Torres on Product Talk, the Christensen Institute on jobs to be done, April Dunford, Intercom's article on RICE, Nielsen Norman Group, Amplitude, the HEART paper from Google, and What Matters with Google's OKR playbook
- User research: Nielsen Norman Group articles on choosing a method, interviews, contextual inquiry, thematic analysis, affinity diagrams, and usability testing, Teresa Torres on story-based interviews and interview snapshots, and John Brooke's retrospective on the System Usability Scale
- Brand design: a peer-reviewed article on Kapferer's brand identity prism and the publisher page of his book, publisher excerpts of Alice Tybout's chapter in *Kellogg on Branding in a Hyper-Connected World* and of Alina Wheeler's *Designing Brand Identity*, Jennifer Aaker on brand personality, Jenni Romaniuk of the Ehrenberg-Bass Institute on distinctive brand assets, Nielsen Norman Group on tone of voice, the voice guides of Mailchimp, Atlassian, and Microsoft, the logo guidance of Atlassian, Apple, and GitHub, the GitHub color page, the Material Components theming docs, and Tim Brown on modular scales
- Content design: the GOV.UK content design guidance and style guide, ISO 24495-1 on plain language, Kristina Halvorson and Rachel Lovinger in A List Apart, Nielsen Norman Group on content audits, the inverted pyramid, error messages, and tone of voice, the Mailchimp Content Style Guide, and Diátaxis
- UI/UX design: the Web Content Accessibility Guidelines 2.2 and their Understanding pages, the WCAG evaluation methodology WCAG-EM 2.0, Rosenfeld, Morville, and Arango's *Information Architecture*, Nielsen Norman Group articles, Laws of UX, the Interaction Design Foundation, Wertheimer's 1923 paper on perceptual grouping and a 2012 review of Gestalt research, and MDN
- Platform conventions: the Apple Human Interface Guidelines, the Android design guides, and the Material Components for Android docs
- Design systems: the Design Tokens Format Module 2025.10 and its glossary, and Brad Frost's *Atomic Design*
- Software engineering: the Guide to the Software Engineering Body of Knowledge (SWEBOK) `v4`, which sets the practice areas
- Requirements: the Extreme Programming rules, Gojko Adzic's *Specification by Example*, martinfowler.com on Given When Then, and ISO/IEC/IEEE 29148
- Architecture and design: martinfowler.com, Gregor Hohpe and Bobby Woolf on integration styles, the C4 model site, Michael Nygard's post on architecture decision records, the OpenAPI and AsyncAPI specifications, and the Storybook docs
- Testing: the ISTQB Foundation Level, Model-Based Tester, and Performance Testing syllabi, the software testing chapter of SWEBOK `v4`, NIST SP 800-142 on combinatorial testing, Kent Beck on test-driven development, the test pyramid, integration test, test double, and contract test pages on martinfowler.com, Martin Fowler on non-determinism in tests, *xUnit Test Patterns*, the Pact docs, the testing chapters of *Software Engineering at Google*, Google's papers and blog posts on code coverage, mutation testing, and flaky tests, the Jia and Harman survey of mutation testing, the Luo et al. study of flaky tests, the QuickCheck paper and John Hughes's "How to Specify It!", and Anthropic's guide and engineering post on evaluations
- Construction: martinfowler.com on infrastructure as code and parallel change, The Twelve-Factor App, Edgar Codd's 1970 paper on the relational model, MDN and the GOV.UK Service Manual on progressive enhancement, web.dev on Core Web Vitals, the App Store Review Guidelines, and the Google Play developer policy
- Configuration management: trunkbaseddevelopment.com, the DORA guides, Conventional Commits 1.0.0, martinfowler.com on continuous integration and deployment pipelines, and Semantic Versioning 2.0.0
- Quality: Google's engineering practices guide, martinfowler.com on YAGNI and exploratory testing, Toyota and the Lean Enterprise Institute on the five whys, the Extreme Programming rules on acceptance tests, the Scrum Guide, and ISO/IEC 25010
- Operations: martinfowler.com on continuous delivery, the OpenTelemetry docs, Amplitude and Mixpanel on tracking plans, the Google SRE book and workbook, and the DORA guide to its metrics
- Security: the OWASP Top 10:2025, the OWASP Application Security Verification Standard 5.0.0, the OWASP Secrets Management Cheat Sheet, Code Review Guide, and Web Security Testing Guide, the Threat Modeling Manifesto, Microsoft's threat modeling docs, the CWE Top 25, and CVSS `v4.0`

Several frameworks come from books, such as *Good Strategy/Bad Strategy*, *Inspired*, *Continuous Discovery Habits*, *Obviously Awesome*, *The New Strategic Brand Management*, *Designing Brand Identity*, *Information Architecture*, and *Specification by Example*. A rule cites a page that was read: an article by the author, a publisher excerpt of the book, or, for Kapferer, a peer-reviewed article that describes his model. A node can also cite the publisher page of the book when that page names what the node says, as the page of *Information Architecture* names its four systems. Where a page no longer loads, the node cites a Wayback Machine snapshot of it.

A rule with no `sources` is a judgment call, so read it with more care.

Each directive also states its `basis`, the kind of source behind it. In the domain and the skills:

| `basis`        | Directives | Where they come from                                                                                                                                                                                                                                                                                                                                                                        |
| -------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard`     | 238        | WCAG 2.2, the Design Tokens Format Module, the OWASP Top 10 and ASVS, Conventional Commits, Semantic Versioning, the ISTQB syllabi, and SWEBOK                                                                                                                                                                                                                                              |
| `research`     | 88         | The Gestalt grouping research, Fitts's law, and Hick's law, mostly through Nielsen Norman Group articles, the DORA research, the HEART paper from Google, NIST SP 800-142, the papers on QuickCheck, mutation testing, code coverage, and flaky tests, and the Ehrenberg-Bass Institute's research on distinctive brand assets                                                              |
| `practitioner` | 452        | Named methods and authors: Nielsen Norman Group, WCAG-EM, Apple, Android and Material Components, Brad Frost, MDN, an OWASP cheat sheet, martinfowler.com, Kent Beck, Gerard Meszaros, the Pact docs, Anthropic, Google, Paul Hammant, Simon Brown, Michael Nygard, Adam Wiggins, the voice guides of Mailchimp, Atlassian, and Microsoft, and the product strategy and brand authors above |
| `judgment`     | 26         | No source                                                                                                                                                                                                                                                                                                                                                                                   |

Every governance directive is `judgment`, because the policies come from this project's own design and cite nothing.

The Design Tokens format counts as `standard` even though it is a W3C Community Group report rather than a W3C Recommendation, and its node says so. WCAG-EM is a W3C Group Note, so it counts as `practitioner`.

## How it fits

This is the first real content for the [schema](schema.md), the [format](node-format.md), and the checks. The [compiled outputs](compiled-outputs.md), the [runtime files](runtime-files.md), and the [human interface](human-interface.md) read it. While a seed directive is `proposed`, only `uv run densho build --proposals`, `uv run densho runtime --proposals`, and the site hold it, and each marks it as not in force.

## What it does not check yet

- Whether a rule is right. The checks read form and structure, and a reviewer reads meaning.
- Whether a value in `sources` exists, says what the rule says, or still says it
- The definitions and the body text. The [language checks](language-checks.md) read only directives, triggers, and skill descriptions.
- A `conflicts_with` pair on real content. No seed directive declares one, because no two seed rules truly conflict.
