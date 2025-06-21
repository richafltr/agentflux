"""
A/B Testing Generator
Creates 4 different UI variations for A/B testing using component maps and GPT-Image-1 native image generation
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
                print(f"  ✅ Generated variation {pattern_id}: {variation['name']}")
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
        image_prompt = self._create_image_modification_prompt(component_map, pattern, modified_components)
        
        # Step 4: Generate variation image using original screenshot + modifications
        variation_image = await self._generate_variation_image_with_screenshot(component_map, image_prompt, pattern)
        
        # Step 5: Create variation package
        variation = {
            "id": pattern_id,
            "name": pattern["name"],
            "description": pattern["description"],
            "layout_strategy": pattern["layout_strategy"],
            "key_changes": pattern["key_changes"],
            "modified_components": modified_components,
            "react_code": variation_react_code,
            "image_prompt": image_prompt,
            "generated_image": variation_image,
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
        CRITICAL: Completely transform this website layout from centered design to a dramatic two-column layout.
        
        TRANSFORMATION GOAL: {pattern['name']} - {pattern['layout_strategy']}
        
        MANDATORY LAYOUT CHANGES:
        {chr(10).join([f"• {change}" for change in pattern['key_changes']])}
        
        SPECIFIC REARRANGEMENT INSTRUCTIONS:
        {layout_instructions}
        
        EXACT POSITIONING REQUIREMENTS:
        - Hero Section: {self._get_hero_positioning(pattern)}
        - Navigation: {self._get_navigation_positioning(pattern)}
        - Call-to-Action: {self._get_cta_positioning(pattern)}
        - Content Layout: {self._get_content_positioning(pattern)}
        
        CRITICAL VISUAL TRANSFORMATION:
        - COMPLETELY REMOVE the centered layout approach
        - CREATE a clear 50/50 split between text and visual content
        - MOVE all headline text to the LEFT side of the screen
        - ADD a large product demo/dashboard mockup on the RIGHT side
        - ENSURE the demo image shows an interface, dashboard, or application
        - MAKE the layout look like a modern SaaS landing page (similar to Stripe, Notion, or Figma)
        
        DESIGN REQUIREMENTS:
        - Maintain the original AgentOps branding and colors
        - Keep the same text content but rearrange positioning
        - Add visual depth with shadows and modern styling
        - Ensure the demo image is engaging and professional
        - Create clear visual hierarchy with left-aligned text
        
        RESULT: The final image should look dramatically different from the original - like a completely new layout with text on left and demo on right, not just minor adjustments to the centered design.
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
            original_screenshot_path = self._get_original_screenshot_path(component_map)
            
            if not original_screenshot_path:
                print("    ⚠️  No original screenshot found, using text-only generation")
                return await self._generate_text_only_variation(modification_prompt, pattern)
            
            # Use GPT-Image-1 edit API with screenshot input and modification prompt
            with open(original_screenshot_path, 'rb') as img_file:
                response = await self.client.images.edit(
                    model="gpt-image-1",
                    image=img_file,
                    prompt=modification_prompt,
                    size="1024x1024"
                )
            
            # Get base64 image data directly
            image_b64 = response.data[0].b64_json
            
            # Decode and save image locally
            import base64
            image_bytes = base64.b64decode(image_b64)
            
            # Create variations directory
            os.makedirs("variations", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_path = f"variations/variation_{timestamp}.png"
            
            with open(local_path, 'wb') as f:
                f.write(image_bytes)
            
            print(f"    ✅ Variation image saved: {local_path}")
            
            return {
                "local_path": local_path,
                "modification_prompt": modification_prompt,
                "original_screenshot_used": True,
                "original_screenshot_path": original_screenshot_path,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-image-1",
                "pattern": pattern['name']
            }
            
        except Exception as e:
            print(f"    ❌ Failed to generate variation image: {e}")
            return {
                "error": str(e),
                "modification_prompt": modification_prompt,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-image-1",
                "pattern": pattern['name']
            }
    
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
                "screenshots/www.agentops.ai_.png",
                "screenshots/segment_1_top.png",
                "segment_1_top.png",
                "screenshots/segment_2_quarter.png",
                "segment_2_quarter.png"
            ]
            
            for screenshot_file in screenshot_files:
                if os.path.exists(screenshot_file):
                    return screenshot_file
            
            return None
            
        except Exception as e:
            print(f"    ⚠️  Could not find original screenshot: {e}")
            return None
    
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
            
            os.makedirs("variations", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_path = f"variations/variation_text_{timestamp}.png"
            
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
        package_file = os.path.join(output_dir, f"ab_test_package_{timestamp}.json")
        
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