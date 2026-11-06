<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Accessibility

## Directives

No directive is in force at this node.

## Definition

Making a product usable by people with disabilities, including people with low vision, limited movement, or hearing loss. The Web Content Accessibility Guidelines (WCAG) `2.2` state the requirements as testable success criteria at three levels: A, AA, and AAA. A product conforms to a level when it meets each criterion of that level and of the levels below it.

## Notes

These directives cover each success criterion of WCAG `2.2` at level A and AA. Criterion `4.1.1` Parsing is obsolete and removed in WCAG `2.2`, so no directive covers it. Level AAA is left out, because WCAG does not recommend AAA as a general policy for a whole site. Two criteria live in other nodes: Reflow in Responsive design, and Consistent Navigation in Navigation.

Some directives are stricter than the standard, because a rule holds at most one `unless`:

- The contrast rules read large text as `18` points or more. The standard also counts bold text of `14` points as large.
- The target size rule keeps one of the five exceptions of the standard. Spacing, an equivalent control, a target that the browser draws, and an essential size also pass.
- The audio rule asks for a pause control. A volume control that works apart from the system volume also passes.
- The time limit rule leaves out the exceptions for a real-time event and an essential limit. A change must allow at least `10` times the default, and an extension must give `20` seconds of warning and work at least `10` times.
- The flash rule leaves out the general flash and red flash thresholds.
- The pointer rule asks for the up event, and the standard also asks for a way to abort or undo that action. The standard also passes a down event that the up event reverses, and an essential action on the down event.
- The motion rule leaves out the exceptions for an accessibility supported interface and for essential motion.
- The review rule leaves out the option of a check for input errors, and it leaves out test answers.
- The redundant entry rule leaves out re-entry for security, and data that is no longer valid.
- The login rule leaves out object recognition and personal content.

The text spacing rule uses the values of the standard: line height `1.5` times the font size, paragraph spacing `2` times, letter spacing `0.12` times, and word spacing `0.16` times. A change of context is a major change, such as a new window, a move of the focus, or new content that changes the meaning of the page.
