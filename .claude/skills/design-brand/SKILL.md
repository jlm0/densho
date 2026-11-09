---
name: design-brand
description: "Define a brand, from its strategy to its logo, colors, type, and guidelines. Use when you define or change the strategy, the visual identity, or the guidelines of a brand. Do not use it for the voice alone (`define-brand-voice`)."
---
<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Design a brand

## Run the skill

1. Run the steps in their order.
2. If the output of a step exists already, skip the step.
3. If a step has a step file, read the step file.
4. Follow each directive of the step.
5. If you need the definition or the notes of a page, read the page.
6. After each step, check its output against each directive of the step.
7. Before you start the next step, correct each part of the output that breaks a directive.

## 1. Define the brand strategy

Step file: [steps/define-the-strategy.md](steps/define-the-strategy.md)

1. Collect the positioning of the product, with its positioning components.
2. If the product has no positioning, run `write-positioning` first.
3. Collect the brand guidelines, the voice and tone guide, and the brand assets that exist.
4. List each section of the brand guidelines that the task creates or changes.
5. Write the six facets of the identity prism.
6. Write the positioning statement from the positioning components.
7. Test the statement with the name of a competitor in place of the name of the brand.
8. Write a test of the statement with people outside the company.

Missing rule: No directive of brand strategy states the purpose, the values, or the promise of the brand.

Missing rule: No directive of brand strategy states what the step gives to the voice and to the visual identity.

Output: The strategy section of the brand guidelines: the six facets of the identity prism and the positioning statement.

## 2. Define the visual identity

Step file: [steps/define-the-visual-identity.md](steps/define-the-visual-identity.md)

1. If step `1` lists no section that this step writes, skip this step.
2. Collect the current brand assets: the logo files, the colors, the typefaces, and samples of their use.
3. Write the logo section: each lockup, the clear space, the minimum sizes, the color versions, and the misuse examples.
4. Write the palette of the color section, with the values for each medium.
5. Assign a role to each color, with a light value and a dark value.
6. Check the contrast of each pair of a container role and its content role.
7. Write the typography section: the typefaces, the type scale with its base and its ratio, and the text styles.

Missing rule: No directive covers the style of the photos, the illustrations, and the icons of the brand.

Output: The logo section, the color section, and the typography section of the brand guidelines.

## 3. Write the brand guidelines

Step file: [steps/write-the-guidelines.md](steps/write-the-guidelines.md)

01. If step `1` lists no section that this step writes, skip this step.
02. Collect the products and the brands of the company.
03. Collect the groups of people who apply the brand, inside and outside the company.
04. If the company has more than one brand, state the architecture type of each product.
05. If the brand has no voice and tone guide, run `define-brand-voice`.
06. Add the voice and tone section from the voice and tone guide.
07. Label each element as `sacred`, `interpretive`, or `customizable`.
08. Add a correct and an incorrect example for each logo rule.
09. Store the colors, the typefaces, and the type scale as design tokens.
10. Link the token files from the guidelines.
11. Give each group of people who apply the brand a section with the rules and the assets that it uses.

Missing rule: No directive states how to choose the architecture type of a new product or an acquired company.

Output: One set of brand guidelines in one online source, with the asset files and the token files beside it.

## Exit checklist

Check each line before you report the brand as done.

- [ ] Each section from step `1` that the task creates or changes has its output.
- [ ] The positioning statement is false with the name of a competitor in place of the name of the brand.
- [ ] Each pair of brand colors for text or controls passes the contrast rules.
- [ ] Each value in the guidelines matches the value in the token files.
- [ ] The report names each directive that the brand misses, and each missing rule that the brand reached.

## Output

- One set of brand guidelines in one online source, with the asset files and the token files beside it. The guidelines hold the strategy, the architecture where it applies, the logo, the colors, the typography, the voice and tone, and the label of each element.
- A list of each directive that the brand misses, with the reason

To check the touchpoints of the brand against the guidelines, run `audit-brand-consistency`.
