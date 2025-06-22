#!/usr/bin/env python3
"""
Stylizer Module - Creates stylized versions of variation images using Replicate
Applies each style preset from style_presets.py to quality-controlled images
"""

import os
import asyncio
import json
import base64
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import replicate
import aiohttp
from PIL import Image
import io
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
        output_dir: str = "outputs/stylized",
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
        abs_output_dir = os.path.abspath(output_dir)
        print(f"📂 Output directory (absolute path): {abs_output_dir}")

        # Determine which styles to apply
        if styles_to_apply:
            selected_styles = [
                s for s in STYLE_PRESETS if s["name"] in styles_to_apply]
        else:
            selected_styles = STYLE_PRESETS

        print(f"📋 Styles to apply: {len(selected_styles)} styles")
        print(
            f"🎨 Style list: {', '.join([s['name'] for s in selected_styles[:5]])}{'...' if len(selected_styles) > 5 else ''}")
        print(
            f"🎯 Variations to process: {ab_test_package['metadata']['total_variations']}")
        print(
            f"📁 Output files will be named: [style_name].png in {output_dir}/[variation]/")

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
            abs_variation_dir = os.path.abspath(variation_output_dir)

            # Check for existing files
            existing_files = [f for f in os.listdir(variation_output_dir) if f.endswith(
                '.png')] if os.path.exists(variation_output_dir) else []
            if existing_files:
                print(
                    f"  ⚠️  Found {len(existing_files)} existing files in {abs_variation_dir}")
                print(
                    f"     Files will be OVERWRITTEN: {', '.join(existing_files[:5])}{'...' if len(existing_files) > 5 else ''}")
            else:
                print(
                    f"  📁 Creating new output directory: {abs_variation_dir}")

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
            # Add timestamp to force new generation and avoid caching
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            style_prompt = f"Apply this exact style: {style['prompt']} [Generated at: {timestamp}]"

            # Open the input image - Replicate will handle the upload
            with open(image_path, "rb") as input_image:
                # Run the Replicate model
                output = await asyncio.to_thread(
                    replicate.run,
                    "black-forest-labs/flux-kontext-pro",
                    input={
                        "prompt": style_prompt,
                        "input_image": input_image,
                        "aspect_ratio": "match_input_image",
                        "output_format": "png",
                        "safety_tolerance": 2,
                        # Random seed
                        "seed": int(datetime.now().timestamp() * 1000) % 1000000
                    }
                )

            # Generate output filename - just use the style name
            safe_style_name = style['name'].lower().replace(
                ' ', '_').replace('-', '_')
            output_filename = f"{safe_style_name}.png"
            output_path = os.path.join(output_dir, output_filename)
            abs_output_path = os.path.abspath(output_path)

            # Check if file already exists
            if os.path.exists(output_path):
                print(
                    f"      ⚠️  File exists, will OVERWRITE: {abs_output_path}")
            else:
                print(f"      📝 Will create new file: {abs_output_path}")

            # Debug: Log what we received
            print(f"      📥 Replicate returned: {output}")

            # Handle Replicate's FileOutput object
            output_url = str(output)  # FileOutput converts to URL string

            # Output should be a URL string
            if output_url.startswith('http'):
                # Download the image from the URL
                print(f"      📥 Downloading from: {output_url}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(output_url) as response:
                        if response.status != 200:
                            raise ValueError(
                                f"Failed to download: HTTP {response.status}")

                        # Read and save the image
                        content = await response.read()

                        # EMERGENCY DEBUG
                        print(f"      🚨 ATTEMPTING TO SAVE TO: {output_path}")
                        print(
                            f"      🚨 ABSOLUTE PATH: {os.path.abspath(output_path)}")
                        print(
                            f"      🚨 DIRECTORY EXISTS: {os.path.exists(os.path.dirname(output_path))}")
                        print(f"      🚨 CWD: {os.getcwd()}")

                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(
                            output_path), exist_ok=True)
                        print(
                            f"      🚨 CREATED DIR: {os.path.dirname(output_path)}")

                        # Force overwrite by removing existing file first
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            print(f"      🗑️  Removed existing file")

                        # Debug: Show exactly where we're writing
                        print(
                            f"      📝 Writing {len(content)} bytes to: {output_path}")
                        print(
                            f"      📂 Current working directory: {os.getcwd()}")

                        with open(output_path, "wb") as f:
                            bytes_written = f.write(content)
                            f.flush()  # Force write to disk
                            os.fsync(f.fileno())  # Force OS to write to disk

                        # EMERGENCY VERIFY
                        print(
                            f"      🚨 FILE EXISTS AFTER WRITE: {os.path.exists(output_path)}")
                        print(
                            f"      🚨 ABSOLUTE PATH CHECK: {os.path.exists(os.path.abspath(output_path))}")

                        # List directory contents
                        if os.path.exists(os.path.dirname(output_path)):
                            files = os.listdir(os.path.dirname(output_path))
                            print(f"      🚨 FILES IN DIR: {files}")

                        # Verify file was written
                        if os.path.exists(output_path):
                            actual_size = os.path.getsize(output_path)
                            print(
                                f"      ✅ SAVED: {output_filename} ({actual_size} bytes)")
                            print(f"         Full path: {abs_output_path}")
                            print(f"         Bytes written: {bytes_written}")
                            print(
                                f"         File size matches: {actual_size == len(content)}")

                            # Generate checksum for verification
                            with open(output_path, 'rb') as f:
                                file_hash = hashlib.md5(f.read()).hexdigest()
                            print(f"         MD5: {file_hash}")
                        else:
                            raise ValueError(
                                f"Failed to save file at {abs_output_path}")
            else:
                raise ValueError(f"Expected URL but got: {output_url}")

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
        saved_files = []

        for variation_key, variation_data in results["stylized_variations"].items():
            stylized_images = variation_data.get("stylized_images", [])
            successful = [s for s in stylized_images if "output_path" in s]

            print(f"\n📊 {variation_key}:")
            print(f"   • Total styles applied: {len(stylized_images)}")
            print(f"   • Successful: {len(successful)}")

            if successful:
                print(
                    f"   • Files saved in: {os.path.abspath(os.path.dirname(successful[0]['output_path']))}")
                for img in successful[:5]:
                    saved_files.append(img['output_path'])
                    print(f"      ✓ {os.path.basename(img['output_path'])}")
                if len(successful) > 5:
                    print(f"      ... and {len(successful) - 5} more files")

            total_images += len(stylized_images)
            successful_styles += len(successful)

        print(f"\n📈 OVERALL RESULTS:")
        print(
            f"   • Total images generated: {successful_styles}/{total_images}")
        print(
            f"   • Success rate: {(successful_styles/total_images*100):.1f}%" if total_images > 0 else "   • Success rate: 0%")

        if saved_files:
            print(f"\n📁 FILES SAVED AT:")
            print(f"   {os.path.abspath(os.path.dirname(saved_files[0]))}")
            print(f"\n🔍 To view your results:")
            print(
                f"   open {os.path.abspath(os.path.dirname(saved_files[0]))}")

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
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .variation-section {{
            margin-bottom: 40px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .style-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .style-card {{
            background: #f9f9f9;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .style-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .style-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .style-info {{
            padding: 15px;
        }}
        .style-name {{
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .style-description {{
            font-size: 14px;
            color: #666;
            line-height: 1.4;
        }}
        .error {{
            color: #e74c3c;
            font-style: italic;
        }}
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
    output_dir: str = "outputs/stylized",
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
