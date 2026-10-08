---
name: To-do
description: A private student task list in a campus study folio.
colors:
  ink: "#172c43"
  muted: "#53657a"
  cover: "#153c65"
  accent: "#2858c8"
  accent-hover: "#1c449f"
  ground: "#f0f4f8"
  sheet: "#ffffff"
  line: "#d8e1eb"
  danger: "#a12838"
  danger-surface: "#fff0f2"
  success: "#236044"
  success-surface: "#edf7f0"
  input-border: "#8798ad"
  outline-border: "#b7c8e7"
  action-hover: "#edf3ff"
typography:
  headline-large:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: "2.25rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-.035em"
  headline:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.5
    letterSpacing: "-.03em"
  title:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.5
  body:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: ".875rem"
    fontWeight: 600
    lineHeight: 1.5
  helper:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: ".8125rem"
    fontWeight: 400
    lineHeight: 1.5
  status:
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif'
    fontSize: ".75rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  control: "8px"
  sheet: "14px"
spacing:
  compact: "8px"
  action-gap: "12px"
  content-gap: "16px"
  section: "24px"
  sheet-inset: "32px"
  page: "48px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.sheet}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
    textColor: "{colors.sheet}"
  button-primary-active:
    backgroundColor: "{colors.cover}"
    textColor: "{colors.sheet}"
  button-outline:
    textColor: "{colors.accent}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  button-quiet:
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  button-delete:
    textColor: "{colors.danger}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  input:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "11px 14px"
  working-sheet:
    backgroundColor: "{colors.sheet}"
    rounded: "{rounded.sheet}"
---

# Design System: To-do

## Overview

**Creative North Star: "Campus Study Folio"**

The Campus Study Folio gives a private task list the feel of a working sheet: cool white surfaces, navy cover material and familiar controls. Its Operate mode uses system UI lettering, direct labels and enough room to act comfortably.

The system stays flat and practical. Ruled rows organize tasks; blue identifies primary actions; completion and errors have both words and color. Authentication pairs a blue introduction with a white form, while editing and recovery remain within the sheet.

**Key Characteristics:**

- Cool white working sheets against a pale blue-gray ground.
- System UI typography and restrained rounded rectangles.
- Ruled task rows with explicit Open and Done labels.
- Inline editing, clear recovery and visible keyboard focus.

## Colors

The palette combines cool paper neutrals with a navy cover and a clear blue action color. The frontmatter owns exact color values.

### Primary

- **Action blue:** accent for primary buttons, links, caret and focus; accent-hover deepens the action on hover.
- **Navy cover:** authentication introduction and brand; also the primary button's pressed state.

### Neutral

- **Ink and muted ink:** main text and secondary explanations.
- **Ground and sheet:** page canvas and white working surfaces.
- **Rule line:** sheet borders and row dividers.
- **Input and outline borders:** defined fields and secondary actions.
- **Action hover:** pale blue feedback for outline and task-status controls.

### Feedback

- **Danger and danger surface:** deletion and validation errors.
- **Success and success surface:** completed task status and success messages. Completion never relies on green alone.

## Typography

The shared font stack is Segoe UI, system-ui, -apple-system, sans-serif. There is no separate display or mono face.

### Hierarchy

- **Large headline:** task-list heading; the auth cover uses the same size and tracking at weight (600).
- **Headline:** authentication and recovery headings; recovery uses line-height (1.25).
- **Title:** add-section and empty-state headings.
- **Body:** task titles and normal copy; long titles wrap anywhere.
- **Label:** field labels and buttons. Secondary section labels also use this size.
- **Helper and status:** field guidance, footer and task-state labels.

At the first narrow threshold, the task-list headline becomes (1.875rem), while auth headings become (1.5rem). At the smallest threshold, recovery headings become (1.5rem).

## Layout

The centered page and header have a maximum width (1104px); the task page caps at (1024px). Desktop page padding is (48px 32px 24px). Authentication uses two columns (.86fr / 1fr), with a navy introduction and white form.

At (700px) and below, auth stacks, the cover's bottom note hides and section insets reduce. At (440px) and below, the add row stacks, task actions move beneath the title with a (52px) left inset, and recovery actions stack. Page side padding becomes (16px).

Task rows use vertical padding (18px), a status control, flexible wrapping title and trailing actions. Shared spacing tokens capture reused gaps and insets; they are not a forced mathematical scale.

**The Working Sheet Rule.** Keep related task controls within one ruled white sheet.

## Elevation & Depth

White sheets and the white navigation bar separate from the pale ground through thin borders. The auth cover provides tonal depth.

**The Flat Surface Rule.** Use borders and color separation for depth; the shipped system has no shadows.

## Shapes

Sheets use the sheet radius; fields, buttons and feedback blocks use the control radius. Borders are thin (1px). SVG outlines supply the compact brand and task-status marks; no raster artwork ships with this system.

## Components

### Buttons

Direct, compact rectangular actions. Buttons have minimum height (44px); task-status controls are (44px × 44px). Primary actions are solid blue, outline actions are transparent with a pale border, quiet actions use muted ink, and delete actions use danger ink. Explicit deletion confirmation uses a solid danger button. Task-row text actions use tighter horizontal padding (12px), reducing to (10px) on the smallest layout.

Hover changes the relevant fill or text. Disabled buttons use opacity (.6) and a wait cursor. Keyboard focus uses an accent outline (3px) with offset (4px).

### Inputs / Fields

White, gently rounded fields have minimum height (48px). Hover strengthens the border to ink; focus changes it to accent; invalid fields use danger. Labels sit above inputs, and helper or error copy stays beside the relevant field. Grouped errors and flash messages use tinted feedback surfaces.

### Navigation

A white horizontal bar contains the navy SVG brand and plain account or authentication actions. Account names wrap rather than forcing overflow; their available width reduces on the smallest layout. A skip link appears on keyboard focus.

### Working Sheet and Task Rows

A single white bordered container joins add and list sections through a rule. Rows use the same divider vocabulary and hold explicit state labels.

**The Visible State Rule.** Pair status color with a readable state label; done titles also receive a strike-through.

Editing replaces its own row with a labeled field and save/cancel actions. Its clip reveal lasts (180ms) with cubic-bezier(.16, 1, .3, 1); reduced-motion removes the animation. Deletion confirmation and recovery offer explicit cancel or return actions.

## Do's and Don'ts

### Do:

- **Do** preserve visible focus, field labels and inline validation.
- **Do** let long task titles wrap and keep task actions reachable on narrow screens.
- **Do** retain the minimum control sizes and reduced-motion behavior.

### Don't:

- **Don't** replace the approved working sheet with dashboard cards.
- **Don't** add imagery or decorative display typography to this Operate interface.
- **Don't** communicate completion or validation through color alone.

