#!/usr/bin/env python3
"""
Test script to verify Agentic Designer installation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
    except ImportError as e:
        print(f"❌ Playwright import failed: {e}")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_local_imports():
    """Test that local modules can be imported"""
    print("\n🔍 Testing local modules...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from design_schema import DesignSchema
        print("✅ DesignSchema module imported successfully")
    except ImportError as e:
        print(f"❌ DesignSchema import failed: {e}")
        return False
    
    try:
        from prompts import DesignPrompts
        print("✅ DesignPrompts module imported successfully")
    except ImportError as e:
        print(f"❌ DesignPrompts import failed: {e}")
        return False
    
    try:
        from screenshot_service import ScreenshotService
        print("✅ ScreenshotService module imported successfully")
    except ImportError as e:
        print(f"❌ ScreenshotService import failed: {e}")
        return False
    
    try:
        from vision_analyzer import VisionAnalyzer
        print("✅ VisionAnalyzer module imported successfully")
    except ImportError as e:
        print(f"❌ VisionAnalyzer import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist"""
    print("\n🔍 Testing directories...")
    
    required_dirs = ["results", "screenshots"]
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"✅ Directory '{directory}' exists")
        else:
            print(f"❌ Directory '{directory}' missing")
            return False
    
    return True

def test_configuration():
    """Test configuration validation"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import Config
        
        # Test if API key is configured
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
            print("✅ OpenAI API key is configured")
            return True
        else:
            print("⚠️ OpenAI API key not configured (this is expected for initial setup)")
            print("💡 Edit the .env file to add your API key")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_playwright_browsers():
    """Test if Playwright browsers are installed"""
    print("\n🔍 Testing Playwright browsers...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["playwright", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "chromium" in result.stdout.lower():
            print("✅ Chromium browser is installed")
            return True
        else:
            print("❌ Chromium browser not found")
            print("💡 Run: playwright install chromium")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ Playwright browsers not properly installed")
        print("💡 Run: playwright install chromium")
        return False
    except FileNotFoundError:
        print("❌ Playwright CLI not found")
        print("💡 Install with: pip install playwright")
        return False

def main():
    """Run all tests"""
    print("🎨 Testing Agentic Designer Installation")
    print("=" * 50)
    
    tests = [
        ("External Dependencies", test_imports),
        ("Local Modules", test_local_imports),
        ("Directories", test_directories),
        ("Configuration", test_configuration),
        ("Playwright Browsers", test_playwright_browsers),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation is ready.")
        print("\n🚀 Quick start:")
        print("• Web interface: python api.py")
        print("• CLI: python main.py https://example.com")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        
        if passed >= total - 1:  # Only config failed
            print("\n💡 If only configuration failed, you just need to:")
            print("1. Edit the .env file")
            print("2. Add your OpenAI API key")
            print("3. Run this test again")

if __name__ == "__main__":
    main() 