#!/usr/bin/env python3
"""
Setup script for Agentic Designer
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_directories():
    """Create necessary directories"""
    directories = ["results", "screenshots", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_env_file():
    """Create .env file template if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Agentic Designer Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-vision-preview
SCREENSHOT_WIDTH=1920
SCREENSHOT_HEIGHT=1080
SCREENSHOT_TIMEOUT=30000
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("📝 Created .env file template")
        print("💡 Please edit .env file and add your OpenAI API key")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🎨 Setting up Agentic Designer...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browsers"):
        print("❌ Failed to install Playwright browsers")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("2. Run the web interface: python api.py")
    print("3. Or use the CLI: python main.py https://example.com")
    print("\n💡 For more information, see the README.md file")

if __name__ == "__main__":
    main() 