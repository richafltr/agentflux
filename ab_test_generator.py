"""
A/B Testing Generator
Creates 4 different UI variations for A/B testing using component maps and GPT-Image-1 native image generation

RECENT ENHANCEMENTS:
- Enhanced design preservation: Strict constraints to prevent color/style drift
- Dimension optimization: Automatic landscape format selection for desktop layouts
- Layout-only transformations: Focus on rearrangement without redesign
- GPT-Image-1 integration: Direct screenshot editing with preservation instructions

DIMENSION LIMITATIONS:
- GPT-Image-1 only supports: 1024x1024, 1024x1536, 1536x1024
- Cannot generate original dimensions like 1920x6179
- Uses 1536x1024 landscape for desktop layouts (best available)
- Focuses on hero section transformation within available space
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI

from config import Config


class ABTestGenerator:
    """Generates A/B testing variations from component maps"""

    # 4 Most Common A/B Testing Patterns
    AB_TEST_PATTERNS = {
        "1": {
            "name": "Hero-First Layout",
            "description": "Prominent hero section with clear CTA, minimal navigation",
            "layout_strategy": "hero_dominant",
            "key_changes": [
                "Large hero section (60% of viewport)",
                "Single primary CTA button",
                "Minimal navigation menu",
                "Social proof below hero"
            ]
        },
        "2": {
            "name": "Feature-Grid Layout",
            "description": "Grid-based feature showcase with multiple CTAs",
            "layout_strategy": "feature_grid",
            "key_changes": [
                "3-column feature grid",
                "Multiple CTA buttons",
                "Tabbed navigation",
                "Testimonials sidebar"
            ]
        },
        "3": {
            "name": "Content-Heavy Layout",
            "description": "Information-rich design with detailed explanations",
            "layout_strategy": "content_rich",
            "key_changes": [
                "Detailed product descriptions",
                "FAQ section prominent",
                "Multiple content blocks",
                "Secondary navigation"
            ]
        },
        "4": {
            "name": "Conversion-Optimized Layout",
            "description": "Focused on conversion with urgency and social proof",
            "layout_strategy": "conversion_focused",
            "key_changes": [
                "Urgency indicators (limited time)",
                "Social proof badges",
                "Sticky CTA button",
                "Minimal distractions"
            ]
        }
    }

    def __init__(self):
        self.config = Config()
        self.client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)

    async def generate_ab_variations(
        self,
        component_map: Dict[str, Any],
        selected_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate A/B testing variations from component map

        Args:
            component_map: The component analysis and React code
            selected_pattern: Optional specific pattern (1-4), if None generates all

        Returns:
            Complete A/B testing variations with images and prompts
        """
        print("🧪 Starting A/B test variation generation...")

        # If no pattern selected, ask user
        if not selected_pattern:
            selected_pattern = self._get_user_selection()

        # Generate variations based on selected pattern(s)
        if selected_pattern == "all":
            variations = await self._generate_all_variations(component_map)
        else:
            variations = await self._generate_single_variation(component_map, selected_pattern)

        # Create final A/B test package
        ab_test_package = {
            "metadata": {
                "original_url": component_map["metadata"]["url"],
                "generation_timestamp": datetime.now().isoformat(),
                "selected_pattern": selected_pattern,
                "total_variations": len(variations)
            },
            "original_analysis": component_map,
            "variations": variations,
            "comparison_metrics": self._generate_comparison_metrics(variations)
        }

        print(f"✅ Generated {len(variations)} A/B test variations!")
        return ab_test_package

    def _get_user_selection(self) -> str:
        """Interactive user selection for A/B test patterns"""
        print("\n🎯 Select A/B Testing Pattern:")
        print("=" * 50)

        for key, pattern in self.AB_TEST_PATTERNS.items():
            print(f"{key}. {pattern['name']}")
            print(f"   {pattern['description']}")
            print(f"   Changes: {', '.join(pattern['key_changes'][:2])}...")
            print()

        print("5. Generate ALL variations (recommended)")
        print("=" * 50)

        while True:
            choice = input("Enter your choice (1-5): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            elif choice == "5":
                return "all"
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")

    async def _generate_all_variations(self, component_map: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all 4 A/B testing variations"""
        variations = {}

        # Generate all patterns in parallel
        tasks = []
        for pattern_id in self.AB_TEST_PATTERNS.keys():
            task = self._create_variation(component_map, pattern_id)
            tasks.append((pattern_id, task))

        # Execute all tasks
        for pattern_id, task in tasks:
            try:
                variation = await task
                variations[f"variation_{pattern_id}"] = variation
                print(
                    f"  ✅ Generated variation {pattern_id}: {variation['name']}")
            except Exception as e:
                print(f"  ❌ Failed to generate variation {pattern_id}: {e}")

        return variations

    async def _generate_single_variation(self, component_map: Dict[str, Any], pattern_id: str) -> Dict[str, Any]:
        """Generate a single A/B testing variation"""
        variation = await self._create_variation(component_map, pattern_id)
        return {f"variation_{pattern_id}": variation}

    async def _create_variation(self, component_map: Dict[str, Any], pattern_id: str) -> Dict[str, Any]:
        """Create a single A/B testing variation"""
        pattern = self.AB_TEST_PATTERNS[pattern_id]

        print(f"  🔄 Creating {pattern['name']} variation...")

        # Step 1: Generate modified component structure
        modified_components = await self._modify_components(component_map, pattern)

        # Step 2: Generate new React code for the variation
        variation_react_code = await self._generate_variation_react_code(modified_components, pattern)

        # Step 3: Create image modification prompt for GPT-Image-1
        image_prompt = self._create_image_modification_prompt(
            component_map, pattern, modified_components)

        # Step 4: Generate variation image using original screenshot + modifications
        variation_image = await self._generate_variation_image_with_screenshot(component_map, image_prompt, pattern)

        # Step 5: Quality check and potentially regenerate if needed
        final_image = variation_image
        if variation_image.get('local_path') and not variation_image.get('error'):
            quality_check = await self._quality_check_image(variation_image['local_path'])

            # If quality issues found and regeneration needed, try to improve
            if quality_check.get('regeneration_needed', False):
                improved_image = await self._regenerate_with_feedback(
                    variation_image['local_path'],
                    image_prompt,
                    quality_check,
                    pattern,
                    component_map
                )

                # Use improved image if successful
                if improved_image.get('local_path') and not improved_image.get('error'):
                    final_image = improved_image
                    print(
                        f"    ✨ Using quality-improved image for {pattern['name']}")

            # Add quality check results to image metadata
            final_image['quality_check'] = quality_check

        # Step 6: Create variation package
        variation = {
            "id": pattern_id,
            "name": pattern["name"],
            "description": pattern["description"],
            "layout_strategy": pattern["layout_strategy"],
            "key_changes": pattern["key_changes"],
            "modified_components": modified_components,
            "react_code": variation_react_code,
            "image_prompt": image_prompt,
            "generated_image": final_image,
            "expected_improvements": self._get_expected_improvements(pattern_id)
        }

        return variation

    async def _modify_components(self, component_map: Dict[str, Any], pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Modify component structure based on A/B testing pattern"""

        modification_prompt = f"""
        Based on this component analysis and A/B testing pattern, modify the component structure:
        
        Original Components: {json.dumps(component_map['component_hierarchy'], indent=2)}
        
        A/B Testing Pattern: {pattern['name']}
        Strategy: {pattern['layout_strategy']}
        Key Changes: {pattern['key_changes']}
        
        Provide a modified component structure that implements these changes:
        1. Rearrange component priority and positioning
        2. Modify component sizes and emphasis
        3. Add/remove elements based on pattern
        4. Adjust content hierarchy
        5. Optimize for the pattern's goals
        
        Return as structured JSON with the new component arrangement.
        """

        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a UX expert specializing in A/B testing and conversion optimization. Modify component structures to match specific testing patterns."
                },
                {
                    "role": "user",
                    "content": modification_prompt
                }
            ],
            max_tokens=1500,
            temperature=0.2
        )

        # Parse the response (would need proper JSON parsing)
        return {
            "modification_strategy": pattern["layout_strategy"],
            "modified_structure": response.choices[0].message.content,
            "original_components": component_map["component_hierarchy"]
        }

    async def _generate_variation_react_code(self, modified_components: Dict[str, Any], pattern: Dict[str, Any]) -> str:
        """Generate React code for the A/B testing variation"""

        react_prompt = f"""
        Generate a complete React component for this A/B testing variation:
        
        Pattern: {pattern['name']}
        Strategy: {pattern['layout_strategy']}
        Modified Components: {json.dumps(modified_components, indent=2)}
        
        Requirements:
        1. Implement the A/B testing pattern exactly
        2. Use modern React with TypeScript
        3. Include Tailwind CSS for styling
        4. Make it responsive and accessible
        5. Add proper conversion tracking hooks
        6. Include A/B testing metadata
        7. Optimize for the pattern's goals
        
        Generate complete, production-ready code that implements this variation.
        """

        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert React developer specializing in A/B testing implementations. Generate conversion-optimized React components."
                },
                {
                    "role": "user",
                    "content": react_prompt
                }
            ],
            max_tokens=2500,
            temperature=0.1
        )

        return response.choices[0].message.content

    def _create_image_modification_prompt(self, component_map: Dict[str, Any], pattern: Dict[str, Any], modified_components: Dict[str, Any]) -> str:
        """Create modification prompt for GPT-Image-1 to transform the original screenshot"""

        # Get specific layout instructions based on pattern
        layout_instructions = self._get_pattern_layout_instructions(pattern)

        modification_prompt = f"""
        LAYOUT REARRANGEMENT TASK: Transform the hero section from centered to two-column layout while preserving ALL original design elements.
        
        TRANSFORMATION GOAL: {pattern['name']} - {pattern['layout_strategy']}
        
        MANDATORY LAYOUT CHANGES (POSITIONING ONLY):
        {chr(10).join([f"• {change}" for change in pattern['key_changes']])}
        
        SPECIFIC REARRANGEMENT INSTRUCTIONS:
        {layout_instructions}
        
        EXACT POSITIONING REQUIREMENTS:
        - Hero Section: {self._get_hero_positioning(pattern)}
        - Navigation: {self._get_navigation_positioning(pattern)}
        - Call-to-Action: {self._get_cta_positioning(pattern)}
        - Content Layout: {self._get_content_positioning(pattern)}
        
        LAYOUT TRANSFORMATION (PRESERVE ALL STYLING):
        - SPLIT the hero section into left text column (50%) and right demo image (50%)
        - MOVE the headline "Trace, Debug, & Deploy Reliable AI Agents" to LEFT side
        - MOVE the description text to LEFT side below headline
        - MOVE the CTA button to LEFT side below description
        - ADD a dashboard/interface mockup on RIGHT side showing AgentOps platform
        - KEEP all colors, fonts, styling, and branding identical to original
        
        CRITICAL DESIGN PRESERVATION:
        - Use EXACT same purple/blue color scheme from original
        - Use EXACT same fonts and typography from original
        - Use EXACT same button styling and colors from original
        - Keep EXACT same background colors and overall aesthetic
        - Preserve the AgentOps logo and navigation exactly as shown
        - Maintain the same professional, clean visual style
        
        RESULT: Should look like the same AgentOps website with hero content rearranged into two columns - identical styling, just different layout positioning.
        """

        return modification_prompt

    def _get_pattern_layout_instructions(self, pattern: Dict[str, Any]) -> str:
        """Get specific layout instructions for each A/B testing pattern"""
        pattern_instructions = {
            "1": """
            CRITICAL: CREATE A DRAMATIC TWO-COLUMN LAYOUT TRANSFORMATION:
            
            LEFT COLUMN (50% width):
            - Move ALL hero text content to the LEFT side of the screen
            - Stack the headline, subheadline, and description vertically on the left
            - Place call-to-action buttons below the text on the left side
            - Add company logos/social proof at the bottom of left column
            - Left-align all text content (not centered)
            
            RIGHT COLUMN (50% width):
            - Create a large demo/dashboard mockup image on the RIGHT side
            - Show a product interface, dashboard, or application screenshot
            - Make this visual element take up the entire right half
            - Add subtle shadows or modern styling to the demo image
            
            LAYOUT TRANSFORMATION:
            - Split the hero section into two equal columns (50/50)
            - Remove the centered layout completely
            - Create clear visual separation between left text and right image
            - Ensure the demo image is prominent and engaging
            - Make the layout feel like a modern SaaS landing page
            """,
            "2": """
            - Create a 3-column grid layout for main features
            - Add multiple call-to-action buttons (one per feature)
            - Make feature cards more prominent with icons or images
            - Distribute content more evenly across the page
            - Add hover effects and interactive elements
            - Include multiple entry points for different user types
            """,
            "3": """
            - Add more detailed descriptions and explanations
            - Include an FAQ section or detailed product information
            - Add testimonials, case studies, or social proof
            - Create expandable sections for additional information
            - Include comparison tables or feature lists
            - Add educational content or how-it-works sections
            """,
            "4": """
            - Add urgency indicators (limited time offers, countdown timers)
            - Include social proof badges (customer count, ratings)
            - Add trust signals (security badges, certifications)
            - Create scarcity elements (limited availability)
            - Include customer testimonials prominently
            - Add risk-reduction elements (money-back guarantee, free trial)
            """
        }
        return pattern_instructions.get(pattern.get('id', '1'), pattern_instructions['1'])

    def _get_hero_positioning(self, pattern: Dict[str, Any]) -> str:
        """Get hero section positioning for the pattern"""
        hero_positions = {
            "1": "Two-column split layout: Left side text content, Right side demo/dashboard image",
            "2": "Moderate size with grid elements below",
            "3": "Smaller hero with more content sections",
            "4": "Prominent with urgency elements and social proof"
        }
        return hero_positions.get(pattern.get('id', '1'), hero_positions['1'])

    def _get_navigation_positioning(self, pattern: Dict[str, Any]) -> str:
        """Get navigation positioning for the pattern"""
        nav_positions = {
            "1": "Minimal, clean navigation with essential items only",
            "2": "Standard navigation with multiple entry points",
            "3": "Detailed navigation with more menu items",
            "4": "Navigation with trust signals and contact info"
        }
        return nav_positions.get(pattern.get('id', '1'), nav_positions['1'])

    def _get_cta_positioning(self, pattern: Dict[str, Any]) -> str:
        """Get call-to-action positioning for the pattern"""
        cta_positions = {
            "1": "Primary CTA button positioned in left column below the headline text",
            "2": "Multiple CTAs distributed across feature sections",
            "3": "CTAs placed after detailed explanations",
            "4": "Prominent CTAs with urgency and social proof"
        }
        return cta_positions.get(pattern.get('id', '1'), cta_positions['1'])

    def _get_content_positioning(self, pattern: Dict[str, Any]) -> str:
        """Get content positioning for the pattern"""
        content_positions = {
            "1": "Hero content split into left text column and right demo image, company logos below",
            "2": "Grid-based content with equal visual weight",
            "3": "Rich, detailed content with multiple sections",
            "4": "Content focused on conversion with social proof"
        }
        return content_positions.get(pattern.get('id', '1'), content_positions['1'])

    async def _generate_variation_image_with_screenshot(self, component_map: Dict[str, Any], modification_prompt: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate variation image using original screenshot as input with GPT-Image-1 edit API"""

        try:
            print("    🎨 Generating variation image with GPT-Image-1...")

            # Get the original screenshot file path
            original_screenshot_path = self._get_original_screenshot_path(
                component_map)

            if not original_screenshot_path:
                print("    ⚠️  No original screenshot found, using text-only generation")
                return await self._generate_text_only_variation(modification_prompt, pattern)

            # Get original screenshot dimensions for optimal sizing
            original_width, original_height = self._get_screenshot_dimensions(
                original_screenshot_path)
            optimal_size = self._get_optimal_generation_size(
                original_width, original_height)

            # Enhance the prompt with design-centric instructions
            design_enhanced_prompt = self._add_design_preservation_instructions(
                modification_prompt, original_width, original_height)

            # Use GPT-Image-1 edit API with screenshot input and enhanced prompt
            with open(original_screenshot_path, 'rb') as img_file:
                response = await self.client.images.edit(
                    model="gpt-image-1",
                    image=img_file,
                    prompt=design_enhanced_prompt,
                    size=optimal_size
                )

            # Get base64 image data directly
            image_b64 = response.data[0].b64_json

            # Decode and save image locally
            import base64
            image_bytes = base64.b64decode(image_b64)

            # Create variations directory
            os.makedirs("outputs/variations", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_path = f"outputs/variations/variation_{timestamp}.png"

            with open(local_path, 'wb') as f:
                f.write(image_bytes)

            print(f"    ✅ Variation image saved: {local_path}")

            return {
                "local_path": local_path,
                "modification_prompt": design_enhanced_prompt,
                "original_screenshot_used": True,
                "original_screenshot_path": original_screenshot_path,
                "original_dimensions": f"{original_width}x{original_height}",
                "generated_size": optimal_size,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-image-1",
                "pattern": pattern['name']
            }

        except Exception as e:
            print(f"    ❌ Failed to generate variation image: {e}")
            return {
                "error": str(e),
                "modification_prompt": modification_prompt,
                "original_screenshot_path": original_screenshot_path if 'original_screenshot_path' in locals() else None,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-image-1",
                "pattern": pattern['name']
            }

    async def _quality_check_image(self, image_path: str) -> Dict[str, Any]:
        """Use GPT-4o to analyze generated image for quality issues"""

        print("    🔍 Running quality check on generated image...")

        # Read the generated image
        with open(image_path, 'rb') as img_file:
            import base64
            image_data = base64.b64encode(img_file.read()).decode('utf-8')

        quality_check_prompt = """
        Analyze this generated A/B testing variation image for quality issues. Look specifically for:
        
        1. Text overflow or clipping
        2. Bad margins or spacing issues
        3. Font problems (too small, too large, poor contrast)
        4. Low contrast between text and background
        5. Misaligned elements
        6. Overlapping content
        7. Broken layouts or missing sections
        8. Blurry or pixelated areas
        9. Inconsistent styling
        10. Any other visual glitches or problems
        
        Be specific and technical in your assessment. If you find issues, describe exactly what's wrong and how to fix it.
        
        Return your analysis as JSON with this structure:
        {
            "has_issues": true/false,
            "issues": [
                {
                    "type": "category of issue",
                    "description": "detailed description of the issue",
                    "severity": "high/medium/low",
                    "fix": "specific instructions to fix this issue"
                }
            ],
            "overall_quality": "poor/fair/good/excellent",
            "regeneration_needed": true/false
        }
        """

        messages = [
            {
                "role": "system",
                "content": "You are a UI/UX expert specializing in design quality assessment. Analyze images for visual problems and provide specific feedback."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": quality_check_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for vision analysis
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )

            # Parse the response
            if response.choices and len(response.choices) > 0 and response.choices[0].message.content:
                response_text = response.choices[0].message.content

                # Extract JSON from response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start != -1 and json_end > 0:
                    json_text = response_text[json_start:json_end]
                    quality_analysis = json.loads(json_text)

                # Log issues found
                if quality_analysis.get('has_issues', False):
                    print(
                        f"    ⚠️  Quality issues found: {len(quality_analysis.get('issues', []))} issues")
                    for issue in quality_analysis.get('issues', []):
                        print(
                            f"       - {issue['type']}: {issue['description'][:50]}...")
                else:
                    print("    ✅ No quality issues detected")

                return quality_analysis
            else:
                print("    ⚠️  Could not parse quality check response")
                return {"has_issues": False, "regeneration_needed": False}

        except Exception as e:
            print(f"    ❌ Quality check failed: {e}")
            return {"has_issues": False, "regeneration_needed": False, "error": str(e)}

    async def _regenerate_with_feedback(
        self,
        original_image_path: str,
        original_prompt: str,
        quality_feedback: Dict[str, Any],
        pattern: Dict[str, Any],
        component_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate image incorporating quality feedback"""

        print("    🔄 Regenerating image with quality improvements...")

        # Build feedback instructions
        feedback_instructions = "\n\nCRITICAL QUALITY IMPROVEMENTS NEEDED:\n"

        for issue in quality_feedback.get('issues', []):
            if issue['severity'] in ['high', 'medium']:
                feedback_instructions += f"\n• FIX {issue['type'].upper()}: {issue['fix']}"

        # Add general quality guidelines
        feedback_instructions += """
        
ADDITIONAL QUALITY REQUIREMENTS:
• Ensure all text is clearly readable with proper contrast
• Maintain consistent margins and spacing throughout
• Use appropriate font sizes (minimum 14px for body text)
• Ensure no elements overlap or clip
• Keep visual hierarchy clear and organized
• Maintain professional, polished appearance
"""

        # Combine original prompt with feedback
        enhanced_prompt = original_prompt + feedback_instructions

        # Get the original screenshot for reference
        original_screenshot_path = self._get_original_screenshot_path(
            component_map)

        if not original_screenshot_path:
            print("    ⚠️  No original screenshot found for regeneration")
            return {"error": "No original screenshot available"}

        try:
            # Regenerate with enhanced prompt
            with open(original_screenshot_path, 'rb') as img_file:
                response = await self.client.images.edit(
                    model="gpt-image-1",
                    image=img_file,
                    prompt=enhanced_prompt,
                    size="1024x1024"  # type: ignore
                )

                # Get base64 image data
            if response.data and len(response.data) > 0 and response.data[0].b64_json:
                image_b64 = response.data[0].b64_json

                # Decode and save improved image
                import base64
                image_bytes = base64.b64decode(image_b64)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                improved_path = f"outputs/variations/variation_{timestamp}_improved.png"

                with open(improved_path, 'wb') as f:
                    f.write(image_bytes)

                print(f"    ✅ Improved variation image saved: {improved_path}")

                return {
                    "local_path": improved_path,
                    "modification_prompt": enhanced_prompt,
                    "original_screenshot_used": True,
                    "original_screenshot_path": original_screenshot_path,
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-image-1",
                    "pattern": pattern['name'],
                    "quality_improved": True,
                    "improvements_applied": [issue['type'] for issue in quality_feedback.get('issues', [])]
                }
            else:
                print("    ❌ No image data in response")
                return {"error": "No image data in response"}

        except Exception as e:
            print(f"    ❌ Failed to regenerate improved image: {e}")
            return {"error": str(e)}

    def _get_original_screenshot_path(self, component_map: Dict[str, Any]) -> Optional[str]:
        """Get original screenshot file path from component map"""
        try:
            # Look for screenshot paths in the component map
            if 'segments' in component_map:
                for segment in component_map['segments']:
                    if 'screenshot_path' in segment and os.path.exists(segment['screenshot_path']):
                        return segment['screenshot_path']

            # Fallback: look for screenshot files in common locations
            screenshot_files = [
                "outputs/screenshots/www.agentops.ai_.png",
                "outputs/screenshots/segment_1_top.png",
                "segment_1_top.png",
                "outputs/screenshots/segment_2_quarter.png",
                "segment_2_quarter.png"
            ]

            for screenshot_file in screenshot_files:
                if os.path.exists(screenshot_file):
                    return screenshot_file

            return None

        except Exception as e:
            print(f"    ⚠️  Could not find original screenshot: {e}")
            return None

    def _get_screenshot_dimensions(self, screenshot_path: str) -> tuple[int, int]:
        """Get dimensions of the original screenshot"""
        try:
            from PIL import Image
            with Image.open(screenshot_path) as img:
                return img.size  # Returns (width, height)
        except Exception as e:
            print(f"    ⚠️  Could not get screenshot dimensions: {e}")
            return (1365, 768)  # Default web dimensions

    def _get_optimal_generation_size(self, original_width: int, original_height: int) -> str:
        """Get the best GPT-Image-1 size that matches the original aspect ratio"""
        aspect_ratio = original_width / original_height

        # Available GPT-Image-1 sizes
        available_sizes = {
            # Landscape 3:2 - BEST for desktop
            "1536x1024": (1536, 1024, 1.5),
            "1024x1024": (1024, 1024, 1.0),           # Square
            # Portrait 2:3 - mobile-like
            "1024x1536": (1024, 1536, 0.667),
        }

        # For desktop screenshots (width > height), prioritize landscape
        if original_width > original_height:
            print(f"    💻 Desktop layout detected (width > height)")
            print(
                f"    📐 Original: {original_width}x{original_height} (ratio: {aspect_ratio:.2f})")
            print(
                f"    ⚠️  GPT-Image-1 limitation: Cannot generate {original_width}x{original_height}")
            print(f"    📐 Using best available: 1536x1024 landscape for desktop view")
            print(
                f"    🎯 Focusing on hero section transformation within available dimensions")
            return "1536x1024"

        # For other cases, find the closest aspect ratio
        best_size = "1024x1024"
        best_diff = float('inf')

        for size_name, (width, height, ratio) in available_sizes.items():
            diff = abs(aspect_ratio - ratio)
            if diff < best_diff:
                best_diff = diff
                best_size = size_name

        print(
            f"    📐 Original: {original_width}x{original_height} (ratio: {aspect_ratio:.2f})")
        print(f"    📐 Using GPT-Image-1 size: {best_size}")

        return best_size

    def _add_design_preservation_instructions(self, modification_prompt: str, original_width: int, original_height: int) -> str:
        """Add design-centric instructions to preserve the natural flow and organic feel"""

        design_instructions = f"""
        CRITICAL DESIGN PRESERVATION - ZERO TOLERANCE FOR CHANGES:
        
        ABSOLUTE COLOR PRESERVATION:
        - Keep EXACT same background colors (light gray/white backgrounds)
        - Keep EXACT same text colors (black text, purple accents)
        - Keep EXACT same button colors (purple/blue gradients)
        - Keep EXACT same brand colors throughout
        - DO NOT change any color schemes, gradients, or hues
        - DO NOT alter the visual color palette in any way
        
        ABSOLUTE TYPOGRAPHY PRESERVATION:
        - Keep EXACT same fonts and font families
        - Keep EXACT same font weights (bold headings, regular body text)
        - Keep EXACT same font sizes and text hierarchy
        - Keep EXACT same text styling and formatting
        - DO NOT change typography or text appearance
        
        ABSOLUTE VISUAL STYLE PRESERVATION:
        - Keep EXACT same shadows, borders, and visual effects
        - Keep EXACT same spacing patterns and padding
        - Keep EXACT same visual treatments and styling
        - Keep EXACT same design system elements
        - DO NOT alter the overall aesthetic or visual style
        
        DIMENSION OPTIMIZATION FOR GPT-IMAGE-1:
        - Original screenshot: {original_width}x{original_height} pixels (desktop full-page)
        - GPT-Image-1 limitation: Cannot generate original dimensions
        - CRITICAL: Use landscape 1536x1024 format to maximize desktop layout space
        - Focus on the HERO SECTION and top portion of the page for transformation
        - Ensure the two-column layout fits naturally within the generated dimensions
        
        LAYOUT REARRANGEMENT ONLY:
        - This is ONLY a component rearrangement, NOT a redesign
        - Move existing elements to new positions without changing their appearance
        - Split hero section into left text column and right demo image
        - Preserve all original design elements exactly as they appear
        - Focus transformation on the main hero/content area
        
        STRICT CONSTRAINTS:
        - DO NOT change colors, fonts, or visual styling
        - DO NOT redesign or recreate any elements  
        - DO NOT alter the brand appearance or aesthetic
        - DO NOT crop or cut off important content
        - DO NOT change the overall professional appearance
        
        {modification_prompt}
        
        FINAL RESULT REQUIREMENTS:
        - Should look like the same website with rearranged layout
        - All colors, fonts, and styling should be identical to original
        - Only the positioning and arrangement should be different
        - Must maintain the AgentOps brand identity perfectly
        - Should feel like a natural layout variation, not a different design
        """

        return design_instructions

    async def _generate_text_only_variation(self, modification_prompt: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback: Generate variation using text-only prompt"""

        text_prompt = f"""
        Create a modern website landing page design for A/B testing:
        
        PATTERN: {pattern['name']} - {pattern['description']}
        
        LAYOUT REQUIREMENTS:
        {chr(10).join([f"• {change}" for change in pattern['key_changes']])}
        
        DESIGN SPECIFICATIONS:
        - Professional business website aesthetic
        - Modern, clean design with good conversion potential
        - Clear visual hierarchy and user flow
        - Responsive design principles
        - High-converting landing page layout
        
        STYLE: Clean, modern, professional website design, flat design, minimal shadows, contemporary UI/UX, optimized for conversions
        """

        try:
            response = await self.client.images.generate(
                model="gpt-image-1",
                prompt=text_prompt,
                size="1024x1024",
                n=1
            )

            image_b64 = response.data[0].b64_json
            import base64
            image_bytes = base64.b64decode(image_b64)

            os.makedirs("outputs/variations", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_path = f"outputs/variations/variation_text_{timestamp}.png"

            with open(local_path, 'wb') as f:
                f.write(image_bytes)

            return {
                "local_path": local_path,
                "text_prompt": text_prompt,
                "method": "text_only_fallback",
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-image-1"
            }

        except Exception as e:
            return {
                "error": str(e),
                "method": "text_only_fallback",
                "generated_at": datetime.now().isoformat()
            }

    def _extract_colors(self, component_map: Dict[str, Any]) -> str:
        """Extract color information from component analysis"""
        # This would extract from the actual analysis
        return "Modern purple and blue gradient (#6366F1, #8B5CF6), white backgrounds, dark text"

    def _extract_typography(self, component_map: Dict[str, Any]) -> str:
        """Extract typography information from component analysis"""
        # This would extract from the actual analysis
        return "Clean sans-serif fonts, bold headings, readable body text"

    def _get_expected_improvements(self, pattern_id: str) -> List[str]:
        """Get expected improvements for each A/B testing pattern"""
        improvements = {
            "1": [
                "Higher conversion rates from clear CTA",
                "Reduced bounce rate from focused messaging",
                "Better mobile experience"
            ],
            "2": [
                "Increased feature discovery",
                "Higher engagement with multiple CTAs",
                "Better for complex products"
            ],
            "3": [
                "Improved user education",
                "Higher qualified leads",
                "Better for B2B conversions"
            ],
            "4": [
                "Urgency-driven conversions",
                "Social proof validation",
                "Reduced decision friction"
            ]
        }
        return improvements.get(pattern_id, [])

    def _generate_comparison_metrics(self, variations: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison metrics for A/B testing"""
        return {
            "suggested_metrics": [
                "Conversion rate",
                "Click-through rate",
                "Bounce rate",
                "Time on page",
                "Scroll depth"
            ],
            "testing_duration": "2-4 weeks",
            "minimum_sample_size": "1000 visitors per variation",
            "statistical_significance": "95% confidence level"
        }

    async def save_ab_test_package(self, ab_test_package: Dict[str, Any], output_dir: str = "ab_tests") -> str:
        """Save complete A/B testing package"""

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save main package
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_file = os.path.join(
            output_dir, f"ab_test_package_{timestamp}.json")

        with open(package_file, 'w') as f:
            json.dump(ab_test_package, f, indent=2)

        # Save individual React components for each variation
        for var_id, variation in ab_test_package["variations"].items():
            var_dir = os.path.join(output_dir, var_id)
            os.makedirs(var_dir, exist_ok=True)

            # Save React code
            react_file = os.path.join(var_dir, f"{var_id}.tsx")
            with open(react_file, 'w') as f:
                f.write(variation["react_code"])

            # Save variation details
            details_file = os.path.join(var_dir, "variation_details.json")
            with open(details_file, 'w') as f:
                json.dump(variation, f, indent=2)

        print(f"💾 A/B test package saved: {package_file}")
        return package_file
