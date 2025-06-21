import json
import asyncio
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
from config import Config
from prompts import DesignPrompts
from screenshot_service import ScreenshotService

class VisionAnalyzer:
    """GPT-4 Vision API analyzer for design system extraction"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        self.client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        self.prompts = DesignPrompts()
    
    async def analyze_screenshot(
        self, 
        base64_image: str, 
        use_multi_stage: bool = True,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a screenshot and extract comprehensive design metadata
        
        Args:
            base64_image: Base64 encoded screenshot
            use_multi_stage: Whether to use multi-stage analysis for better accuracy
            custom_prompt: Optional custom prompt for specialized analysis
            
        Returns:
            Comprehensive design system analysis
        """
        try:
            if custom_prompt:
                return await self._custom_prompt_analysis(base64_image, custom_prompt)
            elif use_multi_stage:
                return await self._multi_stage_analysis(base64_image)
            else:
                return await self._single_stage_analysis(base64_image)
        
        except Exception as e:
            # Check if we have a partially successful analysis from JSON chunks
            if hasattr(self, '_last_successful_merge'):
                print(f"DEBUG: Using last successful merge due to error: {str(e)}")
                return self._last_successful_merge
            raise Exception(f"Vision analysis failed: {str(e)}")
    
    async def _single_stage_analysis(self, base64_image: str) -> Dict[str, Any]:
        """Perform single-stage comprehensive analysis"""
        
        schema_json = self.prompts.get_schema_json()
        
        messages = [
            {
                "role": "system",
                "content": self.prompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.prompts.get_analysis_prompt(schema_json)
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            max_tokens=4000,
            temperature=0.0
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    async def _multi_stage_analysis(self, base64_image: str) -> Dict[str, Any]:
        """Perform multi-stage analysis for enhanced accuracy"""
        
        # Stage 1: Focused category analyses
        focused_analyses = await self._run_focused_analyses(base64_image)
        
        # Stage 2: Comprehensive synthesis
        comprehensive_analysis = await self._synthesize_analysis(
            base64_image, 
            focused_analyses
        )
        
        # Stage 3: Validation and refinement
        final_analysis = await self._validate_analysis(
            base64_image,
            comprehensive_analysis
        )
        
        return final_analysis
    
    async def _run_focused_analyses(self, base64_image: str) -> Dict[str, Dict]:
        """Run focused analyses for specific design categories"""
        
        categories = ["typography", "colors", "layout", "components"]
        
        # Run focused analyses in parallel
        tasks = []
        for category in categories:
            task = self._analyze_category(base64_image, category)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        focused_analyses = {}
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                focused_analyses[categories[i]] = result
            else:
                print(f"Warning: Failed to analyze {categories[i]}: {result}")
        
        return focused_analyses
    
    async def _analyze_category(self, base64_image: str, category: str) -> Dict:
        """Analyze a specific design category"""
        
        focused_prompt = self.prompts.get_focused_prompt(category)
        
        messages = [
            {
                "role": "system",
                "content": self.prompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": focused_prompt + "\n\nProvide detailed analysis in JSON format."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            max_tokens=1500,
            temperature=0.1
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    async def _synthesize_analysis(
        self, 
        base64_image: str, 
        focused_analyses: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """Synthesize focused analyses into comprehensive design system"""
        
        schema_json = self.prompts.get_schema_json()
        
        synthesis_prompt = f"""
        Based on the following focused analyses, create a comprehensive design system analysis:
        
        {json.dumps(focused_analyses, indent=2)}
        
        Synthesize this information into the complete schema structure:
        {schema_json}
        
        Fill in any missing categories not covered in the focused analyses by examining the screenshot directly.
        Ensure consistency across all design elements and provide precise technical specifications.
        """
        
        messages = [
            {
                "role": "system",
                "content": self.prompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": synthesis_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            max_tokens=4000,
            temperature=0.1
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    async def _validate_analysis(
        self, 
        base64_image: str, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and refine the design analysis"""
        
        validation_prompt = f"""
        {self.prompts.get_validation_prompt()}
        
        Current analysis:
        {json.dumps(analysis, indent=2)}
        
        Review this analysis against the screenshot and provide the final, validated design system.
        """
        
        messages = [
            {
                "role": "system",
                "content": self.prompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": validation_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            max_tokens=4000,
            temperature=0.1
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    async def _custom_prompt_analysis(self, base64_image: str, custom_prompt: str) -> Dict[str, Any]:
        """Perform analysis with a custom prompt"""
        
        messages = [
            {
                "role": "system",
                "content": self.prompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": custom_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            max_tokens=4000,
            temperature=0.0
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and clean the API response, handling multiple JSON chunks"""
        print(f"DEBUG: Raw response preview: {response_text[:500]}...")
        
        try:
            # First try to extract multiple JSON chunks and merge them
            json_chunks = []
            text = response_text
            
            # Find all JSON code blocks
            while '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                if end != -1:
                    json_text = text[start:end].strip()
                    try:
                        chunk = json.loads(json_text)
                        json_chunks.append(chunk)
                        print(f"DEBUG: Found JSON chunk: {list(chunk.keys())[:3]}...")
                    except json.JSONDecodeError:
                        pass
                    text = text[end + 3:]
                else:
                    break
            
            # If we found multiple chunks, try to merge them into our schema
            if json_chunks:
                merged_result = self._merge_analysis_chunks(json_chunks)
                print(f"DEBUG: Successfully merged {len(json_chunks)} JSON chunks")
                # Store successful merge for potential error recovery
                self._last_successful_merge = merged_result
                return merged_result
            
            # Fallback to original logic
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                print(f"DEBUG: No JSON brackets found in response")
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            print(f"DEBUG: Extracted JSON preview: {json_text[:200]}...")
            
            # Parse JSON
            parsed_data = json.loads(json_text)
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            raise ValueError(f"Failed to parse response: {str(e)}")
        except Exception as e:
            print(f"DEBUG: Parsing error: {e}")
            raise ValueError(f"Failed to parse response: {str(e)}")
    
    def _merge_analysis_chunks(self, chunks: List[Dict]) -> Dict[str, Any]:
        """Merge multiple JSON chunks into our design schema"""
        from design_schema import DesignSchema
        
        # Initialize with schema structure
        merged_analysis = {}
        schema = DesignSchema()
        
        # Check if we have existing data from previous merges
        if hasattr(self, '_accumulated_chunks'):
            chunks = self._accumulated_chunks + chunks
        else:
            self._accumulated_chunks = []
        
        # Store all chunks for future merging
        self._accumulated_chunks.extend(chunks)
        
        # Map chunk data to schema categories
        for chunk in chunks:
            # Typography mapping
            if 'typography' in chunk:
                merged_analysis['Typography'] = self._map_typography(chunk['typography'])
            
            # Color mapping
            if 'colorPalette' in chunk or 'primary' in chunk:
                merged_analysis['Color & Contrast'] = self._map_colors(chunk)
            
            # Layout mapping
            if 'gridSystem' in chunk or 'spacingPatterns' in chunk:
                merged_analysis['Layout & Grid System'] = self._map_layout(chunk)
            
            # Button/component mapping
            if 'buttonStyles' in chunk:
                merged_analysis['Buttons & Calls-to-Action'] = self._map_buttons(chunk['buttonStyles'])
            
            # Form elements mapping
            if 'formElements' in chunk:
                merged_analysis['Form & Input Styling'] = chunk['formElements']
            
            # Card designs mapping
            if 'cardDesigns' in chunk:
                merged_analysis['Cards / Panels / Containers'] = chunk['cardDesigns']
        
        # Fill in any missing categories with basic analysis
        schema_keys = list(schema.schema_template.keys())
        for key in schema_keys:
            if key not in merged_analysis:
                merged_analysis[key] = f"Analysis not available for {key} category"
        
        print(f"DEBUG: Merged analysis with {len(merged_analysis)} categories from {len(chunks)} total chunks")
        return merged_analysis
    
    def _map_typography(self, typography_data: Dict) -> Dict:
        """Map typography data to schema format"""
        return {
            "Primary, secondary & fallback font families (web-safe or web-hosted)": 
                typography_data.get('fontFamilies', ['Not specified']),
            "Weight spectrum to use (e.g., 300, 400, 600, 700)": 
                list(typography_data.get('fontWeights', {}).values()),
            "Heading sizes (H1-H6) with exact px/rem values": 
                typography_data.get('fontSizes', {}),
            "Line-height & paragraph spacing rules": 
                typography_data.get('lineHeights', {}),
            "Letter-spacing / tracking values by text role": 
                typography_data.get('letterSpacing', {})
        }
    
    def _map_colors(self, color_data: Dict) -> Dict:
        """Map color data to schema format"""
        colors = color_data.get('colorPalette', color_data)
        return {
            "Brand primaries, secondaries, accents (hex/RGB/HSL)": 
                colors.get('primary', {}),
            "Neutral/gray scale set": 
                colors.get('neutral', {}),
            "Success, warning, error, info colors": 
                colors.get('semantic', {}),
            "Gradient definitions (angle, stops)": 
                color_data.get('gradients', [])
        }
    
    def _map_layout(self, layout_data: Dict) -> Dict:
        """Map layout data to schema format"""
        return {
            "Maximum content width / full-bleed rules": 
                layout_data.get('containerWidths', {}).get('extraLarge', 'Not specified'),
            "Column count, gutter width, and margin specs": 
                f"{layout_data.get('gridSystem', {}).get('columns', 12)} columns, {layout_data.get('gridSystem', {}).get('gutters', 'default')} gutters",
            "Responsive breakpoints & how the grid adapts": 
                layout_data.get('gridSystem', {}).get('breakpoints', {}),
            "Vertical rhythm unit (e.g., 4 px or 8 px scale)": 
                layout_data.get('spacingPatterns', {}).get('baseUnit', '8px')
        }
    
    def _map_buttons(self, button_data: Dict) -> Dict:
        """Map button data to schema format"""
        primary = button_data.get('primaryButton', {})
        return {
            "Primary, secondary, tertiary button styles": 
                button_data,
            "Padding, min-width & height, corner radius": 
                f"Padding: {primary.get('padding', 'default')}, Radius: {primary.get('borderRadius', 'default')}",
            "Text style (size, weight, letter-spacing)": 
                f"Size: {primary.get('fontSize', 'default')}, Weight: {primary.get('fontWeight', 'default')}",
            "State styles: default, hover, active, focus, disabled": 
                primary.get('hoverState', {})
        }
    
    async def analyze_website(
        self,
        url: str,
        save_screenshot: bool = True,
        include_mobile: bool = False
    ) -> Dict[str, Any]:
        """
        Complete website analysis workflow
        
        Args:
            url: Website URL to analyze
            save_screenshot: Whether to save screenshot to file
            include_mobile: Whether to include mobile analysis
            
        Returns:
            Complete design system analysis
        """
        async with ScreenshotService() as screenshot_service:
            # Capture screenshot
            print(f"Capturing screenshot of {url}...")
            
            if include_mobile:
                desktop_screenshot, mobile_screenshot = await screenshot_service.capture_with_mobile_view(url)
                
                # Optimize images
                desktop_screenshot = ScreenshotService.optimize_image(desktop_screenshot)
                mobile_screenshot = ScreenshotService.optimize_image(mobile_screenshot)
                
                # Analyze both views
                print("Analyzing desktop view...")
                desktop_analysis = await self.analyze_screenshot(desktop_screenshot)
                
                print("Analyzing mobile view...")
                mobile_analysis = await self.analyze_screenshot(mobile_screenshot)
                
                # Combine analyses
                return {
                    "desktop_analysis": desktop_analysis,
                    "mobile_analysis": mobile_analysis,
                    "url": url,
                    "analysis_type": "multi_device"
                }
            else:
                # Single desktop analysis
                screenshot_path = f"screenshots/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.png" if save_screenshot else None
                
                screenshot = await screenshot_service.capture_website(
                    url, 
                    output_path=screenshot_path
                )
                
                # Optimize image
                screenshot = ScreenshotService.optimize_image(screenshot)
                
                # Analyze screenshot
                print("Analyzing website design...")
                analysis = await self.analyze_screenshot(screenshot)
                
                return {
                    "analysis": analysis,
                    "url": url,
                    "screenshot_path": screenshot_path,
                    "analysis_type": "desktop_only"
                } 