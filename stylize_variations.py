#!/usr/bin/env python3
"""
Standalone script to apply style presets to existing A/B test variations
Can be run independently after main_enhanced.py has generated variations
"""

import asyncio
import argparse
import json
import os
from pathlib import Path
import agentops
from stylizer import VariationStylizer, stylize_from_ab_test_file
from style_presets import get_all_style_names


async def main():
    """Main function for standalone stylization"""

    # Initialize AgentOps
    agentops.init(tags=["agentflux-stylizer"])

    parser = argparse.ArgumentParser(
        description="Apply style presets to existing A/B test variations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stylize variations from a specific A/B test package file
  python stylize_variations.py ab_tests/ab_test_package_20250621_120000.json
  
  # Apply only specific styles
  python stylize_variations.py ab_tests/ab_test_package_20250621_120000.json --styles "Neo-Brutalism,Glassmorphism,Dark Luxury"
  
  # Custom output directory
  python stylize_variations.py ab_tests/ab_test_package_20250621_120000.json --output my_stylized_variations
  
  # List all available styles
  python stylize_variations.py --list-styles
        """
    )

    parser.add_argument(
        "ab_test_file",
        nargs="?",
        help="Path to the A/B test package JSON file"
    )

    parser.add_argument(
        "--styles",
        type=str,
        help="Comma-separated list of style names to apply. If not specified, all styles will be applied."
    )

    parser.add_argument(
        "--output",
        default="outputs/stylized",
        help="Output directory for stylized images (default: outputs/stylized)"
    )

    parser.add_argument(
        "--no-gallery",
        action="store_true",
        help="Skip creating the HTML gallery"
    )

    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List all available style presets and exit"
    )

    args = parser.parse_args()

    # List styles if requested
    if args.list_styles:
        print("🎨 Available Style Presets:")
        print("=" * 60)
        for i, style_name in enumerate(get_all_style_names(), 1):
            print(f"{i:2d}. {style_name}")
        print("=" * 60)
        return 0

    # Check if A/B test file was provided
    if not args.ab_test_file:
        print("❌ Error: Please provide an A/B test package file to stylize")
        print("   Run with --help for usage examples")
        return 1

    # Check if file exists
    if not os.path.exists(args.ab_test_file):
        print(f"❌ Error: File not found: {args.ab_test_file}")
        return 1

    # Parse style names if provided
    style_names = None
    if args.styles:
        style_names = [s.strip() for s in args.styles.split(',')]
        print(f"📋 Selected styles: {', '.join(style_names)}")
    else:
        print("📋 Applying all 20 style presets")

    # Check for Replicate API token
    if not os.environ.get("REPLICATE_API_TOKEN"):
        print("\n⚠️  REPLICATE_API_TOKEN not found in environment variables")
        print("   Please set it before running:")
        print("   export REPLICATE_API_TOKEN='your-api-token'")
        return 1

    try:
        # Run stylization
        print(
            f"\n🎨 Starting stylization of variations from: {args.ab_test_file}")
        print(f"📁 Output directory: {args.output}")
        print("=" * 60)

        results = await stylize_from_ab_test_file(
            args.ab_test_file,
            output_dir=args.output,
            styles=style_names,
            create_gallery=not args.no_gallery
        )

        print("\n✅ Stylization completed successfully!")
        print(
            f"📁 All stylized images saved to: {os.path.abspath(args.output)}/")

        # List the actual files created
        print("\n📂 CREATED FILES:")
        for root, dirs, files in os.walk(args.output):
            level = root.replace(args.output, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in sorted(files)[:10]:  # Show first 10 files
                if file.endswith('.png'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    print(f"{subindent}✓ {file} ({file_size // 1024}KB)")
            if len(files) > 10:
                print(f"{subindent}... and {len(files) - 10} more files")

        if not args.no_gallery:
            gallery_path = os.path.join(args.output, "style_gallery.html")
            abs_gallery_path = os.path.abspath(gallery_path)
            print(f"\n🖼️  View the gallery:")
            print(f"   file://{abs_gallery_path}")
            print(f"\n   Or run: open {abs_gallery_path}")

        return 0

    except Exception as e:
        print(f"\n❌ Stylization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
