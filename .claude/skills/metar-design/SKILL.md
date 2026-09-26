---
name: metar-design
description: The METAR Reader design system (colors, fonts, spacing, components) and how to build UI with it. Use whenever you create or change anything in templates/ or static/ (pages, cards, buttons, forms, badges, layout, styling), or when the user asks how the app should look.
---

# METAR Reader design system

The UI is plain HTML (Jinja templates) + **one hand-written stylesheet** (`static/style.css`) + a small
vanilla JS file (`static/app.js`). There is **no CSS framework**: don't add Materialize, Bootstrap or Tailwind.

## Source of truth
- `DESIGN.md` (next to this file): the full design spec with color tokens, type scale, spacing, shapes and component rules. Read it before adding a new kind of component.
- `reference.png` (next to this file): the target look for the station page. Open it when you need to match the visual style.
- `static/style.css`: the spec as CSS variables (`:root { --primary … }`) plus every component class. **Reuse these classes. Don't invent new colors or sizes.**

## Rules
- Colors only from the `:root` variables. Flight categories always use `.cat .cat-VFR|MVFR|IFR|LIFR`
  (green / blue / red / purple). Never recolor them.
- Fonts: **Inter** for text, **JetBrains Mono** (`.mono`) for codes, times, raw METAR and units.
- Shapes: cards 8px (`--radius-lg`), buttons/inputs 6px (`--radius`), badges 4px (`--radius-sm`). Only chips and status pills are fully round.
- Icons: Material Symbols Outlined, `<span class="material-symbols-outlined">air</span>`.
- Layout: `.page` (max 1120px) → `.dossier` (8/4 columns, stacks under 1024px) → `.stack`. Metric widgets go in `.metrics` (3 columns, then 2, then 1).
- Must work at ~400px wide. Check it with a narrow browser window.
- Server-rendered: data comes from `briefing.build_briefing()` as `b`. Put new calculations in
  `briefing.py` (with a test in `test_briefing.py`), not in templates or JS.
- JS only for browser-side features (clock, copy, favorites/recent in `localStorage`). Build DOM with
  `textContent`, never `innerHTML` with data.

## Component cheat-sheet (all in style.css)
| Need | Use |
|---|---|
| Card | `.card` + `.card-pad` / `.card-pad-md`, title `.card-title` with icon |
| Primary / secondary button | `.btn .btn-primary` / `.btn .btn-ghost` (add `.btn-lg` for 48px) |
| Small label above a value | `.upper-label` |
| Metric widget | `.card.metric` → `.metric-head`, `.metric-value` (`.big`, `.unit`), `.metric-foot` |
| Good / warning / bad text | `.note .note-good|note-warn|note-bad` |
| Error message | `.alert` |
| Code-ish text | `.mono` · dark raw block: `.raw-box` / `.raw-text` |
| Station list row | `ul.station-list[data-station-list="favorites|recent"]` (filled by app.js) |
| Chips (quick links) | `.chips` > `a.chip` |

## Checking your work
Run `python -m pytest`, then `python app.py`, and **look at the pages in the browser**:
`/`, `/station/KJFK`, `/station/KHIO` (often fog/LIFR), `/station/EGLL` (non-US), `/station/ZZZZ` (error),
`/favorites`, `/recent`, `/guide`, first at desktop width and then at ~400px.
