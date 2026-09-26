---
name: AeroBrief METAR
colors:
  surface: '#fbf8ff'
  surface-dim: '#dad9e3'
  surface-bright: '#fbf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f2fc'
  surface-container: '#eeedf7'
  surface-container-high: '#e8e7f1'
  surface-container-highest: '#e3e1eb'
  on-surface: '#1a1b22'
  on-surface-variant: '#444653'
  inverse-surface: '#2f3037'
  inverse-on-surface: '#f1f0fa'
  outline: '#757684'
  outline-variant: '#c4c5d5'
  surface-tint: '#3755c3'
  primary: '#00288e'
  on-primary: '#ffffff'
  primary-container: '#1e40af'
  on-primary-container: '#a8b8ff'
  inverse-primary: '#b8c4ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#003272'
  on-tertiary: '#ffffff'
  tertiary-container: '#00489e'
  on-tertiary-container: '#9cbbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#b8c4ff'
  on-primary-fixed: '#001453'
  on-primary-fixed-variant: '#173bab'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#fbf8ff'
  on-background: '#1a1b22'
  surface-variant: '#e3e1eb'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-raw-metar:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 22px
  label-telemetry:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
  label-badge:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
  caption:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-md: 1.5rem
  margin: 1rem
  margin-md: 2rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
---

## Brand & Style

This design system delivers an authoritative, high-efficiency flight operations utility built for pilots, dispatchers, flight instructors, and aviation enthusiasts. It draws direct inspiration from modern flight deck EFBs (Electronic Flight Bags) and tactical dispatch tools such as ForeFlight, FlightAware, and Windy.

The core aesthetic combines **Corporate / Modern utilitarianism** with **precision data density**:
- **Clarity over decorative flourish**: Visual structures minimize cognitive load during pre-flight briefings and quick turnarounds.
- **Flight Category Primacy**: Standardized FAA/ICAO flight rule categories (VFR, MVFR, IFR, LIFR) serve as immediate visual anchors using unmistakable status cues.
- **Dual-nature presentation**: Raw telecommunication strings (ICAO METAR/TAF codes) coexist alongside decoded human-readable metrics with zero ambiguity.
- **Aviation Discipline**: High legibility, crisp contrast ratios meeting WCAG AAA requirements for essential telemetry, monospaced tabular figures for runway and altimeter data, and structural grid rhythm.

## Colors

The palette is engineered around high-contrast cockpit readability, establishing a foundational deep navy canvas and crisp aviation blue accents against brilliant neutral surfaces.

### Primary Roles
- **Primary (`#1e40af` - Aviation Blue)**: Dedicated to primary interactive elements, brand topbars, active search triggers, and key navigational landmarks.
- **Secondary (`#0f172a` - Deep Slate / Cockpit Dark)**: Utilized for high-priority typography, telemetry headers, structural borders, and dark-surface counterweights.
- **Tertiary (`#3b82f6` - Sky Accent)**: Interactive focus rings, secondary badges, active tab underlines, and link states.
- **Neutral Canvas (`#f8fafc` & `#ffffff`)**: Crisp, glare-resistant surfaces separating background canvas from elevated flight cards.

### Domain-Specific Flight Category Tokens
Aviation meteorological categories must remain strictly standardized:
- **VFR (Visual Flight Rules)**: `#16a34a` (Green) with `#f0fdf4` tint background.
- **MVFR (Marginal VFR)**: `#2563eb` (Blue) with `#eff6ff` tint background.
- **IFR (Instrument Flight Rules)**: `#dc2626` (Red) with `#fef2f2` tint background.
- **LIFR (Low IFR)**: `#9333ea` (Magenta / Purple) with `#faf5ff` tint background.

Text colors on light tinted badges use their respective dark 800-series tone (`#166534`, `#1e40af`, `#991b1b`, `#6b21a8`) to ensure 4.5:1+ contrast compliance.

## Typography

The typographic hierarchy is split intentionally across two primary typefaces:
1. **Inter**: Handles all operational titles, humanized decoded weather reports, form labels, and general body copy. Inter's tall x-height and neutral geometric proportions ensure rapid reading under motion or fluctuating screen brightness.
2. **JetBrains Mono**: Dedicated exclusively to raw ICAO alphanumeric strings (e.g. `KPDX 241953Z 31008KT 10SM CLR 18/06 A3012`), airport codes, Zulu timestamps, wind vectors, and altimeter units. This prevents character misinterpretation (e.g., distinguishing `0` from `O`, `1` from `I`).

Letter tracking is kept tight on headlines (`-0.015em`) for modern density, and loosened slightly on mono telemetry (`+0.02em`) for distinct character isolation.

## Layout & Spacing

The layout operates on an 8pt architectural rhythm with a strict, responsive 12-column grid.

### Layout Model
- **Max Content Width**: 1120px for desktop single-station briefings and multi-station comparison boards, preventing eye fatigue from wide horizontal telemetry scanning.
- **Top Application Bar**: Fixed height 56px, containing brand mark, Zulu clock indicator, and fast ICAO switcher.
- **Breakpoints**:
  - `Mobile (<640px)`: Single column layout. 16px margins, 12px card padding, search input stacks vertically with primary action button.
  - `Tablet (640px - 1024px)`: 6-column grid, 24px margins. Data cards support 2-up comparison.
  - `Desktop (>1024px)`: 12-column grid. Flight card features a dominant 8-column primary decoded telemetry readout flanked by a 4-column side widget for raw METAR, runway wind crosswind calculator, and station details.

### Spacing Tokens Application
- `space-xs` (4px): Inner badge padding, icon-to-text inline spacing.
- `space-sm` (8px): Form input inner vertical padding, tight metric label-to-value gaps.
- `space-md` (16px): Standard component internal padding, card internal grid gap.
- `space-lg` (24px): Card-to-card vertical flow spacing, section headers.
- `space-xl` (32px): Canvas section grouping.

## Elevation & Depth

Visual hierarchy uses a refined **tonal layering system coupled with crisp structural outlines**, avoiding muddy or exaggerated shadows to ensure clarity in field environments.

### Surface Tiers
- **Canvas Base (`Level 0`)**: `#f1f5f9` (Cool Slate 100). The foundational backdrop that sets up high contrast with active flight cards.
- **Primary Card Surface (`Level 1`)**: `#ffffff`. Bounded by a razor-thin border `1px solid #e2e8f0` and an ambient shadow `0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.03)`.
- **Raised Interactive / Popover Panels (`Level 2`)**: `#ffffff` elevated with `0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.03)` with a `1px solid #cbd5e1` outline for quick airport search dropdowns and condition overlays.
- **Inset Telemetry Container (`Level Inset`)**: `#f8fafc` with an inner border `1px solid #e2e8f0` used for enclosing raw METAR/TAF blocks and tabular runway data.

## Shapes

The design system employs **Level 1 (Soft)** shape geometry. 

- **Containers & Flight Cards**: Standard radius of `0.375rem` (6px) to `0.5rem` (8px), maintaining an instrumental, avionics-grade demeanor. Rounded pill shapes are prohibited for containers to avoid consumer-toy aesthetics.
- **Flight Category Badges & Tags**: Fixed `0.25rem` (4px) rounded corners, ensuring status indicators look crisp and tabular.
- **Form Controls & Buttons**: Matched at `0.375rem` (6px) for an integrated cockpit instrument aesthetic.

## Components

### Buttons
- **Primary Button**: Background `#1e40af`, text `#ffffff`, height 42px, padding `0 1.25rem`, font-weight 600. Focus ring: `0 0 0 3px rgba(59, 130, 246, 0.35)`. Hover: `#1d4ed8`.
- **Secondary / Ghost Button**: Background transparent, border `1px solid #cbd5e1`, text `#0f172a`, hover background `#f8fafc`.

### Search Input Field (ICAO Quick Lookup)
- **Container**: White background, `1px solid #cbd5e1`, 44px height, corner radius 6px.
- **Floating Label / Placeholder**: Clear 14px text showing standard format (`e.g., KJFK, EGLL, KLAX`).
- **Typography**: Text typed into the field is automatically capitalized and rendered in `JetBrains Mono` at 16px with letter-spacing `0.05em`.
- **Leading Icon**: High-contrast search or airport beacon icon in `#64748b`.

### Flight Category Badges
- **VFR**: Background `#dcfce7`, text `#15803d`, border `1px solid #bbf7d0`.
- **MVFR**: Background `#dbeafe`, text `#1d4ed8`, border `1px solid #bfdbfe`.
- **IFR**: Background `#fee2e2`, text `#b91c1c`, border `1px solid #fecaca`.
- **LIFR**: Background `#f3e8ff`, text `#7e22ce`, border `1px solid #e9d5ff`.
- Badges must consistently display the category abbreviation in bold uppercase with accompanying criteria tooltip (e.g. `VFR: CIG > 3000' & VIS > 5SM`).

### Weather Cards & Metric Widgets
- Decoded data points (Wind, Visibility, Altimeter, Temperature, Dew Point, Ceiling) sit inside a clean 2x3 or 3x2 modular card grid.
- Each widget includes a subtle uppercase label (11px, `#64748b`), followed by a primary numeric value in 20px bold `Inter`, accompanied by units in 13px mono (e.g. `12 kts`, `29.92 inHg`, `+18°C`).

### Raw METAR Container
- Dedicated terminal block using `#0f172a` (Cockpit Slate) background with `#38bdf8` and `#f8fafc` monospaced text, equipped with a 1-click "Copy ICAO string" button in the upper corner.