"""
A/B Testing Generator
Creates 4 different UI variations for A/B testing using component maps and DALL-E image generation
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
        
        # Step 3: Create DALL-E prompt for image generation
        dalle_prompt = self._create_dalle_prompt(component_map, pattern, modified_components)
        
        # Step 4: Generate variation image
        variation_image = await self._generate_variation_image(dalle_prompt)
        
        # Step 5: Create variation package
        variation = {
            "id": pattern_id,
            "name": pattern["name"],
            "description": pattern["description"],
            "layout_strategy": pattern["layout_strategy"],
            "key_changes": pattern["key_changes"],
            "modified_components": modified_components,
            "react_code": variation_react_code,
            "dalle_prompt": dalle_prompt,
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
    
    def _create_dalle_prompt(self, component_map: Dict[str, Any], pattern: Dict[str, Any], modified_components: Dict[str, Any]) -> str:
        """Create DALL-E prompt for generating variation images"""
        
        # Extract key visual elements from original analysis
        original_colors = self._extract_colors(component_map)
        original_typography = self._extract_typography(component_map)
        
        dalle_prompt = f"""
        Create a modern, professional website landing page design with these specifications:
        
        LAYOUT PATTERN: {pattern['name']} - {pattern['description']}
        
        VISUAL STYLE:
        - Color scheme: {original_colors}
        - Typography: {original_typography}
        - Modern, clean design aesthetic
        - Professional business website
        
        LAYOUT REQUIREMENTS:
        {chr(10).join([f"- {change}" for change in pattern['key_changes']])}
        
        SPECIFIC ELEMENTS:
        - Header with navigation
        - Hero section with clear value proposition
        - Call-to-action buttons
        - Feature highlights or benefits
        - Social proof elements
        - Footer section
        
        STYLE: Clean, modern, professional, high-converting landing page design, flat design, minimal shadows, contemporary UI/UX
        """
        
        return dalle_prompt
    
    async def _generate_variation_image(self, dalle_prompt: str) -> Dict[str, Any]:
        """Generate variation image using DALL-E"""
        
        try:
            print("    🎨 Generating variation image with DALL-E...")
            
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1792x1024",  # Landscape format for web layouts
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Save image locally
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        
                        # Create variations directory
                        os.makedirs("variations", exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        local_path = f"variations/variation_{timestamp}.png"
                        
                        with open(local_path, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"    ✅ Variation image saved: {local_path}")
                        
                        return {
                            "url": image_url,
                            "local_path": local_path,
                            "prompt": dalle_prompt,
                            "generated_at": datetime.now().isoformat()
                        }
            
        except Exception as e:
            print(f"    ❌ Failed to generate variation image: {e}")
            return {
                "error": str(e),
                "prompt": dalle_prompt,
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