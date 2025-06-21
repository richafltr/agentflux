#!/usr/bin/env python3
"""
Agentic Designer - AI-Powered Design System Extraction
Analyzes website screenshots using GPT-4 Vision to extract comprehensive design metadata
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from vision_analyzer import VisionAnalyzer
from config import Config
import agentops


class AgenticDesigner:
    """Main application class for the Agentic Designer system"""

    def __init__(self):
        self.analyzer = VisionAnalyzer()
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

        # Create screenshots directory
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)

    async def analyze_website(
        self,
        url: str,
        output_file: str = None,
        include_mobile: bool = False,
        save_screenshot: bool = True,
        multi_stage: bool = True
    ) -> dict:
        """
        Analyze a website and extract its design system

        Args:
            url: Website URL to analyze
            output_file: Optional output file path
            include_mobile: Include mobile view analysis
            save_screenshot: Save screenshot to file
            multi_stage: Use multi-stage analysis for better accuracy

        Returns:
            Design system analysis results
        """
        try:
            print(f"🎨 Starting design analysis for: {url}")
            print(
                f"📊 Multi-stage analysis: {'enabled' if multi_stage else 'disabled'}")
            print(
                f"📱 Mobile analysis: {'enabled' if include_mobile else 'disabled'}")
            print("-" * 60)

            # Perform analysis
            results = await self.analyzer.analyze_website(
                url=url,
                save_screenshot=save_screenshot,
                include_mobile=include_mobile
            )

            # Add metadata
            results["metadata"] = {
                "analysis_timestamp": datetime.now().isoformat(),
                "multi_stage_analysis": multi_stage,
                "include_mobile": include_mobile,
                "tool_version": "1.0.0"
            }

            # Save results
            if output_file:
                output_path = Path(output_file)
            else:
                # Generate filename from URL
                safe_url = url.replace(
                    'https://', '').replace('http://', '').replace('/', '_')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.results_dir / f"{safe_url}_{timestamp}.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"✅ Analysis complete!")
            print(f"📄 Results saved to: {output_path}")

            if save_screenshot and results.get("screenshot_path"):
                print(f"📸 Screenshot saved to: {results['screenshot_path']}")

            return results

        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            raise

    def print_summary(self, results: dict):
        """Print a summary of the analysis results"""

        if results.get("analysis_type") == "multi_device":
            print("\n🖥️  DESKTOP ANALYSIS SUMMARY")
            self._print_analysis_summary(results["desktop_analysis"])
            print("\n📱 MOBILE ANALYSIS SUMMARY")
            self._print_analysis_summary(results["mobile_analysis"])
        else:
            print("\n📊 ANALYSIS SUMMARY")
            self._print_analysis_summary(results["analysis"])

    def _print_analysis_summary(self, analysis: dict):
        """Print summary for a single analysis"""

        print("-" * 40)

        # Typography summary
        if "Typography" in analysis:
            typography = analysis["Typography"]
            if isinstance(typography, dict):
                fonts = typography.get(
                    "Primary, secondary & fallback font families (web-safe or web-hosted)", [])
                if fonts:
                    print(
                        f"🔤 Primary Font: {fonts[0] if isinstance(fonts, list) else fonts}")

        # Color summary
        if "Color & Contrast" in analysis:
            colors = analysis["Color & Contrast"]
            if isinstance(colors, dict):
                primary_colors = colors.get(
                    "Brand primaries, secondaries, accents (hex/RGB/HSL)", {})
                if primary_colors:
                    print(f"🎨 Brand Colors: {list(primary_colors.keys())[:3]}")

        # Layout summary
        if "Layout & Grid System" in analysis:
            layout = analysis["Layout & Grid System"]
            if isinstance(layout, dict):
                max_width = layout.get(
                    "Maximum content width / full-bleed rules", "")
                if max_width:
                    print(f"📐 Max Width: {max_width}")

        # Mood summary
        if "Tone & Mood Descriptors" in analysis:
            mood = analysis["Tone & Mood Descriptors"]
            if isinstance(mood, dict):
                adjectives = mood.get(
                    "Three-to-five adjectives defining the visual vibe (e.g., 'clean, approachable, tech-forward')", [])
                if adjectives:
                    print(f"✨ Design Vibe: {', '.join(adjectives)}")

        print("-" * 40)


async def main():
    """Main application entry point"""

    parser = argparse.ArgumentParser(
        description="Agentic Designer - Extract design systems from website screenshots using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://agentops.ai
  python main.py https://stripe.com --mobile --output stripe_analysis.json
  python main.py https://airbnb.com --no-multi-stage --summary
        """
    )

    parser.add_argument(
        "url",
        help="Website URL to analyze"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated in results/)"
    )

    parser.add_argument(
        "-m", "--mobile",
        action="store_true",
        help="Include mobile view analysis"
    )

    parser.add_argument(
        "--no-screenshot",
        action="store_true",
        help="Don't save screenshot to file"
    )

    parser.add_argument(
        "--no-multi-stage",
        action="store_true",
        help="Use single-stage analysis (faster but less accurate)"
    )

    parser.add_argument(
        "-s", "--summary",
        action="store_true",
        help="Print analysis summary to console"
    )

    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )

    args = parser.parse_args()

    # Validate configuration
    try:
        Config.validate()
        if args.validate_config:
            print("✅ Configuration is valid")
            return 0
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure to set your OPENAI_API_KEY environment variable")
        print("   You can also create a .env file with: OPENAI_API_KEY=your_key_here")
        return 1

    # Initialize application
    app = AgenticDesigner()

    try:
        # Run analysis
        results = await app.analyze_website(
            url=args.url,
            output_file=args.output,
            include_mobile=args.mobile,
            save_screenshot=not args.no_screenshot,
            multi_stage=not args.no_multi_stage
        )

        # Print summary if requested
        if args.summary:
            app.print_summary(results)

        return 0

    except KeyboardInterrupt:
        print("\n⏸️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    agentops.init(tags=["agentops-design-system-extraction"])
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted")
        sys.exit(1)
