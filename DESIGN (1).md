```markdown
# High-End Dark Mode Design System: The Sovereign Analyst Specification

## 1. Overview & Creative North Star: "The Digital Obsidian"
This design system moves beyond the standard "dark mode" toggle. Our Creative North Star is **The Digital Obsidian**—a philosophy that treats the UI not as a flat screen, but as a carved, multi-dimensional space of polished stone and light. 

To break the "template" look, we reject the rigid grid in favor of **Intentional Asymmetry**. Large-scale `display` typography should be used to anchor layouts, often offset from the main content column to create an editorial, high-end magazine feel. We avoid the "boxed-in" look by using depth, light, and atmosphere rather than lines to define the workspace.

---

## 2. Color & Atmospheric Depth
Our palette is rooted in the deep midnight spectrum, utilizing tonal shifts to create a sense of executive authority.

### Core Palette (Material Design Mapping)
- **Surface / Background**: `#0b1326` (The base "Obsidian" layer)
- **Primary (Accent)**: `#adc6ff` (A luminous, professional blue)
- **Secondary**: `#bcc7de` (Cool slate for supporting elements)
- **Tertiary (Success)**: `#4edea3` (Vibrant emerald for growth/positive states)
- **On-Surface (Headers)**: `#dae2fd` (A crisp, near-white blue)
- **On-Surface Variant (Secondary Text)**: `#c2c6d6` (Softened slate for hierarchy)

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning or containment. Boundaries must be defined solely through:
1.  **Background Color Shifts**: Use `surface_container_low` (`#131b2e`) sitting on `surface` (`#0b1326`) to define a sidebar.
2.  **Tonal Transitions**: Use vertical spacing (`spacing-12` or `16`) to let content breathe, allowing the eye to find the natural edge.

### The "Glass & Gradient" Rule
To inject "soul" into the interface, the **Primary CTA** and **Hero Elements** should utilize subtle gradients. Instead of a flat `#adc6ff`, transition from `primary` to `primary_container` (`#4d8eff`) at a 135-degree angle. For floating overlays (Modals, Dropdowns), use **Glassmorphism**: Apply a 70% opacity to your surface token and a `20px` backdrop-blur to allow the "Obsidian" background to glow through.

---

## 3. Typography: The Editorial Voice
We use a dual-typeface system to balance technical precision with executive elegance.

- **The Authority (Manrope)**: Used for `display` and `headline` tiers. Manrope’s geometric yet warm nature feels modern and bespoke. Use `display-lg` (3.5rem) with tight letter-spacing (-0.02em) for hero headlines to command attention.
- **The Utility (Inter)**: Used for `title`, `body`, and `label` tiers. Inter provides maximum legibility for dense analytical data.

**Hierarchy Guidance:**
Always pair a `headline-lg` in pure white (`on_surface`) with a `body-md` in slate (`on_surface_variant`). This high-contrast pairing mimics high-end print journalism and reduces cognitive load in dark environments.

---

## 4. Elevation & Depth: Tonal Layering
In this system, depth is "baked into" the color tokens. We do not use traditional drop shadows for structure.

### The Layering Principle (Bottom to Top)
1.  **Level 0 (Base)**: `surface` (`#0b1326`) - The foundational canvas.
2.  **Level 1 (Sections)**: `surface_container_low` (`#131b2e`) - For large layout areas like sidebars or footers.
3.  **Level 2 (Cards)**: `surface_container` (`#171f33`) - For primary content containers.
4.  **Level 3 (Interactive)**: `surface_container_high` (`#222a3d`) - For hover states or active elements.

### Ambient Shadows & "Ghost Borders"
- **Floating Shadows**: For high-priority floating elements (Modals), use a shadow with a `40px` blur, `0%` spread, and `8%` opacity. The shadow color must be `#000000`, creating a "void" effect rather than a gray smudge.
- **The Ghost Border**: If accessibility requires a container edge, use `outline_variant` (`#424754`) at **15% opacity**. It should be felt, not seen.

---

## 5. Signature Components

### Buttons: The Tactile Light
- **Primary**: A gradient fill (Primary to Primary Container). `0.375rem` (md) corner radius. No border. Text is `on_primary_fixed` (`#001a42`).
- **Secondary**: Ghost style. No fill, `outline` token at 20% opacity. On hover, the background shifts to `surface_bright` (`#31394d`).

### Cards: The Bezel-Less Container
Cards must never have a border. Use `surface_container` and internal padding of `spacing-6` (1.5rem). For nested lists inside cards, use **Vertical White Space** (`spacing-4`) instead of dividers.

### Data Inputs: The Recessed Field
Inputs should feel "carved" into the surface. Use `surface_container_lowest` (`#060e20`) for the field background with a `sm` (`0.125rem`) bottom-accent-only border using the `primary` token during the `focus` state.

### Executive Sidebar
The sidebar should use `surface_container_low` and extend to the full height of the viewport. Navigation items should not have boxes; use a vertical "pill" indicator (`rounded-full`) in `primary` only for the active state, positioned 4px from the left edge.

---

## 6. Do’s and Don’ts

### Do:
- **Use "Space as Structure"**: Trust the spacing scale (`spacing-12`, `spacing-16`) to separate high-level concepts.
- **Embrace Asymmetry**: Align headers to the left while pushing data visualizations to the right to create visual interest.
- **Color with Intent**: Use `tertiary` (`#4edea3`) sparingly. It is a "Success" state or a "Growth" indicator, never a decorative element.

### Don’t:
- **Don't use #000000**: Pure black kills the "Midnight" depth. Always use the `surface` token.
- **Don't use Divider Lines**: If you feel the need for a line, increase the `spacing` token by one level instead.
- **Don't use High-Opacity Shadows**: Shadows should be "ambient air," not heavy ink. Keep opacity below 10%.
- **Don't use 100% Opaque Borders**: This shatters the "Digital Obsidian" illusion and makes the UI look like a legacy enterprise app.