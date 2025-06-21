from typing import Dict, List, Union, Optional, ClassVar
from pydantic import BaseModel

class DesignSchema(BaseModel):
    """Comprehensive design system schema for extracting UI metadata"""
    
    schema_template: ClassVar[Dict] = {
        "Typography": [
            "Primary, secondary & fallback font families (web-safe or web-hosted)",
            "Weight spectrum to use (e.g., 300, 400, 600, 700)",
            "Heading sizes (H1-H6) with exact px/rem values",
            "Body, sub-body, caption, and micro-copy sizes",
            "Line-height & paragraph spacing rules",
            "Letter-spacing / tracking values by text role",
            "Case usage rules (Title Case, ALL CAPS, small-caps)",
            "Text alignment preferences & max character/line width",
            "Link, hover, visited & focus styles (color, underline, animation)",
            "Font-smoothing / antialiasing guidance (e.g., –webkit-font-smoothing)"
        ],
        "Color & Contrast": [
            "Brand primaries, secondaries, accents (hex/RGB/HSL)",
            "Neutral/gray scale set",
            "Success, warning, error, info colors",
            "Gradient definitions (angle, stops)",
            "Overlay & scrim tints (opacity levels)",
            "Minimum contrast ratios and WCAG targets"
        ],
        "Layout & Grid System": [
            "Maximum content width / full-bleed rules",
            "Column count, gutter width, and margin specs",
            "Responsive breakpoints & how the grid adapts",
            "Vertical rhythm unit (e.g., 4 px or 8 px scale)",
            "Section spacing above/below (hero, feature blocks, footer, etc.)"
        ],
        "Spacing & Sizing Tokens": [
            "Base spacing unit & multiplier scale (e.g., 4-pt, 8-pt)",
            "Standard padding/margin tiers (XS–XL)",
            "Corner-radius scale (buttons, cards, inputs, images)"
        ],
        "Imagery": [
            "Hero image style (photo, illustration, 3-D render)",
            "Subject-matter guidelines & mood (e.g., people-centric, product-focused)",
            "Color treatment (duotone, desaturation, overlays)",
            "Acceptable aspect ratios & cropping rules",
            "Minimum resolution/DPI & file formats (AVIF, WebP, SVG)",
            "Allowed/no-go visual clichés or stock tropes",
            "Watermark or logo overlay rules"
        ],
        "Illustration & Iconography": [
            "Illustration style (flat, outline, skeuomorphic, 3-D, isometric)",
            "Line weight range & corner radius for icons",
            "Filled vs outlined icon usage rules",
            "Icon grid size & padding (e.g., keyed to 24 px)",
            "Animation/hover behavior for icons (spin, color shift, none)"
        ],
        "Logo Usage": [
            "Color variants (full-color, mono-light, mono-dark)",
            "Minimum size & clear-space requirements",
            "Preferred placement(s) on desktop & mobile",
            "Backgrounds the logo may/ may not sit on"
        ],
        "Buttons & Calls-to-Action": [
            "Primary, secondary, tertiary button styles",
            "Padding, min-width & height, corner radius",
            "Text style (size, weight, letter-spacing)",
            "State styles: default, hover, active, focus, disabled",
            "Shadow/elevation or border usage rules",
            "Icon-in-button conventions"
        ],
        "Form & Input Styling": [
            "Field height & internal padding",
            "Border shape (radius, stroke, or none)",
            "Label, helper text & placeholder typography",
            "Focus, hover, error & success states (border, shadow, icon)",
            "Checkbox, radio & switch visual design"
        ],
        "Navigation & Header": [
            "Desktop vs mobile navbar height & padding",
            "Link spacing & separator rules",
            "Hover/active indicators (underline, highlight, color)",
            "Sticky or scroll-hide/show behavior styling",
            "Burger-menu icon style & animation"
        ],
        "Cards / Panels / Containers": [
            "Default background (solid, translucent, glass, gradient)",
            "Border, radius & shadow tiers (e.g., card-1, card-2)",
            "Internal padding and media / text alignment"
        ],
        "Shadows & Elevation": [
            "Layer naming (e.g., Elevation 1-5)",
            "X/Y offset, blur, spread & color opacity per tier",
            "When to swap shadows for borders in dark mode"
        ],
        "Borders & Dividers": [
            "Standard stroke widths & styles (solid, dashed)",
            "Divider thickness & color",
            "Inset vs outset rules"
        ],
        "Motion & Animation": [
            "Primary easing curves (e.g., cubic-bezier)",
            "Duration bands (very-fast <150 ms, normal 200-400 ms, slow >600 ms)",
            "Preferred motion directions (fade-in up, scale-in, etc.)",
            "Scroll-triggered reveal behavior specs",
            "Reduced-motion fallbacks and when to disable animation"
        ],
        "Micro-Interactions": [
            "Button tap ripple or scale effect",
            "Form field shake on error vs color change",
            "Tooltip styling & animation",
            "Loading spinners / skeleton screens style"
        ],
        "Media Blocks (Video / Audio / 3-D)": [
            "Aspect ratio & max width rules",
            "Autoplay, loop, mute defaults & overlay icon style",
            "Poster frame treatment (gradient overlay, play button)",
            "Player control skin (minimal, brand colors)"
        ],
        "Backgrounds": [
            "Solid vs gradient vs pattern hierarchy",
            "Texture use (noise, grain) & opacity limits",
            "Parallax or fixed attachment behavior"
        ],
        "Dark-Mode / High-Contrast Variants": [
            "Token swaps for colors, shadows, borders",
            "Image/illustration adaptations (tinted, inverted)",
            "Focus ring color adjustments"
        ],
        "Accessibility Visuals": [
            "Focus indicator thickness & color",
            "Link underline rules for color-blind safety",
            "High-contrast palette mapping"
        ],
        "Data-Viz & Infographics": [
            "Chart color palette & order",
            "Gridline weight & opacity",
            "Label typography & number formatting rules"
        ],
        "Cursors & Pointer States": [
            "Cursor override for draggable, clickable, custom hover",
            "Pointer animation (subtle grow, color pulse)"
        ],
        "Tone & Mood Descriptors": [
            "Three-to-five adjectives defining the visual vibe (e.g., 'clean, approachable, tech-forward')",
            "Emotional goals (trust, excitement, calm)"
        ],
        "Reusable Brand Motifs": [
            "Shapes, lines, or patterns (e.g., angled lines at 30°, dotted wave)",
            "Frequency & placement guidance"
        ],
        "Favicons & Social Preview Assets": [
            "Favicon shapes, background transparency rules",
            "Open Graph / social card imagery style & typography"
        ]
    } 