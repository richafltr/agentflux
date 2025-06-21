# 🎨 Agentic Designer

An AI-powered design system extraction tool that analyzes website screenshots using GPT-4 Vision to extract comprehensive design metadata with a designer's eye and developer's precision.

## ✨ Features

- **🔍 Deep Analysis**: Extract typography, colors, spacing, layout patterns, and UI components
- **📱 Multi-Device Support**: Analyze both desktop and mobile views
- **⚡ Multi-Stage Analysis**: Advanced multi-stage analysis for enhanced accuracy
- **🌐 Web Interface**: Beautiful web UI for easy interaction
- **🔧 CLI Support**: Command-line interface for automation
- **📊 Comprehensive Schema**: 25+ design categories with detailed specifications
- **🎯 GPT-4 Vision**: Powered by OpenAI's latest vision model

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key with GPT-4 Vision access
- Internet connection for website screenshots

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agentflux
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4-vision-preview
   SCREENSHOT_WIDTH=1920
   SCREENSHOT_HEIGHT=1080
   SCREENSHOT_TIMEOUT=30000
   ```

### Usage

#### Web Interface (Recommended)

1. **Start the web server**:
   ```bash
   python api.py
   ```

2. **Open your browser** and go to `http://localhost:8000`

3. **Enter a website URL** and click "Analyze Design System"

4. **Download the results** when analysis is complete

#### Command Line Interface

1. **Basic analysis**:
   ```bash
   python main.py https://agentops.ai
   ```

2. **With mobile analysis**:
   ```bash
   python main.py https://stripe.com --mobile --summary
   ```

3. **Custom output file**:
   ```bash
   python main.py https://airbnb.com --output my_analysis.json
   ```

4. **All options**:
   ```bash
   python main.py https://example.com \
     --mobile \
     --output results.json \
     --summary \
     --no-multi-stage
   ```

## 📋 Command Line Options

```bash
python main.py <URL> [OPTIONS]

Arguments:
  URL                   Website URL to analyze

Options:
  -o, --output         Output file path (default: auto-generated)
  -m, --mobile         Include mobile view analysis
  --no-screenshot      Don't save screenshot to file
  --no-multi-stage     Use single-stage analysis (faster, less accurate)
  -s, --summary        Print analysis summary to console
  --validate-config    Validate configuration and exit
  -h, --help          Show help message
```

## 🏗️ Architecture

### Core Components

1. **`main.py`** - Command-line interface
2. **`api.py`** - Web interface (FastAPI)
3. **`vision_analyzer.py`** - GPT-4 Vision analysis engine
4. **`screenshot_service.py`** - Website screenshot capture
5. **`prompts.py`** - Advanced prompt engineering
6. **`design_schema.py`** - Design system schema definition
7. **`config.py`** - Configuration management

### Analysis Pipeline

1. **Screenshot Capture**: Uses Playwright to capture high-quality screenshots
2. **Image Optimization**: Optimizes images for API limits
3. **Multi-Stage Analysis**: 
   - Stage 1: Focused category analyses (typography, colors, layout, components)
   - Stage 2: Comprehensive synthesis
   - Stage 3: Validation and refinement
4. **JSON Output**: Structured design system data

## 📊 Design Categories Analyzed

The system extracts detailed information across 25+ design categories:

### Core Design Elements
- **Typography**: Font families, weights, sizes, line-heights, letter-spacing
- **Color & Contrast**: Brand colors, neutrals, semantic colors, gradients
- **Layout & Grid**: Content widths, breakpoints, spacing, vertical rhythm
- **Spacing & Sizing**: Base units, padding/margin scales, border radius

### UI Components
- **Buttons & CTAs**: Styles, states, dimensions, hover effects
- **Forms & Inputs**: Field styling, states, validation designs
- **Navigation**: Header design, link styles, mobile patterns
- **Cards & Containers**: Background styles, shadows, borders

### Visual Design
- **Imagery**: Style guidelines, aspect ratios, treatments
- **Icons & Illustrations**: Style, line weights, usage patterns
- **Logo Usage**: Variants, sizing, placement rules
- **Backgrounds**: Patterns, textures, gradients

### Interaction Design
- **Motion & Animation**: Easing curves, durations, directions
- **Micro-Interactions**: Button effects, transitions, loading states
- **Accessibility**: Focus indicators, contrast ratios, WCAG compliance

### Advanced Features
- **Dark Mode**: Color token swaps, adaptations
- **Data Visualization**: Chart colors, styling patterns
- **Brand & Mood**: Tone descriptors, emotional goals
- **Social Assets**: Favicon rules, Open Graph imagery

## 📖 Example Output

```json
{
  "Typography": {
    "Primary, secondary & fallback font families": [
      "\"Clash Display\", \"Inter\", -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif"
    ],
    "Weight spectrum to use": [300, 400, 600, 800, 900],
    "Heading sizes (H1-H6) with exact px/rem values": {
      "H1": "7.5rem / 120px",
      "H2": "4.5rem / 72px",
      "H3": "3rem / 48px"
    }
  },
  "Color & Contrast": {
    "Brand primaries, secondaries, accents": {
      "Primary-Indigo": "#7C5CFF",
      "Primary-Dark": "#181221",
      "Accent-Neon-Green": "#64B576"
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-4-vision-preview` | OpenAI model to use |
| `SCREENSHOT_WIDTH` | `1920` | Screenshot width in pixels |
| `SCREENSHOT_HEIGHT` | `1080` | Screenshot height in pixels |
| `SCREENSHOT_TIMEOUT` | `30000` | Page load timeout in milliseconds |

### API Configuration

The system uses GPT-4 Vision with optimized parameters:
- **Temperature**: 0.1 (for consistent results)
- **Max Tokens**: 4000 (for comprehensive analysis)
- **Image Detail**: High (for better analysis quality)

## 🌐 Web API Endpoints

### Core Endpoints

- `GET /` - Web interface
- `POST /api/analyze` - Start new analysis
- `GET /api/analysis/{id}` - Get analysis status
- `GET /api/analysis/{id}/download` - Download results
- `GET /health` - Health check

### Example API Usage

```bash
# Start analysis
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://agentops.ai", "include_mobile": true}'

# Check status
curl "http://localhost:8000/api/analysis/{analysis_id}"

# Download results
curl "http://localhost:8000/api/analysis/{analysis_id}/download" \
  -o results.json
```

## 🎯 Use Cases

### For Designers
- **Design System Documentation**: Extract comprehensive design systems
- **Competitive Analysis**: Analyze competitor design patterns
- **Design Audits**: Systematic review of existing designs
- **Style Guide Creation**: Generate detailed style guides

### For Developers
- **CSS Generation**: Extract exact specifications for implementation
- **Design Token Creation**: Generate design token libraries
- **Component Analysis**: Understand component patterns and states
- **Accessibility Audits**: Check contrast ratios and accessibility features

### For Product Teams
- **Brand Analysis**: Understand brand expression and consistency
- **User Experience Research**: Analyze interaction patterns
- **Design Trend Analysis**: Track design evolution over time
- **Quality Assurance**: Ensure design implementation accuracy

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   ```bash
   # Verify your API key
   python main.py --validate-config
   ```

2. **Screenshot Failures**:
   ```bash
   # Install Playwright browsers
   playwright install chromium
   ```

3. **Memory Issues with Large Images**:
   - The system automatically optimizes images
   - Adjust `SCREENSHOT_WIDTH` and `SCREENSHOT_HEIGHT` if needed

4. **Analysis Timeouts**:
   - Increase `SCREENSHOT_TIMEOUT` for slow websites
   - Try `--no-multi-stage` for faster analysis

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=1
python main.py https://example.com
```

## 🚀 Advanced Usage

### Batch Processing

```bash
# Process multiple URLs
for url in "https://site1.com" "https://site2.com"; do
  python main.py "$url" --output "results/$(basename "$url").json"
done
```

### Custom Prompts

Modify `prompts.py` to customize analysis focus:

```python
# Add custom category analysis
def get_custom_prompt():
    return """
    Focus on analyzing micro-interactions and animation patterns:
    - Hover states and transitions
    - Loading animations
    - Scroll-triggered effects
    """
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Design System Analysis
  run: |
    python main.py ${{ env.WEBSITE_URL }} \
      --output design-analysis.json \
      --no-screenshot
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/agentflux/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/agentflux/discussions)
- **Email**: support@your-domain.com

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision API
- Playwright team for browser automation
- FastAPI for the web framework
- The design systems community for inspiration

---

**Made with ❤️ for designers and developers who care about beautiful, systematic design.**