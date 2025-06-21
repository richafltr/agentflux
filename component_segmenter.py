"""
Component Segmentation Service
Divides screenshots into scrollable sections and analyzes each component individually
"""

import os
import json
from typing import Dict, List, Tuple, Any
from PIL import Image
import asyncio
from datetime import datetime

from config import Config
from screenshot_service import ScreenshotService
from vision_analyzer import VisionAnalyzer


class ComponentSegmenter:
    """Segments screenshots into components and analyzes each section"""
    
    def __init__(self):
        self.config = Config()
        self.screenshot_service = ScreenshotService()
        self.vision_analyzer = VisionAnalyzer()
        
    async def segment_and_analyze(self, url: str) -> Dict[str, Any]:
        """
        Main workflow: Screenshot → Segment → Analyze → Generate React Code
        
        Returns:
            Complete analysis with segmented components and React code
        """
        print(f"🔄 Starting component segmentation for: {url}")
        
        # Step 1: Capture full page screenshot with scroll segments
        scroll_segments = await self._capture_scroll_segments(url)
        
        # Step 2: Analyze each segment individually
        component_analyses = await self._analyze_segments(scroll_segments)
        
        # Step 3: Generate React code for each component
        react_components = await self._generate_react_code(component_analyses)
        
        # Step 4: Create component map structure
        component_map = self._create_component_map(
            url, scroll_segments, component_analyses, react_components
        )
        
        print(f"✅ Segmentation complete! Generated {len(scroll_segments)} components")
        return component_map
    
    async def _capture_scroll_segments(self, url: str) -> List[Dict[str, Any]]:
        """Capture 4 scroll segments of the webpage"""
        print("📸 Capturing scroll segments...")
        
        segments = []
        scroll_positions = [0, 0.25, 0.5, 0.75]  # Top, Quarter, Half, Three-quarters
        
        for i, scroll_pos in enumerate(scroll_positions):
            segment_name = f"segment_{i+1}_{['top', 'quarter', 'half', 'bottom'][i]}"
            
            # Capture screenshot at specific scroll position
            screenshot_path = await self.screenshot_service.capture_with_scroll(
                url, scroll_position=scroll_pos, filename=f"{segment_name}.png"
            )
            
            # Convert to base64 for analysis
            with open(screenshot_path, "rb") as img_file:
                import base64
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            segments.append({
                "segment_id": segment_name,
                "scroll_position": scroll_pos,
                "screenshot_path": screenshot_path,
                "base64_image": base64_image,
                "components": []  # Will be populated during analysis
            })
            
            print(f"  📷 Captured {segment_name} at {scroll_pos*100}% scroll")
        
        return segments
    
    async def _analyze_segments(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze each segment to extract component information"""
        print("🔍 Analyzing individual segments...")
        
        analyses = {}
        
        # Analyze segments in parallel for efficiency
        tasks = []
        for segment in segments:
            task = self._analyze_single_segment(segment)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                segment_id = segments[i]["segment_id"]
                analyses[segment_id] = result
                print(f"  ✅ Analyzed {segment_id}")
            else:
                print(f"  ❌ Failed to analyze segment {i}: {result}")
        
        return analyses
    
    async def _analyze_single_segment(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single scroll segment for components"""
        
        # Use focused prompts for component identification
        component_prompt = f"""
        Analyze this webpage segment and identify distinct UI components.
        Focus on:
        1. Navigation elements (header, menu, breadcrumbs)
        2. Hero sections (banners, call-to-actions)
        3. Content blocks (cards, articles, features)
        4. Interactive elements (buttons, forms, inputs)
        5. Footer elements (links, contact info)
        
        For each component, provide:
        - Component type and purpose
        - Exact positioning and dimensions
        - Visual styling details
        - Content hierarchy
        - Interactive states
        
        Return as structured JSON with component boundaries and specifications.
        """
        
        # Analyze using vision analyzer with component-focused prompt
        analysis = await self.vision_analyzer.analyze_screenshot(
            segment["base64_image"], 
            use_multi_stage=False,
            custom_prompt=component_prompt
        )
        
        return {
            "segment_info": {
                "id": segment["segment_id"],
                "scroll_position": segment["scroll_position"]
            },
            "components": analysis,
            "screenshot_path": segment["screenshot_path"]
        }
    
    async def _generate_react_code(self, component_analyses: Dict[str, Any]) -> Dict[str, str]:
        """Generate React code for each analyzed component"""
        print("⚛️  Generating React components...")
        
        react_components = {}
        
        for segment_id, analysis in component_analyses.items():
            print(f"  🔧 Generating React code for {segment_id}...")
            
            react_prompt = f"""
            Based on this component analysis, generate clean, modern React code:
            
            Analysis: {json.dumps(analysis, indent=2)}
            
            Requirements:
            1. Use functional components with hooks
            2. Include Tailwind CSS classes for styling
            3. Make components responsive and accessible
            4. Include proper TypeScript interfaces
            5. Add hover states and interactions
            6. Use semantic HTML elements
            7. Include proper ARIA labels
            
            Generate complete, production-ready React component code that matches the analyzed design exactly.
            Include all necessary imports and exports.
            """
            
            # Generate React code using GPT-4
            react_code = await self._generate_code_with_gpt4(react_prompt)
            react_components[segment_id] = react_code
            
            print(f"  ✅ Generated React code for {segment_id}")
        
        return react_components
    
    async def _generate_code_with_gpt4(self, prompt: str) -> str:
        """Generate code using GPT-4"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert React developer. Generate clean, modern, production-ready React components with TypeScript and Tailwind CSS."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _create_component_map(
        self, 
        url: str, 
        segments: List[Dict[str, Any]], 
        analyses: Dict[str, Any], 
        react_code: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create the final component map structure"""
        
        timestamp = datetime.now().isoformat()
        
        component_map = {
            "metadata": {
                "url": url,
                "analysis_timestamp": timestamp,
                "total_segments": len(segments),
                "analysis_type": "component_segmentation"
            },
            "segments": {},
            "react_components": react_code,
            "component_hierarchy": self._build_component_hierarchy(analyses)
        }
        
        # Build segment data
        for segment in segments:
            segment_id = segment["segment_id"]
            component_map["segments"][segment_id] = {
                "scroll_position": segment["scroll_position"],
                "screenshot_path": segment["screenshot_path"],
                "analysis": analyses.get(segment_id, {}),
                "react_code_key": segment_id
            }
        
        return component_map
    
    def _build_component_hierarchy(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Build a hierarchical view of all components"""
        hierarchy = {
            "navigation": [],
            "hero": [],
            "content": [],
            "interactive": [],
            "footer": []
        }
        
        # Categorize components from all segments
        for segment_id, analysis in analyses.items():
            # This would be enhanced based on actual component analysis structure
            # For now, create a basic categorization
            hierarchy["content"].append({
                "segment_id": segment_id,
                "components": analysis.get("components", {})
            })
        
        return hierarchy
    
    async def save_component_map(self, component_map: Dict[str, Any], output_dir: str = "components") -> str:
        """Save component map and associated files"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main component map
        map_file = os.path.join(output_dir, "component_map.json")
        with open(map_file, 'w') as f:
            json.dump(component_map, f, indent=2)
        
        # Save individual React components
        react_dir = os.path.join(output_dir, "react_components")
        os.makedirs(react_dir, exist_ok=True)
        
        for component_id, react_code in component_map["react_components"].items():
            component_file = os.path.join(react_dir, f"{component_id}.tsx")
            with open(component_file, 'w') as f:
                f.write(react_code)
        
        print(f"💾 Component map saved to: {map_file}")
        print(f"⚛️  React components saved to: {react_dir}")
        
        return map_file 