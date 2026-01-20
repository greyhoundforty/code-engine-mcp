# Example Apps Color Scheme

Both the Python (Flask) and Go example apps use a retro CRT aesthetic inspired by the McElroy Entertainment System.

## Color Palette

### Background
- **Primary Background**: `linear-gradient(135deg, #0a2e2e 0%, #1a4a4a 100%)`
  - Dark teal gradient creating depth
- **Container Background**: `rgba(10, 46, 46, 0.8)`
  - Semi-transparent overlay for layering

### Text Colors
- **Primary Text**: `#00ffcc` (Bright cyan/mint green)
  - Used for labels, body text, and values
- **Header Background**: `linear-gradient(90deg, #00ffcc 0%, #00cc99 100%)`
  - Cyan to teal gradient
- **Header Text**: `#0a2e2e` (Dark teal)
  - High contrast against bright background

### Accents
- **Border/Accent**: `#ff1493` (Hot pink/magenta)
  - Used for container borders and labels
- **Status Indicator**: `#00ff00` (Bright green)
  - Pulsing dot for online status
- **Info Item Border**: `#00ffcc` (Cyan)
  - Left border accent for info cards

### Effects
- **Glow Shadow**: `rgba(0, 255, 204, 0.3)` and `rgba(255, 20, 147, 0.2)`
  - Animated glow effect around container
- **Info Item Background**: `rgba(0, 255, 204, 0.1)`
  - Subtle cyan tint for info cards

## Typography
- **Font Family**: `'Courier New', monospace`
  - Retro terminal/CRT aesthetic
- **Header Font Size**: `2em`
- **Value Font Size**: `1.2em`
- **Label Font Size**: `0.85em`

## Animations
- **Glow Animation**: 2s ease-in-out infinite alternate
- **Pulse Animation**: 1.5s ease-in-out infinite (for status indicator)

## Design Philosophy
The design evokes a 1970s-1980s CRT terminal aesthetic with:
- Monospace typography
- High-contrast cyan text on dark backgrounds
- Pink/magenta accent borders (reminiscent of VHS packaging)
- Glowing effects simulating CRT phosphor persistence
- Geometric layouts with rounded corners for modern polish
