#!/usr/bin/env python3
"""
Stylizer Module - Creates stylized versions of variation images using Replicate
Applies each style preset from style_presets.py to quality-controlled images
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import replicate
import aiohttp
from agentops.sdk.decorators import agent, tool
from style_presets import STYLE_PRESETS, get_all_style_names


@agent
class VariationStylizer:
    """Create stylized versions of variation images using Replicate's flux-kontext-pro"""

    def __init__(self, replicate_api_token: Optional[str] = None):
        """
        Initialize the stylizer with Replicate API token

        Args:
            replicate_api_token: Optional Replicate API token. If not provided, 
                               will look for REPLICATE_API_TOKEN env var
        """
        if replicate_api_token:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        elif not os.environ.get("REPLICATE_API_TOKEN"):
            raise ValueError(
                "REPLICATE_API_TOKEN not found. Please provide token or set environment variable.")

        print("🎨 Initialized Variation Stylizer with Replicate")

    @tool
    async def stylize_all_variations(
        self,
        ab_test_package: Dict[str, Any],
        output_dir: str = "stylized_variations",
        styles_to_apply: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Apply style presets to all variation images in the A/B test package

        Args:
            ab_test_package: The complete A/B test package with variations
            output_dir: Directory to save stylized images
            styles_to_apply: Optional list of style names to apply. If None, applies all styles

        Returns:
            Dictionary with stylization results
        """
        print("\n🎨 Starting Stylization Process")
        print("=" * 60)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Determine which styles to apply
        if styles_to_apply:
            selected_styles = [
                s for s in STYLE_PRESETS if s["name"] in styles_to_apply]
        else:
            selected_styles = STYLE_PRESETS

        print(f"📋 Styles to apply: {len(selected_styles)}")
        print(
            f"🎯 Variations to process: {ab_test_package['metadata']['total_variations']}")

        stylization_results = {
            "metadata": {
                "stylization_timestamp": datetime.now().isoformat(),
                "total_styles": len(selected_styles),
                "total_variations": ab_test_package['metadata']['total_variations'],
                "model": "black-forest-labs/flux-kontext-pro"
            },
            "stylized_variations": {}
        }

        # Process each variation
        for variation_key, variation in ab_test_package.get("variations", {}).items():
            print(f"\n🔄 Processing {variation_key}: {variation['name']}")

            # Get the image path (prefer quality-improved version if available)
            image_path = self._get_best_image_path(variation)

            if not image_path:
                print(f"  ⚠️  No image found for {variation_key}, skipping...")
                continue

            # Create output directory for this variation
            variation_output_dir = os.path.join(output_dir, variation_key)
            os.makedirs(variation_output_dir, exist_ok=True)

            # Apply each style
            stylized_images = await self._apply_styles_to_image(
                image_path,
                selected_styles,
                variation_output_dir,
                variation_key
            )

            stylization_results["stylized_variations"][variation_key] = {
                "original_variation": variation['name'],
                "source_image": image_path,
                "stylized_images": stylized_images
            }

        # Save stylization results
        results_file = os.path.join(output_dir, "stylization_results.json")
        with open(results_file, 'w') as f:
            json.dump(stylization_results, f, indent=2)

        print(f"\n✅ Stylization complete! Results saved to: {results_file}")
        self._display_stylization_summary(stylization_results)

        return stylization_results

    def _get_best_image_path(self, variation: Dict[str, Any]) -> Optional[str]:
        """Get the best available image path for a variation (prefer quality-improved)"""
        generated_image = variation.get("generated_image", {})

        # Check if quality was improved and use that image
        if generated_image.get("quality_improved", False):
            return generated_image.get("local_path")

        # Otherwise use the original generated image
        return generated_image.get("local_path")

    async def _apply_styles_to_image(
        self,
        image_path: str,
        styles: List[Dict[str, Any]],
        output_dir: str,
        variation_key: str
    ) -> List[Dict[str, Any]]:
        """Apply multiple styles to a single image"""
        stylized_results = []

        # Process styles in batches to avoid overwhelming the API
        batch_size = 5
        for i in range(0, len(styles), batch_size):
            batch = styles[i:i + batch_size]

            # Process batch concurrently
            tasks = []
            for style in batch:
                task = self._stylize_single_image(
                    image_path,
                    style,
                    output_dir,
                    variation_key
                )
                tasks.append(task)

            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for style, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    print(f"    ❌ Failed to apply {style['name']}: {result}")
                    stylized_results.append({
                        "style_name": style["name"],
                        "error": str(result)
                    })
                else:
                    stylized_results.append(result)

            # Small delay between batches
            if i + batch_size < len(styles):
                await asyncio.sleep(2)

        return stylized_results

    async def _stylize_single_image(
        self,
        image_path: str,
        style: Dict[str, Any],
        output_dir: str,
        variation_key: str
    ) -> Dict[str, Any]:
        """Apply a single style to an image using Replicate"""
        print(f"    🎨 Applying style: {style['name']}")

        try:
            # Prepare the prompt with style instructions
            style_prompt = f"Apply this exact style: {style['prompt']}"

            # Open the input image
            with open(image_path, "rb") as input_image:
                # Run the Replicate model
                output = await asyncio.to_thread(
                    replicate.run,
                    "black-forest-labs/flux-kontext-pro",
                    input={
                        "prompt": style_prompt,
                        "input_image": input_image,
                        "output_format": "png"
                    }
                )

            # Generate output filename
            safe_style_name = style['name'].lower().replace(
                ' ', '_').replace('-', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{variation_key}_{safe_style_name}_{timestamp}.png"
            output_path = os.path.join(output_dir, output_filename)

            # Save the stylized image
            # Replicate returns an iterator - we need to consume it
            if hasattr(output, '__iter__') and not isinstance(output, (str, bytes)):
                # If output is an iterator, get the first item
                output_list = list(output)
                if output_list:
                    output = output_list[0]
                    print(
                        f"      📥 Replicate returned: {type(output)} - {str(output)[:100] if isinstance(output, str) else 'non-string'}")
                else:
                    raise ValueError("No output from Replicate model")

            # Now handle the actual output
            if hasattr(output, 'read'):
                # If output is a file-like object
                with open(output_path, "wb") as f:
                    f.write(output.read())
            elif isinstance(output, bytes):
                # If output is bytes
                with open(output_path, "wb") as f:
                    f.write(output)
            elif isinstance(output, str) and output.startswith('http'):
                # If output is a URL, download it
                async with aiohttp.ClientSession() as session:
                    async with session.get(output) as response:
                        # Check if the request was successful
                        if response.status != 200:
                            raise ValueError(
                                f"Failed to download image: HTTP {response.status}")

                        # Check content type
                        content_type = response.headers.get('Content-Type', '')
                        if 'image' not in content_type:
                            raise ValueError(
                                f"Invalid content type: {content_type}")

                        # Read the content
                        content = await response.read()

                        # Verify we got actual content
                        # PNG files should be at least 1KB
                        if not content or len(content) < 1000:
                            raise ValueError(
                                f"Downloaded content too small: {len(content)} bytes")

                        # Save the file
                        with open(output_path, "wb") as f:
                            f.write(content)

                        # Verify the file was written correctly
                        if os.path.getsize(output_path) != len(content):
                            raise ValueError(
                                "File size mismatch after writing")
            else:
                # Handle other output types
                raise ValueError(f"Unexpected output type: {type(output)}")

            print(f"      ✅ Saved: {output_filename}")

            return {
                "style_name": style["name"],
                "style_description": style["prompt"][:100] + "...",
                "output_path": output_path,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            raise

    def _display_stylization_summary(self, results: Dict[str, Any]):
        """Display a summary of the stylization results"""
        print("\n" + "🎨 STYLIZATION SUMMARY" + " " * 20)
        print("=" * 60)

        total_images = 0
        successful_styles = 0

        for variation_key, variation_data in results["stylized_variations"].items():
            stylized_images = variation_data.get("stylized_images", [])
            successful = [s for s in stylized_images if "output_path" in s]

            print(f"\n📊 {variation_key}:")
            print(f"   • Total styles applied: {len(stylized_images)}")
            print(f"   • Successful: {len(successful)}")

            total_images += len(stylized_images)
            successful_styles += len(successful)

        print(f"\n📈 OVERALL RESULTS:")
        print(
            f"   • Total images generated: {successful_styles}/{total_images}")
        print(
            f"   • Success rate: {(successful_styles/total_images*100):.1f}%")
        print("\n" + "=" * 60)

    @tool
    async def create_style_gallery(
        self,
        stylization_results: Dict[str, Any],
        output_file: str = "style_gallery.html"
    ) -> str:
        """Create an HTML gallery to view all stylized variations"""

        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>AgentFlux Stylized Variations Gallery</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        h1, h2, h3 {
            color: #333;
        }
        .variation-section {
            margin-bottom: 40px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .style-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .style-card {
            background: #f9f9f9;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s;
        }
        .style-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .style-card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        .style-info {
            padding: 15px;
        }
        .style-name {
            font-weight: 600;
            margin-bottom: 5px;
        }
        .style-description {
            font-size: 14px;
            color: #666;
            line-height: 1.4;
        }
        .error {
            color: #e74c3c;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>🎨 AgentFlux Stylized Variations Gallery</h1>
    <p>Generated on: {timestamp}</p>
"""

        # Add each variation section
        for variation_key, variation_data in stylization_results["stylized_variations"].items():
            html_content += f"""
    <div class="variation-section">
        <h2>{variation_key.replace('_', ' ').title()}</h2>
        <p>Original: {variation_data['original_variation']}</p>
        <div class="style-grid">
"""

            # Add each stylized image
            for style_result in variation_data["stylized_images"]:
                if "error" in style_result:
                    html_content += f"""
            <div class="style-card">
                <div class="style-info">
                    <div class="style-name">{style_result['style_name']}</div>
                    <div class="error">Error: {style_result['error']}</div>
                </div>
            </div>
"""
                else:
                    # Get relative path for the image
                    img_path = os.path.relpath(style_result['output_path'])
                    html_content += f"""
            <div class="style-card">
                <img src="{img_path}" alt="{style_result['style_name']}">
                <div class="style-info">
                    <div class="style-name">{style_result['style_name']}</div>
                    <div class="style-description">{style_result['style_description']}</div>
                </div>
            </div>
"""

            html_content += """
        </div>
    </div>
"""

        html_content += """
</body>
</html>
"""

        # Save the HTML file
        html_content = html_content.format(
            timestamp=stylization_results["metadata"]["stylization_timestamp"]
        )

        with open(output_file, 'w') as f:
            f.write(html_content)

        print(f"\n🖼️  Style gallery created: {output_file}")
        return output_file


# Convenience function for command-line usage
@tool
async def stylize_from_ab_test_file(
    ab_test_file: str,
    output_dir: str = "stylized_variations",
    styles: Optional[List[str]] = None,
    create_gallery: bool = True
):
    """
    Stylize variations from a saved A/B test package file

    Args:
        ab_test_file: Path to the A/B test package JSON file
        output_dir: Directory to save stylized images
        styles: Optional list of style names to apply
        create_gallery: Whether to create an HTML gallery
    """
    # Load the A/B test package
    with open(ab_test_file, 'r') as f:
        ab_test_package = json.load(f)

    # Initialize stylizer
    stylizer = VariationStylizer()

    # Apply styles
    results = await stylizer.stylize_all_variations(
        ab_test_package,
        output_dir,
        styles
    )

    # Create gallery if requested
    if create_gallery:
        gallery_path = os.path.join(output_dir, "style_gallery.html")
        await stylizer.create_style_gallery(results, gallery_path)

    return results
