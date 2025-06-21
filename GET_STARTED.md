# 🚀 Get Started with AgentFlux

**AgentFlux** is an AI-powered design system analyzer that extracts comprehensive design metadata from websites with "designer's eye and coder's precision."

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **OpenAI API key** (get one at [platform.openai.com](https://platform.openai.com/api-keys))
- **Git** for cloning the repository

## ⚡ Quick Start (5 minutes)

### 1. Clone and Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd agentflux

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Configure Your API Key
```bash
# Copy the environment template
cp env.template .env.local

# Edit with your API key
nano .env.local  # or use your preferred editor
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o
```

### 3. Test the Installation
```bash
# Run the test (with venv activated)
python test_installation.py
```

### 4. Analyze Your First Website
```bash
# Analyze a website (CLI)
python main.py https://www.agentops.ai/ --output analysis.json --summary

# Or start the web interface
python web_app.py
# Then visit http://localhost:8000
```

### 🚀 One-Liner Setup (after cloning)
```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && playwright install && python main.py https://www.agentops.ai/ --output agentops_analysis.json --summary
```

## 🎯 Usage Examples

### Command Line Interface

**Basic Analysis:**
```bash
python main.py https://www.stripe.com --output stripe_analysis.json
```

**With Summary:**
```bash
python main.py https://www.airbnb.com --summary --output airbnb_analysis.json
```

**Multi-stage Analysis (Enhanced Accuracy):**
```bash
python main.py https://www.figma.com --output figma_analysis.json --summary
# Multi-stage is enabled by default
```

**Single-stage Analysis (Faster):**
```bash
python main.py https://www.notion.so --no-multi-stage --output notion_analysis.json
```

**Include Mobile Analysis:**
```bash
python main.py https://www.spotify.com --mobile --output spotify_analysis.json
```

### Web Interface

1. **Start the server:**
   ```bash
   python web_app.py
   ```

2. **Open your browser:** http://localhost:8000

3. **Enter a URL** and click "Analyze Design"

4. **View results** in real-time with beautiful visualizations

## 📊 What You Get

AgentFlux extracts **24+ design categories** including:

### 🎨 **Core Design Elements**
- **Typography:** Font families, weights, sizes, line heights
- **Colors:** Brand palette, neutrals, gradients, semantic colors
- **Layout:** Grid system, breakpoints, spacing patterns
- **Components:** Buttons, forms, cards, navigation

### 🔧 **Technical Specifications**
- **Exact measurements:** px, rem, percentages
- **CSS properties:** padding, margins, border-radius
- **Responsive breakpoints:** mobile, tablet, desktop
- **State variations:** hover, focus, active, disabled

### 📋 **Output Formats**
- **JSON:** Structured data for developers
- **Summary:** Human-readable overview
- **Screenshots:** High-quality captures

## 🛠 Configuration Options

### Environment Variables (.env.local)
```env
# Required
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o

# Screenshot Settings
SCREENSHOT_WIDTH=1920
SCREENSHOT_HEIGHT=1080
SCREENSHOT_QUALITY=80

# Analysis Settings
MAX_TOKENS=4000
TEMPERATURE=0.0
ANALYSIS_TIMEOUT=120

# Web App Settings
WEB_HOST=localhost
WEB_PORT=8000
```

### Command Line Options
```bash
python main.py --help
```

## 📁 Project Structure

```
agentflux/
├── main.py              # CLI interface
├── web_app.py           # Web interface
├── api.py               # FastAPI backend
├── vision_analyzer.py   # AI analysis engine
├── screenshot_service.py # Screenshot capture
├── design_schema.py     # Design system schema
├── prompts.py           # AI prompts
├── config.py            # Configuration
├── setup.py             # Installation script
├── test_installation.py # System verification
├── env.template         # Environment template
├── requirements.txt     # Dependencies
├── screenshots/         # Generated screenshots
└── results/            # Analysis results
```

## 🔍 Example Analysis Output

```json
{
  "analysis": {
    "Typography": {
      "Primary, secondary & fallback font families": [
        "Primary: Inter, sans-serif",
        "Secondary: Georgia, serif"
      ],
      "Weight spectrum": [400, 500, 600, 700],
      "Heading sizes": {
        "h1": "48px",
        "h2": "36px",
        "h3": "24px"
      }
    },
    "Color & Contrast": {
      "Brand primaries": "#6366F1",
      "Neutral/gray scale": {
        "50": "#F9FAFB",
        "900": "#111827"
      }
    },
    "Buttons & Calls-to-Action": {
      "Primary button": {
        "backgroundColor": "#6366F1",
        "padding": "12px 24px",
        "borderRadius": "8px"
      }
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**"No module named 'playwright'"**
```bash
# Install playwright browsers
source venv/bin/activate
playwright install
```

**"Invalid API key"**
- Check your `.env.local` file
- Verify your OpenAI API key at platform.openai.com
- Ensure you have credits available

**"Analysis failed"**
- Check your internet connection
- Try a different website URL
- Use `--no-multi-stage` for faster analysis

**"Permission denied"**
```bash
# Fix permissions on macOS/Linux
chmod +x setup.py
```

### Getting Help

1. **Check the logs:** Look for error messages in the terminal
2. **Test installation:** Run `python test_installation.py`
3. **Try a simple site:** Start with `https://example.com`
4. **Check requirements:** Ensure Python 3.8+ and all dependencies

## 🎯 Pro Tips

### Best Practices
- **Use multi-stage analysis** for production-quality results
- **Include mobile analysis** for responsive design insights
- **Save screenshots** for visual reference
- **Use summaries** for quick overviews

### Performance Optimization
- **Single-stage analysis** for faster results
- **Adjust screenshot quality** to reduce API costs
- **Use smaller screenshot dimensions** for testing

### Advanced Usage
```bash
# Batch analyze multiple sites
for url in "site1.com" "site2.com" "site3.com"; do
  python main.py "https://$url" --output "${url}_analysis.json"
done

# Custom screenshot settings
SCREENSHOT_WIDTH=1440 SCREENSHOT_HEIGHT=900 python main.py https://example.com
```

## 🔄 Updates

Keep AgentFlux updated:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 🎉 You're Ready!

Start analyzing websites and extracting professional design systems with AI precision. Happy analyzing! 🚀

**Need help?** Check the full documentation in `README.md` or open an issue. 