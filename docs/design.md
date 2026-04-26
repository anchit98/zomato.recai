# VibeCheck | Design System & Visual Language

## 1. Design Philosophy
VibeCheck is built on the **"Midnight Premium"** aesthetic—a combination of high-contrast dark mode, glassmorphism, and dynamic depth. The goal is to make restaurant discovery feel cinematic and intelligent rather than transactional.

### Key Pillars:
- **Depth & Translucency**: Using background blurs and noise textures to create layers.
- **Vibrancy**: Subtle but powerful gradients to highlight "vibes."
- **Focus**: Removing clutter to emphasize the AI-generated explanations.

---

## 2. Visual Language

### Glassmorphism
The core of the UI uses a custom "Glass" token system:
- **Background**: `rgba(255, 255, 255, 0.03)`
- **Blur**: `backdrop-filter: blur(12px)`
- **Border**: `1px solid rgba(255, 255, 255, 0.08)`
- **Shadow**: Deep black shadows with a slight indigo tint.

### Grainy Gradients
To avoid a "flat" digital look, the application uses a noise texture overlay:
- **Noise Source**: `grainy-gradients.vercel.app/noise.svg`
- **Effect**: Layered at 20% opacity with a contrast of 150% to give a tactile, high-end feel.

---

## 3. Color Palette

| Name | Hex/RGBA | Usage |
| :--- | :--- | :--- |
| **Midnight** | `#030712` | Main Background |
| **Card Slate** | `#111827` | Base layer for glass elements |
| **Indigo Glow** | `#6366f1` | Primary Actions & Brand |
| **Violet Pulse** | `#a855f7` | Secondary Accents |
| **Amber Gold** | `#f59e0b` | Ratings & Star icons |
| **Glass Border** | `rgba(255,255,255,0.1)`| Borders for inputs and cards |

---

## 4. Typography
- **Primary Font**: `Inter` (Sans Serif)
- **Weight Strategy**: 
  - **900 (Black)**: Hero headlines & Brand.
  - **700 (Bold)**: Card titles & Section headers.
  - **500 (Medium)**: Body text & Inputs.
  - **400 (Regular)**: Explanations & Meta-data.

---

## 5. Component Anatomy

### 5.1 Search Panel
- **Layout**: Horizontal multi-input for desktop, stacked for mobile.
- **Inputs**: Transparent background with bottom-highlighted focus states.
- **CTA**: Full gradient button with a `scale-105` hover interaction.

### 5.2 Recommendation Cards
- **Rank Badge**: Floating top-left with a `premium-gradient`.
- **Stats Grid**: High-contrast icons (Star/Dollar) in tinted background containers.
- **AI Insight Section**: 
  - Uses `line-clamp` logic for truncation.
  - "Read More" micro-interaction with chevron rotation.

---

## 6. Motion & Interaction

### Transition Tokens
We use `framer-motion` for all transitions to ensure "weighted" movement:
- **Page Entry**: Fade-in with 20px upward slide.
- **Hover States**: 
  - Cards: `scale(1.02)` + Border color shift to Indigo.
  - Buttons: `scale(0.95)` on active (click).
- **Loading State**: Shimmer animation using a moving linear gradient from `white/5` to `white/10`.

---

## 7. Responsive Breakpoints
- **Mobile (< 768px)**: Single column, full-width inputs, hidden sidebar (drawer mode).
- **Desktop (> 1024px)**: Grid layout (3 columns), persistent search bar, right-aligned history drawer.
