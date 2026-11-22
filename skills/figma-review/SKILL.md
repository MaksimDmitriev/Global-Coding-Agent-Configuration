---
name: figma-review
description: Review responsive web pages and native Android or iOS screens and flows against approved Figma designs. Use for implementation parity checks, choosing a design baseline, and practical designer feedback alongside UI and screenshot tests.
---

# Figma UX review

Use the approved Figma frame, components, and tokens as the source of truth for design intent. Review and report by default. Make design or app edits only when requested.

## Compare the same screen and state

- Resolve the target Figma frame, variant, and theme from the user's link or project references. Use any project design map or prior audit to locate frames and code. Confirm the current design and implementation before carrying forward historical findings. If two plausible Figma targets disagree and the choice matters, show the conflict and ask which is approved while continuing with unambiguous areas.
- Inspect the relevant Figma frames, component variants, variables, and prototype transitions using the available Figma tools. Match each platform to its approved Figma variant, viewport, theme, content, and UI state. If platforms share a frame, account for documented platform conventions.
  - **Web.** Match CSS viewport and responsive breakpoints. Check keyboard navigation, visible focus, and hover where relevant.
  - **Android.** Match effective dp layout and sp text sizing at the chosen font scale. Account for system insets and check TalkBack semantics where relevant.
  - **iOS.** Match point-based layout and Dynamic Type settings. Account for safe areas and check VoiceOver semantics where relevant.
- Follow the production UI and state wiring for the selected flow. Reuse existing screenshots, previews, and UI tests as evidence and use a running browser, simulator, emulator, or device build when available. Check whether fixtures bypass production state mapping. Use mocked or simulated states when reviewing hardware connection and command feedback.
- Call a difference confirmed when the approved design and comparable implementation evidence establish it. Report missing design states as design gaps. If a reference or matching render is unavailable, state what you could verify from source and what still needs a matched comparison or runtime check. A passing screenshot test establishes agreement with its stored baseline.

## Recommend a design direction

- Start with the product's main task and the users who perform it. Look for an established system in the approved Figma library, tokens (named reusable values), and repeating components. Check app themes and dependencies for corroboration. A library in the code only proves that the app uses it, so describe what the Figma design actually follows.
- Recommend a baseline the owner can act on. Keep coherent existing patterns and fill important gaps with familiar controls. If there is no coherent baseline, propose a small set of reusable components and styles for a representative screen first. Explain the choice in terms of what users need, such as quick scanning, comfortable touch interaction, or dense data.
- For Android, [Material 3](https://developer.android.com/develop/ui/compose/designsystems/material3) can provide familiar components and theme roles. For iOS, [Apple's Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/) guide familiar native controls and navigation. For web, start with the project's existing component library or styled native controls. [Bootstrap](https://getbootstrap.com/docs/5.3/getting-started/introduction/) or [Tailwind CSS](https://tailwindcss.com/) is an optional web toolkit. Share brand choices and terminology across platforms where appropriate and allow each platform's controls to behave as users expect. Treat a proposed baseline as a Figma decision for the owner to approve.

## Check consistency and usability

- **First impression.** Look at the rendered screen or Figma frame at its intended size before inspecting measurements. Identify what draws the eye first, whether the main task is obvious, and whether spacing, alignment, and contrast make related elements easy to scan. Compare repeated components side by side. Recheck the smallest and widest relevant layouts when a suggestion could change density, wrapping, or where the primary action appears.
- **Spacing.** List distinct values by role in the reviewed scope, such as page padding, card padding, and gaps between related controls. Flag one-off values for the same role, such as 4, 5, 7, and 8 used for equivalent gaps in the platform’s layout units. Check the Figma spacing scale first. If it has none, suggest a small starting scale such as 4, 8, 12, 16, and 24 in the platform’s layout units. Multiples of 4 are a useful starting convention for authored gaps and padding. Verify exceptions by purpose, such as a border, optical alignment, a platform inset, or responsive sizing. Check that related elements sit closer together than separate groups.
- **Typography.** Count distinct styles and show their roles. Check size, line height, weight, and style mapping for equivalent text. For a typical screen, look for a clear hierarchy among screen titles, section titles, body text, and labels. Reuse an existing role when it serves the same purpose. Judge the sizes and count by how well they support hierarchy and readability in the reviewed scope.
- **Color.** Inventory text colors by purpose and theme, such as primary text, supporting text, links, and status. Flag near-duplicates serving the same role, and check that each foreground works on its actual background. Look for a text or icon cue when color conveys important status.
- **Clarity and flows.** Check whether the user can identify the next action, predict what a control does, and recover from wrong turns. Look for extra steps, confusing navigation, and dead ends.
- **Feedback.** Follow relevant loading, success, error, disabled, connection loss, and recovery states. Check whether the app explains what happened and gives an actionable next step.
- **Accessibility.** Check readability, contrast, effective touch targets, and screen-reader labels, roles, and state announcements. Use the applicable platform guidance when reporting a threshold and mark runtime behavior that still needs verification.
- **Consistency.** Compare terminology, control behavior, and repeated components across the screens in scope.

Use existing design tokens, component roles, and platform conventions to judge consistency. Treat counts as a way to spot duplication and weak hierarchy. When Figma itself is inconsistent or could be improved, propose the change for Figma first.

## Report findings

Name the reviewed frame or flow and app revision or build, plus the platforms, states, themes, and sizes actually checked. Lead with the findings that most affect the user's next action or ability to recover.

- **Designer’s assessment** recommends a visual baseline in plain language, says what is already working, and names the highest-impact change to try first. Distinguish the design patterns you can see from standards you propose adopting.
- **Implementation differences** give the expected Figma value or behavior, the observed app value or behavior, the impact, and a concrete correction. Link the Figma node and supporting app evidence such as a source line, screenshot, or test.
- **Design suggestions** identify a usability concern or missing state in Figma and propose a small change to review there. For each important suggestion, show what you observed, why it affects the user, the proposed Figma change, and how to verify the result. Include a short spacing, typography, and text-color inventory when relevant. For example, if equivalent label-to-field gaps are 5, 7, and 8, suggest one 8-unit gap and check the narrow layout for wrapping and comfortable grouping.
- **Verification gaps** name the missing evidence and the smallest check that would resolve the uncertainty. Suggest a targeted UI test when an important interaction or state transition has a specific coverage gap.
