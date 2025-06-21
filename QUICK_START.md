# 🚀 Quick Start Guide

Your **Agentic Designer** system is ready! Follow these simple steps to start analyzing websites.

## ✅ Installation Status
- ✅ Virtual environment created
- ✅ All Python dependencies installed  
- ✅ All core modules working
- ✅ Directory structure ready
- ⚠️ OpenAI API key needed
- ⚠️ Playwright browsers (may need reinstall)

## 📝 Step 1: Configure API Key

1. **Edit the `.env` file**:
   ```bash
   nano .env
   ```

2. **Add your OpenAI API key**:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   OPENAI_MODEL=gpt-4-vision-preview
   SCREENSHOT_WIDTH=1920
   SCREENSHOT_HEIGHT=1080
   SCREENSHOT_TIMEOUT=30000
   ```

3. **Save and exit** (Ctrl+X, then Y, then Enter)

## 🔧 Step 2: Final Setup

```bash
# Activate virtual environment and install browsers
source venv/bin/activate
playwright install chromium
```

## 🎨 Step 3: Start Using the System

### Option A: Web Interface (Recommended)
```bash
source venv/bin/activate
python api.py
```
Then open http://localhost:8000 in your browser!

### Option B: Command Line
```bash
source venv/bin/activate
python main.py https://agentops.ai --summary
```

## 📊 Example Usage

### Web Interface
1. Visit `http://localhost:8000`
2. Enter a website URL (e.g., `https://agentops.ai`)
3. Choose options (mobile analysis, multi-stage, etc.)
4. Click "Analyze Design System"
5. Download results when complete

### Command Line Examples
```bash
# Basic analysis
python main.py https://stripe.com

# With mobile analysis and summary
python main.py https://airbnb.com --mobile --summary

# Custom output file
python main.py https://github.com --output github_analysis.json

# Fast single-stage analysis
python main.py https://example.com --no-multi-stage
```

## 📋 What You'll Get

The system extracts comprehensive design metadata including:

- **Typography**: Font families, weights, sizes, spacing
- **Colors**: Brand colors, neutrals, gradients, semantic colors
- **Layout**: Grid systems, breakpoints, spacing scales
- **Components**: Buttons, forms, navigation, cards
- **Visual Design**: Images, icons, logos, backgrounds
- **Interactions**: Animations, hover states, micro-interactions
- **Accessibility**: Contrast ratios, focus indicators
- **And 20+ more categories!**

## 🎯 Test with AgentOps.ai

Try analyzing the AgentOps website (from your example):
```bash
source venv/bin/activate
python main.py https://agentops.ai --summary
```

This will generate a comprehensive design system analysis similar to the example you provided, with precise typography, color palettes, layout specifications, and component details.

## 🔍 Troubleshooting

If you get errors:
1. **API Key Error**: Make sure your OpenAI API key is correctly set in `.env`
2. **Import Errors**: Always activate the virtual environment first: `source venv/bin/activate`
3. **Browser Errors**: Run `playwright install chromium` in the activated environment
4. **Network Errors**: Check your internet connection and website accessibility

## 🚀 You're Ready!

Your AI-powered design system extraction tool is ready to analyze any website with expert precision. The system uses advanced multi-stage prompting to extract design metadata with the eye of a designer and the precision of a developer.

Happy analyzing! 🎨 