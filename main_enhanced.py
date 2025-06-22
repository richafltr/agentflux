#!/usr/bin/env python3
"""
Enhanced AgentFlux - AI Design System Analyzer with A/B Testing Generator
Complete workflow: Screenshot → Component Segmentation → React Code → A/B Variations → Image Generation → Stylization
"""

import asyncio
import argparse
import json
import os
from datetime import datetime
from typing import Optional
import agentops
from component_segmenter import ComponentSegmenter
from ab_test_generator import ABTestGenerator
from screenshot_service import ScreenshotService
from stylizer import VariationStylizer


class EnhancedAgentFlux:
    """Enhanced AgentFlux with component segmentation, A/B testing, and stylization"""

    def __init__(self):
        self.segmenter = ComponentSegmenter()
        self.ab_generator = ABTestGenerator()
        self.stylizer = None  # Initialize only if stylization is requested

    async def run_complete_analysis(
        self,
        url: str,
        ab_pattern: Optional[str] = None,
        output_dir: str = "outputs",
        apply_styles: bool = False,
        style_names: Optional[list] = None
    ) -> dict:
        """
        Run the complete enhanced analysis workflow

        Args:
            url: Website URL to analyze
            ab_pattern: A/B testing pattern (1-4) or None for interactive selection
            output_dir: Output directory for all results
            apply_styles: Whether to apply style presets to variations
            style_names: Optional list of specific style names to apply

        Returns:
            Complete analysis results
        """
        print("🚀 Starting Enhanced AgentFlux Analysis")
        print("=" * 60)
        print(f"🎯 Target URL: {url}")
        print(f"📁 Output Directory: {output_dir}")
        if apply_styles:
            print(f"🎨 Style Application: Enabled")
        print("=" * 60)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Step 1: Component Segmentation & Analysis
            print("\n📋 STEP 1: Component Segmentation & Analysis")
            print("-" * 40)
            component_map = await self.segmenter.segment_and_analyze(url)

            # Save component analysis
            component_file = await self.segmenter.save_component_map(
                component_map,
                os.path.join(output_dir, "components")
            )
            print(f"✅ Component analysis saved: {component_file}")

            # Step 2: A/B Testing Variation Generation with Quality Check
            print("\n🧪 STEP 2: A/B Testing Variation Generation")
            print("-" * 40)
            print("• Generating variations with DALL-E...")
            print("• Running quality checks with GPT-4o...")
            print("• Applying improvements if needed...")
            ab_test_package = await self.ab_generator.generate_ab_variations(
                component_map,
                ab_pattern
            )

            # Save A/B testing package
            ab_test_file = await self.ab_generator.save_ab_test_package(
                ab_test_package,
                os.path.join(output_dir, "ab_tests")
            )
            print(f"✅ A/B test package saved: {ab_test_file}")

            # Step 3: Apply Style Presets (if requested)
            stylization_results = None
            if apply_styles:
                print("\n🎨 STEP 3: Applying Style Presets with Replicate")
                print("-" * 40)

                # Initialize stylizer if not already done
                if self.stylizer is None:
                    try:
                        self.stylizer = VariationStylizer()
                    except ValueError as e:
                        print(f"⚠️  Stylization skipped: {e}")
                        print(
                            "   Please set REPLICATE_API_TOKEN environment variable to enable stylization")
                        apply_styles = False

                if apply_styles:
                    stylization_results = await self.stylizer.stylize_all_variations(
                        ab_test_package,
                        output_dir=os.path.join(
                            output_dir, "stylized"),
                        styles_to_apply=style_names
                    )

                    # Create style gallery
                    gallery_path = os.path.join(
                        output_dir, "stylized", "style_gallery.html")
                    await self.stylizer.create_style_gallery(stylization_results, gallery_path)
                    print(f"✅ Style gallery created: {gallery_path}")

            # Step 4: Generate Summary Report
            step_number = 4 if apply_styles else 3
            print(f"\n📊 STEP {step_number}: Generating Summary Report")
            print("-" * 40)
            summary = self._generate_summary_report(
                component_map, ab_test_package, stylization_results)

            summary_file = os.path.join(output_dir, "analysis_summary.json")
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            print(f"✅ Summary report saved: {summary_file}")

            # Step 5: Display Results
            self._display_results(summary)

            return {
                "component_analysis": component_map,
                "ab_test_package": ab_test_package,
                "stylization_results": stylization_results,
                "summary": summary,
                "output_directory": output_dir
            }

        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            raise

    def _generate_summary_report(self, component_map: dict, ab_test_package: dict, stylization_results: Optional[dict] = None) -> dict:
        """Generate a comprehensive summary report"""

        # Count quality improvements
        quality_improvements = 0
        quality_issues_found = 0
        for variation_key, variation in ab_test_package.get("variations", {}).items():
            if "generated_image" in variation and "quality_check" in variation["generated_image"]:
                quality_check = variation["generated_image"]["quality_check"]
                if quality_check.get("has_issues", False):
                    quality_issues_found += len(
                        quality_check.get("issues", []))
                if variation["generated_image"].get("quality_improved", False):
                    quality_improvements += 1

        summary = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "url": component_map["metadata"]["url"],
                "tool_version": "Enhanced AgentFlux v3.0 with Quality Assurance & Stylization"
            },
            "component_analysis": {
                "total_segments": component_map["metadata"]["total_segments"],
                "react_components_generated": len(component_map["react_components"]),
                "component_categories": list(component_map["component_hierarchy"].keys())
            },
            "ab_testing": {
                "total_variations": ab_test_package["metadata"]["total_variations"],
                "selected_pattern": ab_test_package["metadata"]["selected_pattern"],
                "variations_generated": list(ab_test_package["variations"].keys()),
                "quality_issues_found": quality_issues_found,
                "quality_improvements_applied": quality_improvements
            },
            "deliverables": {
                "component_json_maps": "✅ Generated",
                "react_components": "✅ Generated",
                "ab_test_variations": "✅ Generated",
                "dalle_generated_images": "✅ Generated with Quality Check",
                "implementation_ready": "✅ Ready"
            },
            "next_steps": [
                "Review generated React components",
                "Test A/B variations with real traffic",
                "Implement conversion tracking",
                "Monitor performance metrics"
            ]
        }

        # Add stylization information if available
        if stylization_results:
            total_stylized = 0
            for var_data in stylization_results.get("stylized_variations", {}).values():
                successful = [s for s in var_data.get(
                    "stylized_images", []) if "output_path" in s]
                total_stylized += len(successful)

            summary["stylization"] = {
                "styles_applied": stylization_results["metadata"]["total_styles"],
                "total_stylized_images": total_stylized,
                "gallery_created": True
            }
            summary["deliverables"]["stylized_variations"] = "✅ Generated"
            summary["deliverables"]["style_gallery"] = "✅ Created"

        return summary

    def _display_results(self, summary: dict):
        """Display analysis results in a beautiful format"""

        print("\n" + "🎉 ANALYSIS COMPLETE!" + " " * 20)
        print("=" * 60)

        print(f"\n📊 COMPONENT ANALYSIS:")
        print(
            f"   • {summary['component_analysis']['total_segments']} scroll segments analyzed")
        print(
            f"   • {summary['component_analysis']['react_components_generated']} React components generated")
        print(
            f"   • {len(summary['component_analysis']['component_categories'])} component categories")

        print(f"\n🧪 A/B TESTING VARIATIONS:")
        print(
            f"   • {summary['ab_testing']['total_variations']} variations generated")
        print(f"   • Pattern: {summary['ab_testing']['selected_pattern']}")
        print(
            f"   • Variations: {', '.join(summary['ab_testing']['variations_generated'])}")

        if summary['ab_testing'].get('quality_issues_found', 0) > 0:
            print(
                f"   • Quality issues found: {summary['ab_testing']['quality_issues_found']}")
            print(
                f"   • Quality improvements applied: {summary['ab_testing']['quality_improvements_applied']}")

        if 'stylization' in summary:
            print(f"\n🎨 STYLIZATION:")
            print(
                f"   • Styles applied: {summary['stylization']['styles_applied']}")
            print(
                f"   • Total stylized images: {summary['stylization']['total_stylized_images']}")
            print(
                f"   • Gallery created: {'Yes' if summary['stylization']['gallery_created'] else 'No'}")

        print(f"\n📦 DELIVERABLES:")
        for item, status in summary['deliverables'].items():
            print(f"   • {item.replace('_', ' ').title()}: {status}")

        print(f"\n🚀 NEXT STEPS:")
        for i, step in enumerate(summary['next_steps'], 1):
            print(f"   {i}. {step}")

        print("\n" + "=" * 60)
        print("🎯 Your enhanced design system analysis is ready!")
        print("   ✨ Now with automated quality checks and improvements!")
        if 'stylization' in summary:
            print("   🎨 Plus 20 unique stylized variations for each A/B test!")
        print("   Use the generated React components and A/B test variations")
        print("   to implement and test your optimized website designs.")
        print("=" * 60)


async def main():
    """Main CLI interface for Enhanced AgentFlux"""

    agentops.init(tags=["agentops-design-system-analyzer"])

    parser = argparse.ArgumentParser(
        description="Enhanced AgentFlux - AI Design System Analyzer with A/B Testing & Stylization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete analysis with interactive A/B pattern selection
  python main_enhanced.py https://www.agentops.ai/
  
  # Generate specific A/B testing pattern
  python main_enhanced.py https://www.stripe.com --ab-pattern 1
  
  # Generate all A/B variations
  python main_enhanced.py https://www.figma.com --ab-pattern all
  
  # Generate with stylized variations (all 20 styles)
  python main_enhanced.py https://www.notion.so --stylize
  
  # Generate with specific styles only
  python main_enhanced.py https://www.vercel.com --stylize --styles "Neo-Brutalism,Glassmorphism,Dark Luxury"
  
  # Custom output directory
  python main_enhanced.py https://www.notion.so --output custom_analysis
        """
    )

    parser.add_argument(
        "url",
        help="Website URL to analyze"
    )

    parser.add_argument(
        "--ab-pattern",
        choices=["1", "2", "3", "4", "all"],
        help="A/B testing pattern: 1=Hero-First, 2=Feature-Grid, 3=Content-Heavy, 4=Conversion-Optimized, all=Generate all patterns"
    )

    parser.add_argument(
        "--output",
        default="outputs",
        help="Output directory for analysis results (default: outputs)"
    )

    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip GPT-Image-1 image generation (faster, less cost)"
    )

    parser.add_argument(
        "--stylize",
        action="store_true",
        help="Apply style presets to variations using Replicate (requires REPLICATE_API_TOKEN)"
    )

    parser.add_argument(
        "--styles",
        type=str,
        help="Comma-separated list of style names to apply (e.g., 'Neo-Brutalism,Glassmorphism'). If not specified, all 20 styles will be applied."
    )

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url

    # Parse style names if provided
    style_names = None
    if args.styles:
        style_names = [s.strip() for s in args.styles.split(',')]
        print(f"📋 Selected styles: {', '.join(style_names)}")

    # Initialize Enhanced AgentFlux
    enhanced_flux = EnhancedAgentFlux()

    try:
        # Run complete analysis
        results = await enhanced_flux.run_complete_analysis(
            url=args.url,
            ab_pattern=args.ab_pattern,
            output_dir=args.output,
            apply_styles=args.stylize,
            style_names=style_names
        )

        print(f"\n✅ Analysis completed successfully!")
        print(f"📁 All results saved to: {args.output}/")

    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
