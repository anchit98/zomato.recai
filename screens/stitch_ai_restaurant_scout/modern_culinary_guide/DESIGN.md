---
name: Modern Culinary Guide
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f4'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#5f5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e2dfde'
  on-secondary-container: '#636262'
  tertiary: '#5c5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#757474'
  on-tertiary-container: '#fffcfb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1b'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474747'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  h1:
    fontFamily: lexend
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h2:
    fontFamily: lexend
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h3:
    fontFamily: lexend
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: lexend
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: lexend
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: lexend
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
  label-bold:
    fontFamily: lexend
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  price:
    fontFamily: lexend
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.0'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  container-max: 1200px
  gutter: 20px
---

## Brand & Style

This design system is built on the principles of **Minimalism** and **High-Contrast Boldness**. It prioritizes immediate clarity and appetite appeal through typography and color rather than imagery. The brand persona is energetic, efficient, and reliable, aiming to evoke a sense of urgency and satisfaction. 

The aesthetic relies on "Maximum White Space" to allow the signature red accents to command attention. By stripping away visual noise, the design system ensures that information architecture—prices, ratings, and dish names—remains the primary hero. The result is a clean, editorial-style interface that feels premium yet accessible.

## Colors

The palette is dominated by the signature **Culinary Red**, used strategically for primary actions, branding, and highlighting key information. 

- **Primary Red (#E23744):** Reserved for call-to-action buttons, active states, and critical brand touchpoints.
- **Deep Carbon (#1C1C1C):** Used for primary headlines and body text to ensure maximum WCAG contrast ratios.
- **Slate Grey (#2D2D2D):** Applied to secondary information, metadata, and icons to create a clear visual hierarchy.
- **Pure White (#FFFFFF):** The foundational background color to maintain a fresh, hygienic look.
- **Success Green (#24963F):** Specifically for ratings and "available" indicators, providing a functional contrast to the brand red.

## Typography

The design system utilizes **Lexend** exclusively to leverage its exceptional legibility and modern, geometric structure. As an "images-excluded" system, typography carries the burden of navigation and emotional resonance.

Headlines use heavy weights and tight line-heights to create "visual anchors" on the page. Body text is optimized for long-form reading with generous leading. A specialized "Price" style is defined to ensure costs are immediately scannable. Letter spacing is slightly tightened on large headings for a premium feel, while labels are tracked out for clarity at small sizes.

## Layout & Spacing

The layout employs a **Fixed Grid** system centered on the screen to maintain a structured, editorial feel. A 12-column grid is used for desktop, collapsing to a single column for mobile.

The spacing philosophy follows a strict 4px baseline power-of-two scale. 
- **Vertical Rhythm:** Sections are separated by `xl` (48px) spacing to prevent content density fatigue.
- **Card Padding:** Internal card padding is set to `md` (16px) or `lg` (24px) to ensure text does not feel cramped against borders.
- **Grouping:** Use `sm` (8px) spacing between related text elements (e.g., a dish name and its description).

## Elevation & Depth

This design system avoids heavy drop shadows in favor of **Low-Contrast Outlines** and subtle tonal shifts. Depth is used to signify interactivity and containment:

1.  **Level 0 (Base):** Pure white background.
2.  **Level 1 (Cards):** A 1px border (#E8E8E8). No shadow.
3.  **Level 2 (Hover/Active):** A very soft, diffused shadow (0px 4px 12px rgba(28, 28, 28, 0.08)) is applied to cards to indicate they are clickable.
4.  **Level 3 (Modals/Overlays):** A darker scrim (60% opacity of #1C1C1C) with a medium-soft shadow to isolate focus.

By using borders as the primary containment method, the UI remains crisp and high-contrast, mimicking the layout of a modern physical menu.

## Shapes

The shape language is **Rounded**, using a base radius of 8px (`0.5rem`). This softens the high-contrast typography and creates a friendly, approachable atmosphere.

- **Primary Containers:** 8px radius for standard cards and input fields.
- **Large Components:** 12px or 16px radius for large featured sections or modals.
- **Interactive Small Elements:** Chips and badges may use a "pill" shape (fully rounded) to distinguish them from structural cards.

## Components

### Buttons
- **Primary:** Solid #E23744 with white Lexend Bold text. 8px radius.
- **Secondary:** White background with a 1px #E23744 border and red text.
- **Ghost:** No background or border; red or deep carbon text for low-priority actions.

### Cards
Cards are the primary organizational unit. They feature a 1px #E8E8E8 border, 16px internal padding, and 8px rounded corners. In the absence of images, cards use bold H3 headlines and distinct price tags to create hierarchy.

### Input Fields
Inputs use a white background with a 1px #E8E8E8 border. Upon focus, the border transitions to #1C1C1C or #E23744 with a subtle 2px outer glow of the same color at 10% opacity.

### Chips & Tags
Used for categories (e.g., "Vegetarian," "Fast Food"). These are small, pill-shaped elements with a light grey background (#F8F8F8) and #2D2D2D text. Active states toggle to the primary red.

### Lists & Menus
List items are separated by subtle 1px horizontal dividers (#F0F0F0). Each item should have a clear "Add" or "Action" button aligned to the right to maintain a consistent scan pattern.