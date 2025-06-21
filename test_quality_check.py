#!/usr/bin/env python3
"""
Test script to demonstrate the quality check feature
"""

import asyncio
import json
from ab_test_generator import ABTestGenerator


async def test_quality_check():
    """Test the quality check feature with a sample image"""

    generator = ABTestGenerator()

    # Test with a variation image (you'll need to have one generated first)
    test_image_path = "variations/variation_20250621_160910.png"

    print("🔍 Testing Quality Check Feature")
    print("=" * 50)
    print(f"Test Image: {test_image_path}")
    print("-" * 50)

    try:
        # Run quality check
        quality_result = await generator._quality_check_image(test_image_path)

        # Display results
        print("\n📊 Quality Check Results:")
        print(f"Has Issues: {quality_result.get('has_issues', False)}")
        print(
            f"Overall Quality: {quality_result.get('overall_quality', 'Not assessed')}")
        print(
            f"Regeneration Needed: {quality_result.get('regeneration_needed', False)}")

        if quality_result.get('has_issues', False):
            print("\n🚨 Issues Found:")
            for i, issue in enumerate(quality_result.get('issues', []), 1):
                print(
                    f"\n{i}. {issue['type']} (Severity: {issue['severity']})")
                print(f"   Description: {issue['description']}")
                print(f"   Fix: {issue['fix']}")
        else:
            print("\n✅ No quality issues detected!")

        # Save results
        with open('quality_check_results.json', 'w') as f:
            json.dump(quality_result, f, indent=2)
        print("\n💾 Results saved to: quality_check_results.json")

    except FileNotFoundError:
        print(f"❌ Test image not found: {test_image_path}")
        print("   Please run the main analysis first to generate variation images.")
    except Exception as e:
        print(f"❌ Error during quality check: {e}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(test_quality_check())
