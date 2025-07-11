# 📁 AgentFlux Project Structure

## 🎯 Overview
AgentFlux has been reorganized for clarity and maintainability. All generated artifacts are now centralized in the `outputs/` directory.

## 📂 Directory Structure

```
agentflux/
├── outputs/                    # All generated artifacts
│   ├── analyses/              # JSON analysis files
│   ├── screenshots/           # Website screenshots
│   ├── components/            # Generated React components
│   ├── variations/            # A/B test variation images
│   ├── stylized/              # Stylized variations
│   └── ab_tests/              # A/B test packages
│
├── *.py                       # Source code files
├── requirements.txt           # Python dependencies
├── README.md                  # Main documentation
└── env.template              # Environment template
```

## 📦 Output Organization

### `outputs/analyses/`
- Component analysis JSON files
- A/B test packages
- Summary reports

### `outputs/screenshots/`
- Original website screenshots
- Segmented component images

### `outputs/components/`
- Generated React/TSX components
- Component variations

### `outputs/variations/`
- A/B test variation images generated by DALL-E

### `outputs/stylized/`
- Style preset variations
- Style gallery HTML

### `outputs/ab_tests/`
- Complete A/B test packages with variations

## 🚀 Usage

When running the enhanced analysis:
```bash
python main_enhanced.py https://example.com
```

All outputs will be automatically organized in the `outputs/` directory.

## 🧹 Cleanup
The old scattered directories (`enhanced_analysis/`, `fresh_analysis/`, `screenshots/`, `variations/`) have been consolidated into the new structure. 