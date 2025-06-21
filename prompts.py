from design_schema import DesignSchema
import json

class DesignPrompts:
    """Advanced prompt engineering for design system extraction"""
    
    @staticmethod
    def get_system_prompt():
        return """You are an expert UI/UX designer and front-end developer with 15+ years of experience analyzing design systems. 
        You have an exceptional eye for design details and can extract precise technical specifications from visual elements.
        
        Your expertise includes:
        - Typography analysis (font families, weights, sizes, spacing)
        - Color system extraction (brand colors, neutrals, semantic colors)
        - Layout and grid system analysis
        - Component design patterns
        - Accessibility considerations
        - Modern design trends and best practices
        
        You analyze screenshots with the precision of a developer and the aesthetic understanding of a seasoned designer."""

    @staticmethod
    def get_analysis_prompt(schema_json: str):
        return f"""Analyze this website screenshot with expert-level precision and extract comprehensive design system metadata.

        ANALYSIS INSTRUCTIONS:
        1. **Typography Analysis**: Examine all text elements carefully
           - Identify font families by analyzing character shapes, letter forms
           - Determine font weights by observing stroke thickness
           - Measure heading hierarchy and body text sizes
           - Note line-height, letter-spacing, and text alignment patterns

        2. **Color Analysis**: Extract the complete color palette
           - Identify primary, secondary, and accent colors with exact hex values
           - Build the neutral/gray scale progression
           - Note semantic colors (success, warning, error, info)
           - Analyze gradient definitions and overlay treatments

        3. **Layout & Spacing**: Understand the underlying grid system
           - Identify maximum content widths and responsive breakpoints
           - Measure consistent spacing patterns and padding/margins
           - Determine the base spacing unit (4px, 8px scale)
           - Note section spacing and vertical rhythm

        4. **Component Analysis**: Examine UI components in detail
           - Button styles, states, and dimensions
           - Navigation patterns and interactive elements
           - Card/container designs and shadow systems
           - Form elements and input styling

        5. **Visual Design Elements**: Capture the design aesthetic
           - Logo usage and brand applications
           - Iconography style and treatment
           - Image and media handling
           - Background patterns and textures

        6. **Interaction Design**: Note micro-interactions and animations
           - Hover states and transitions
           - Motion design patterns
           - Accessibility considerations

                 RESPONSE FORMAT:
         You MUST return ONLY a single JSON object that follows this exact schema structure. Do not include any markdown text, explanations, or multiple JSON objects. Return only the unified JSON:

         {schema_json}
         
         IMPORTANT: Your response must start with {{ and end with }}. Do not include any text before or after the JSON.

        ANALYSIS DEPTH:
        - Provide specific measurements when possible (px, rem, percentages)
        - Include exact color values (hex, RGB, HSL)
        - Note CSS properties and technical implementation details
        - Capture the design's personality and brand characteristics
        - Consider responsive design patterns and mobile adaptations
        - Include accessibility features and considerations

        QUALITY STANDARDS:
        - Be precise and technical in your analysis
        - Provide actionable design specifications
        - Include context for design decisions
        - Note any innovative or noteworthy design patterns
        - Consider the overall user experience and design cohesion

        Remember: This analysis will be used to recreate the design system, so accuracy and completeness are critical."""

    @staticmethod
    def get_focused_prompt(category: str):
        """Get a focused prompt for specific design categories"""
        focused_prompts = {
            "typography": """Focus specifically on typography analysis:
            - Examine font families, weights, and sizes with precision
            - Measure line-heights and letter-spacing values
            - Identify the typographic hierarchy and scale
            - Note text alignment patterns and max-width constraints
            - Analyze link styles and interactive text elements""",
            
            "colors": """Focus specifically on color analysis:
            - Extract exact hex/RGB values for all colors
            - Build the complete color palette and neutral scale
            - Identify gradient definitions and color relationships
            - Note semantic color usage (success, error, warning, info)
            - Analyze contrast ratios and accessibility compliance""",
            
            "layout": """Focus specifically on layout and spacing:
            - Identify the underlying grid system and breakpoints
            - Measure consistent spacing patterns and rhythm
            - Note container widths and responsive behavior
            - Analyze section spacing and vertical rhythm
            - Document padding and margin patterns""",
            
            "components": """Focus specifically on UI components:
            - Analyze button styles, states, and specifications
            - Examine form elements and input styling
            - Note card designs and container patterns
            - Document navigation and header elements
            - Capture interactive states and micro-interactions"""
        }
        return focused_prompts.get(category, "")

    @staticmethod
    def get_validation_prompt():
        return """Review and validate the design analysis for accuracy and completeness:
        
        1. Check for consistency across similar elements
        2. Ensure all measurements are realistic and precise
        3. Verify color values are accurate and complete
        4. Confirm the design system is cohesive and well-structured
        5. Add any missing details or patterns
        6. Ensure the analysis provides actionable design specifications
        
        Return the validated and refined design system analysis."""

    @staticmethod
    def get_schema_json():
        """Return the schema as a formatted JSON string"""
        schema = DesignSchema()
        return json.dumps(schema.schema_template, indent=2) 