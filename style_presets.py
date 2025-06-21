#!/usr/bin/env python3
"""
Style presets for image stylization
Contains pre-configured style prompts for various design aesthetics
"""

from typing import List, Dict, Any, Optional

STYLE_PRESETS: List[Dict[str, Any]] = [
    {
        "name": "Neo-Brutalism",
        "prompt": "Raw unfinished neo-brutalist design with stark black #111 backgrounds and punchy primary colors like bright red #FF4433 and cyan #00CFFF paired with white. Typography uses monospace or grotesque sans fonts like Söhne or Space Grotesk in gigantic weights from 700-900. Layout features thick 2-4px solid borders, boxy grids, oversized offsets with no shadows. Imagery includes unedited screenshots, deliberately pixelated icons, and lo-fi GIFs. Motion is abrupt with on-scroll reveals and no easing, hover states only swap background and text colors."
    },
    {
        "name": "Glassmorphism",
        "prompt": "Frosted glass panels floating over vibrant radial gradients from purple #8A2BE2 to cyan #00FFFF with plenty of negative space. Typography uses thin light weights 300-400 with letter-spacing 0.02em for an airy feel. Layout layers translucent cards with backdrop blur filter at 16px and brightness 1.2, creating 3D stacking via translateZ. Features abstract blobs and soft focus photography behind glass panels. Motion includes subtle parallax on cursor with glass cards popping 2px on hover."
    },
    {
        "name": "Claymorphism",
        "prompt": "Soft clay-like 3D design with pastel colors like pink #F5B5FF and yellow #FFF6AC plus gentle neutrals #F8F9FA. Typography uses rounded sans fonts like Baloo 2 or Nunito at medium weights. Layout has thick 8-16px inner padding with 4-8px fully rounded corners at 28-48px border-radius. Features 3D clay figures and hand-modelled icons made in Spline or Blender. Motion includes micro-bounces with spring physics when buttons are tapped and skeleton loaders shaped like blobs. Uses double box-shadow for extruded look with light top-left and dark bottom-right."
    },
    {
        "name": "Cyberpunk Neon Noir",
        "prompt": "Dystopian cyberpunk aesthetic with pure #0A0A0F black base and vivid neon colors hot pink #FF005C, cyan #00F0FF, purple #AC00FF with additive glow using drop-shadow filter. Typography uses condensed uppercase glitched fonts like Orbitron or Angst. Layout features diagonal section cuts with clip-path, terminal-style cards, and vivid glitch dividers. Includes chromatic-aberration photos, render-line cityscapes, and code overlays at 20% opacity. Motion has RGB glitch keyframes on hover and CRT scanline background loops with overlay blend-mode."
    },
    {
        "name": "Vaporwave Retro",
        "prompt": "80s-90s vaporwave aesthetic with teal #00E1F5 to pink #FF77E9 gradients and checkerboard patterns. Typography mixes pixel fonts for navigation, huge serif Times for headlines, and occasional Japanese glyphs. Layout recreates Windows 95 UI chrome with floating divs, dotted borders, and marquee text. Features VHS static overlays, pillars, sunsets, and low-poly dolphins. Motion includes scrolling marquees recreated with CSS keyframes, slow rotation GIFs, and optional background music with mute toggle."
    },
    {
        "name": "Swiss Minimalism",
        "prompt": "Hyper-disciplined Swiss design using only black #000, white #fff, and one red accent #E63946. Typography strictly uses Helvetica Now or Neue Haas Grotesk with tight leading 1.1 for headlines and generous 1.6 for body text. Layout follows 12-column modular grid with baseline rhythm where decimals align to 4px. Features sparse full-bleed editorial photos with no drop shadows. Motion is minimal with fade-ins at 50ms and no parallax. Uses CSS Grid with baseline-grid utility and strictly audited spacing tokens."
    },
    {
        "name": "Maximalist Y2K",
        "prompt": "Loud chaotic Y2K aesthetic with metallic gradients, holographic stickers, and emoji explosions. Typography ironically uses Impact and Comic Sans plus stretched variable fonts. Layout has overlapping layers, sticker sheets, and rotating banner carousels. Features glossy buttons, lens-flare GIFs, and Tamagotchi mascots. Motion includes cursor-follower sparkles, CSS shard wipe transitions, and autoplay loops. Keeps DOM depth manageable and throttles animations on mobile."
    },
    {
        "name": "Dark Luxury",
        "prompt": "High-end cinematic luxury design with #0D0D0D base, deep bronze #C08B55 and muted emerald #1B4537 accents. Typography uses display serif fonts like Canela or Tiempos at 800 weight for H1 with thin grotesque body text. Layout features edge-to-edge hero video, centered typography, and sticky nav that auto-hides. Includes 4K slow-motion product glamour shots with soft bloom lens effects. Motion uses fade-in with opacity blur filter and scroll-triggered 50% speed parallax."
    },
    {
        "name": "Editorial Magazine",
        "prompt": "Sophisticated editorial magazine layout with ivory #FAF9F7 background, charcoal #1A1A1A text, and spot color #DA1212. Typography combines serif headline Recoleta with classic Georgia body at 18-20px and 30px line height. Layout uses CSS multicolumn for long reads, pull-quotes in grid breaks, and drop-cap first letters. Features high-res reportage photography, inline infographics, and captioned galleries. Motion includes scroll-driven progress bar, figure zoom on click, and reading-time indicator."
    },
    {
        "name": "Retro Pixel Art",
        "prompt": "8-bit arcade aesthetic with strict 16-color NES palette on 1px pixel grid. Typography uses bitmap fonts like Press Start 2P with uppercase headers. Layout has fixed-width 960px canvas with tiled repeating backgrounds. Features sprite sheets, tile-based landscapes, and 64x64 character avatars. Motion includes sprite walking loops, health bar scroll progress, and chiptune sound effects on interactions. Uses pixelated image rendering and avoids fractional pixel transforms."
    },
    {
        "name": "Skeuomorphic Realism",
        "prompt": "Realistic skeuomorphic design with desaturated material tones and shadows at 80-degree light angle. Typography uses friendly rounded Avenir font stamped into surfaces via inset text-shadow. Layout creates physical compartments with tear-off corners and embossed toggle switches. Features high-res textures of wood and denim with beveled icons. Motion shows slight depression on click with 2px translateY and page flip micro-animations. Keeps shadows subtle under 8px blur."
    },
    {
        "name": "Motion Scrollytelling",
        "prompt": "Narrative timeline design with neutral #FDFCFB background and story-based palette gradients per chapter. Typography uses large numbers and section labels with system fonts for body text. Layout has full viewport steps with sticky canvas where SVG or WebGL animates. Features data visualizations, animated charts, and Lottie illustrations. Motion uses GSAP or Framer Motion timeline scrubbing tied to scrollY with progressive reveal. Offers linear fallback for reduced motion preference."
    },
    {
        "name": "Immersive 3D WebGL",
        "prompt": "Game-engine quality 3D scene with dark #141414 neutral background to let model colors pop. Typography uses minimal UI labels with monospace small caps for HUD feel. Layout has full-screen canvas with overlay UI cards using blur behind. Features GLB/GLTF models, HDRI reflections, and PBR materials. Motion includes scroll to orbit, click for explode-view, and particle systems on hero load. Built with Three.js and React Three Fiber with loading manager and fallback poster."
    },
    {
        "name": "Split Screen Story",
        "prompt": "Dual narrative split-screen with contrasting halves white #FFFFFF left and dark #222 right or complementary gradients. Typography features bold 200px numeric hero bridging the gutter with mirrored body copy alignment. Layout has sticky halves that swap on scroll with vertical swipe transitions for mobile. Left side shows video while right displays product shots or stat infographics. Motion morphs gutter line on hover and slides halves to reveal CTA drawer."
    },
    {
        "name": "Card Dashboard",
        "prompt": "Data-dense SaaS dashboard with light neutral #F7F7FA base, subtle #0000000F shadows, and accent blue #0066FF. Typography uses Inter or Roboto Mono for numbers with 14-16px body for dense information. Layout uses auto-fit grid with minmax 280px 1fr and draggable rearrangement. Features inline sparklines, mini pie charts, and status badges. Motion includes card drag-and-drop tilt and live-update count-up animations. Implements CSS Variables for theming."
    },
    {
        "name": "Typographic Playground",
        "prompt": "Experimental type-as-art design with monochrome background and section accents like #FF5500 and #00D26A. Typography exploits variable font axes for gravity and width with viewport-max clamps for size. Layout is nearly text-only with giant oversized headlines at 100vw and small footnotes pinned. Features only typographic posters or ASCII art if any imagery. Motion morphs character weight and width on scroll with hover warping letters via SVG filters."
    },
    {
        "name": "Monochrome Noir",
        "prompt": "Moody detective aesthetic in pure black and white with 10-step gray ramp and hidden red #FF3333 accent for CTAs. Typography pairs condensed serif Playfair Display SC with light grotesque body text. Layout has high contrast hero with centered title and vertical bars as section dividers. Features grainy black and white photos with duotone background using multiply blend-mode. Motion includes slow mask-reveal text with film grain overlay canvas."
    },
    {
        "name": "Pastel Soft Gradient",
        "prompt": "Calm wellness design with diagonal multi-stop gradients from pink #FDEBFB to mint #D4F7F5 to yellow #FFFCD1. Typography uses elegant sans-serif Galano Grotesque at lightweight 300 with letter-spacing +0.5px. Layout has wide 1440px container with 64px breathing space throughout. Features soft-shadow product renders with floating SVG petals or shapes. Motion includes fade-up with slight 1.02 scale entrance and continuous 10-second gradient background shift."
    },
    {
        "name": "Photo-Led Minimal",
        "prompt": "Huge storytelling photography dominates with micro-copy only, where photo dictates palette with white or solid #141414 overlay at 50% opacity. Typography uses one weight and size in giant scale with body copy hidden until scroll. Layout has 100vh hero with cover object-fit and transparent navbar becoming sticky solid after 80px scroll. Features art-directed hero images randomized server-side per visit. Motion includes subtle Ken Burns zoom on hero with slide-down nav entrance."
    },
    {
        "name": "AI-Generated Dynamic",
        "prompt": "Ever-changing user-personalized design with base palette derived from user data or time of day while ensuring WCAG compliance algorithmically. Typography uses system font stack for performance with dynamic weight adjustments via variable font axes. Layout includes placeholders for real-time generated images like diffusion-model paintings and stable diffusion textures with live prompt overlay. Motion features regenerate button that morphs artwork with subtle shimmer during generation. Streams base64 images with queued requests and provides freeze theme toggle."
    }
]


def get_all_style_prompts() -> List[str]:
    """Get all style prompts as a list"""
    return [style["prompt"] for style in STYLE_PRESETS]


def get_all_style_names() -> List[str]:
    """Get all style names"""
    return [style["name"] for style in STYLE_PRESETS]


def get_style_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific style preset by name"""
    for style in STYLE_PRESETS:
        if style["name"].lower() == name.lower():
            return style
    return None


def get_random_style() -> Dict[str, Any]:
    """Get a random style preset"""
    import random
    return random.choice(STYLE_PRESETS)
