---
name: Facts-First Financial Intelligence
colors:
  surface: '#f3fbf5'
  surface-dim: '#d4dcd6'
  surface-bright: '#f3fbf5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eef6ef'
  surface-container: '#e8f0ea'
  surface-container-high: '#e2eae4'
  surface-container-highest: '#dce4de'
  on-surface: '#161d1a'
  on-surface-variant: '#3c4a43'
  inverse-surface: '#2a322e'
  inverse-on-surface: '#ebf3ec'
  outline: '#6c7a73'
  outline-variant: '#bbcac1'
  surface-tint: '#006c4f'
  primary: '#006c4f'
  on-primary: '#ffffff'
  primary-container: '#01b386'
  on-primary-container: '#003d2c'
  inverse-primary: '#50ddad'
  secondary: '#386754'
  on-secondary: '#ffffff'
  secondary-container: '#baeed5'
  on-secondary-container: '#3e6e59'
  tertiary: '#a23d35'
  on-tertiary: '#ffffff'
  tertiary-container: '#f27a6e'
  on-tertiary-container: '#691411'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#71fac8'
  primary-fixed-dim: '#50ddad'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#baeed5'
  secondary-fixed-dim: '#9fd1b9'
  on-secondary-fixed: '#002115'
  on-secondary-fixed-variant: '#1f4f3d'
  tertiary-fixed: '#ffdad6'
  tertiary-fixed-dim: '#ffb4ab'
  on-tertiary-fixed: '#410002'
  on-tertiary-fixed-variant: '#822620'
  background: '#f3fbf5'
  on-background: '#161d1a'
  surface-variant: '#dce4de'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
  data-metric:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system embodies high-conviction clarity, institutional rigor, and friction-free comprehension. Tailored for an authoritative Mutual Fund and Stock FAQ Assistant, the interface prioritizes factual transparency over speculative excitement. It strips away emotional cues in favor of crisp visual logic, immediate scannability, and regulatory precision.

### Aesthetic Direction
The style merges **Modern FinTech Precision** with **Minimalist Utility**, drawing from the structural discipline of Stripe, the keyboard-first craftsmanship of Linear, and the approachable directness of Groww. 

- **Trust Through Structure:** Rigid layout alignment, unambiguous hierarchy, and clinical typography eliminate visual ambiguity.
- **Calm, High-Information Density:** White surfaces paired with micro-borders allow dense financial facts, expense ratios, lock-in periods, and NAV historical metrics to be absorbed without cognitive overload.
- **Controlled Accents:** The vibrant emerald green is reserved strictly for affirmative status, verified primary actions, and factual positive indicators—never as decorative fill.

## Colors

The palette is engineered around high contrast, legible legibility, and regulatory distinction. The balance enforces a crisp, institutional light-first canvas.

### Palette Architecture
- **Primary Accent (`#01B386`):** Used for key conversational affordances, active filters, verified data pills, and primary interactive buttons. Represents capital health, verified fact-checking, and directional confidence.
- **Secondary (`#51816C`):** Muted Sage. Used for authoritative section titles, question headers, and primary metrics to command reading order.
- **Tertiary (`#F27A6E`):** Coral Alert. Paired with background fill for mandatory regulatory disclaimers, risk factors, SEBI/SEC citations, and market volatility notices.
- **Body Neutral (`#717974`):** Slate Neutral. Optimized for high sustained reading comfort in dense FAQ responses, prospectus summaries, and numerical tables.
- **Caption & Metadata Neutral (`#7C7E8C`):** Muted cool slate for timestamps, source references, footnotes, and tertiary labels.
- **Surface Canvas (`#F9FAFB`):** Cool, crisp off-white backdrop that prevents eye strain.
- **Surface Elevation (`#FFFFFF`):** High-purity white used for floating cards, conversational modules, and factual metric tiles.
- **Structural Outlines (`#EAECEF`):** Subtle dividers and boundary borders creating spatial separation without visual friction.

## Typography

The typography leverages a dual-type strategy: **Plus Jakarta Sans** for structural headers, search queries, and key monetary metrics; **Inter** for conversational prose, answers, and data grids.

### Implementation Guidelines
- **Numerical Alignment:** All tabular financial data, returns, expense percentages, and dates must use font feature settings `font-variant-numeric: tabular-nums` to maintain absolute spatial alignment across lists.
- **Hierarchy Enforcements:** Never style narrative body text above `16px`. Financial answers require concise reading blocks; line lengths must be constrained to a maximum of 68 characters (`68ch`) for sustained comprehension.
- **Regulatory Text:** Risk factors and compliance footnotes must render in `label-sm` or `body-sm`, retaining full opacity to respect strict accessibility guidelines.

## Layout & Spacing

The layout is grounded in a clean 8pt grid with 4pt half-steps for compact data rows, metadata groupings, and input containers.

### Grid & Structure
- **Desktop (1024px+):** Fixed central workspace with a max-width of `1200px`. A 12-column layout splits 4 columns for search history, popular tickers, and category indexing, and 8 columns for conversational FAQ discovery and data sheets.
- **Tablet (768px – 1023px):** Fluid grid with 8 columns, 24px margins, and collapsible secondary navigation panels into sliding sheet drawers.
- **Mobile (< 768px):** Single-column stacked stream with 16px lateral margins. Input bars dock firmly to the bottom viewport boundary with safe area insets.

### Spacing Principles
- Gaps between modular facts inside a card must not exceed `space-md` (12px).
- Spacing between disparate question threads relies on `space-xl` (32px) to ensure clear semantic separation.

## Elevation & Depth

This design system avoids heavy shadows, skewing instead toward subtle physical edges defined by low-contrast borders complemented by micro-ambient drop shadows.

### Elevation Hierarchy
1. **Level 0 (Base Canvas):** `#F9FAFB`. Passive workspace backdrop without shadows or borders.
2. **Level 1 (Default Containers & Fact Cards):** Surface `#FFFFFF`, border `1px solid #EAECEF`, shadow `0 2px 8px rgba(0, 0, 0, 0.04)`. Used for answered FAQ cards, fund snapshot blocks, and search suggestions.
3. **Level 2 (Hover & Focus States):** Surface `#FFFFFF`, border `1px solid #01B386`, shadow `0 4px 14px rgba(0, 0, 0, 0.06)`. Signifies user interaction and selection intent.
4. **Level 3 (Modals, Overlays, and Docked Assistant Trays):** Surface `#FFFFFF`, border `1px solid #EAECEF`, shadow `0 12px 32px rgba(81, 129, 108, 0.08)`. Ensures prominent elevation without muddying background text.

## Shapes

The design system employs moderate roundedness (`0.5rem` / 8px base) to strike the right balance between modern consumer FinTech friendliness and institutional credibility.

### Shape Scale Rules
- **Base Components (Inputs, Buttons, Cards, Alert Banners):** Standard 8px radius (`roundedness: 2`).
- **Data Chips & Category Badges:** Pill-shaped (fully rounded `9999px`) to distinguish interactive filters and tags from rectangular data cards.
- **Tooltips & Micro-badges:** 4px radius (`rounded-sm`) for compact, precise labeling.

## Components

### Buttons
- **Primary:** Background `#01B386` (hover `#01a077`), text `#FFFFFF`, font `label-md`. Height `40px` (desktop) / `44px` (mobile). Subtle focus ring `0 0 0 3px rgba(1, 179, 134, 0.25)`.
- **Secondary / Ghost:** Transparent surface with border `1px solid #EAECEF`, text `#51816C` (hover background `#F9FAFB`, hover border `#D3D6DC`).
- **Destructive / Flag:** Plain text button `#F27A6E` for compliance reporting or dispute filings.

### Inputs & Search Bars
- **FAQ Assistant Search:** Height `48px`, background `#FFFFFF`, border `1px solid #EAECEF`, text `#51816C`, placeholder `#7C7E8C`. Contains a persistent keyboard shortcut pill (`⌘K`) on the trailing edge. On focus, transition border color to `#01B386` with a `2px` outer halo.

### Cards & Fact Modules
- Pure white container with `1px solid #EAECEF` and shadow `0 2px 8px rgba(0,0,0,0.04)`.
- **Header:** Features ticker / scheme name in `headline-sm` (`#51816C`), alongside a category pill.
- **Body:** Answer text in `body-md` (`#717974`).
- **Footer:** Separated by a `1px` subtle divider, containing last-updated timestamp (`#7C7E8C`), data source badge, and feedback action buttons.

### Chips & Filter Pills
- Unselected: Background `#FFFFFF`, border `1px solid #EAECEF`, text `#717974`.
- Selected: Background `rgba(1, 179, 134, 0.12)`, border `1px solid #01B386`, text `#01B386` with weight `600`.

### Compliance & Risk Warning Banners
- Surface: `#FFF8E6`.
- Border: `1px solid rgba(242, 122, 110, 0.3)`.
- Text: `#F27A6E`.
- Leading icon: Muted warning triangle. Used exclusively for mandatory statutory declarations (e.g., "Mutual fund investments are subject to market risks...").

### Data Comparison Lists & Metrics
- Split alternating key-value pairs separated by hairline borders (`#EAECEF`).
- Metric Label: `body-sm` (`#7C7E8C`).
- Metric Value: `label-md` or `data-metric` (`#51816C`), aligned right with monospace numerical styling.