#!/usr/bin/env python3
"""
Test script for Enhanced AgentFlux
Demonstrates the complete workflow with component segmentation and A/B testing
"""

import asyncio
import os
from main_enhanced import EnhancedAgentFlux


async def test_enhanced_workflow():
    """Test the enhanced AgentFlux workflow"""
    
    print("🧪 Testing Enhanced AgentFlux Workflow")
    print("=" * 50)
    
    # Test URL
    test_url = "https://www.agentops.ai/"
    
    # Initialize Enhanced AgentFlux
    enhanced_flux = EnhancedAgentFlux()
    
    try:
        print(f"🎯 Testing with URL: {test_url}")
        print("📋 This will:")
        print("   1. Capture 4 scroll segments")
        print("   2. Analyze each component individually") 
        print("   3. Generate React code for each component")
        print("   4. Create A/B testing variations")
        print("   5. Generate GPT-Image-1 images for variations")
        print()
        
        # Run with pattern 1 (Hero-First Layout) for testing
        results = await enhanced_flux.run_complete_analysis(
            url=test_url,
            ab_pattern="1",  # Hero-First Layout for testing
            output_dir="test_enhanced_output"
        )
        
        print("\n🎉 Test completed successfully!")
        print("\n📁 Generated files:")
        
        # List generated files
        output_dir = "test_enhanced_output"
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, output_dir)
                    print(f"   📄 {rel_path}")
        
        print(f"\n✅ All test results saved to: {output_dir}/")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


async def test_component_segmentation_only():
    """Test just the component segmentation feature"""
    
    print("\n🔧 Testing Component Segmentation Only")
    print("-" * 40)
    
    from component_segmenter import ComponentSegmenter
    
    segmenter = ComponentSegmenter()
    test_url = "https://www.agentops.ai/"
    
    try:
        component_map = await segmenter.segment_and_analyze(test_url)
        
        print(f"✅ Segmentation successful!")
        print(f"   • {component_map['metadata']['total_segments']} segments captured")
        print(f"   • {len(component_map['react_components'])} React components generated")
        
        # Save results
        await segmenter.save_component_map(component_map, "test_components")
        print("💾 Component map saved to: test_components/")
        
    except Exception as e:
        print(f"❌ Component segmentation test failed: {str(e)}")


async def test_ab_generation_only():
    """Test just the A/B testing generation feature"""
    
    print("\n🧪 Testing A/B Generation Only")
    print("-" * 40)
    
    from ab_test_generator import ABTestGenerator
    
    ab_generator = ABTestGenerator()
    
    # Create mock component map for testing
    mock_component_map = {
        "metadata": {
            "url": "https://test.com",
            "total_segments": 4
        },
        "component_hierarchy": {
            "navigation": [],
            "hero": [],
            "content": [],
            "footer": []
        },
        "react_components": {
            "segment_1_top": "// Mock React component",
            "segment_2_quarter": "// Mock React component"
        }
    }
    
    try:
        # Test with pattern 2 (Feature-Grid Layout)
        ab_package = await ab_generator.generate_ab_variations(
            mock_component_map,
            selected_pattern="2"
        )
        
        print(f"✅ A/B generation successful!")
        print(f"   • {ab_package['metadata']['total_variations']} variations generated")
        print(f"   • Pattern: {ab_package['metadata']['selected_pattern']}")
        
        # Save results
        await ab_generator.save_ab_test_package(ab_package, "test_ab_tests")
        print("💾 A/B test package saved to: test_ab_tests/")
        
    except Exception as e:
        print(f"❌ A/B generation test failed: {str(e)}")


async def main():
    """Run all tests"""
    
    print("🚀 Enhanced AgentFlux Test Suite")
    print("=" * 60)
    
    # Test individual components first
    await test_component_segmentation_only()
    await test_ab_generation_only()
    
    # Test complete workflow
    await test_enhanced_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("📁 Check the following directories for results:")
    print("   • test_components/ - Component segmentation results")
    print("   • test_ab_tests/ - A/B testing results")
    print("   • test_enhanced_output/ - Complete workflow results")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 