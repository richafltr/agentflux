# Quality Check Feature Documentation

## Overview

The Enhanced AgentFlux now includes an automated quality check feature that uses GPT-4o to analyze generated A/B test variation images for visual inconsistencies and problems. If issues are detected, the system automatically regenerates the images with improvements.

## How It Works

### 1. Initial Image Generation
- DALL-E generates A/B test variations based on the original screenshot and modification prompts
- Each variation represents a different design pattern (Hero-First, Feature-Grid, etc.)

### 2. Quality Check Phase
After each image is generated, the system:
- Feeds the generated image to GPT-4o for quality analysis
- Checks for common issues:
  - Text overflow or clipping
  - Bad margins or spacing
  - Font problems (size, contrast)
  - Low contrast between elements
  - Misaligned components
  - Overlapping content
  - Broken layouts
  - Blurry or pixelated areas
  - Inconsistent styling

### 3. Automatic Improvement
If quality issues are found:
- The system extracts specific fix instructions from GPT-4o's feedback
- Regenerates the image with an enhanced prompt that includes:
  - Original modification instructions
  - Specific fixes for identified issues
  - General quality guidelines
- The improved image replaces the original

## Benefits

- **Consistent Quality**: Ensures all generated variations meet quality standards
- **Automatic Fixes**: No manual intervention needed for common issues
- **Detailed Feedback**: Each issue is documented with severity and fix instructions
- **Improved UX**: Better visual consistency for A/B testing

## Output

The quality check results are included in:
- The analysis summary JSON
- Console output during generation
- Individual variation metadata

## Example Quality Check Output

```json
{
  "has_issues": true,
  "issues": [
    {
      "type": "text_contrast",
      "description": "Hero text has low contrast against background",
      "severity": "high",
      "fix": "Increase text color contrast to meet WCAG AA standards"
    },
    {
      "type": "spacing",
      "description": "Insufficient margin between navigation and hero section",
      "severity": "medium",
      "fix": "Add 40-60px vertical spacing between navigation and hero"
    }
  ],
  "overall_quality": "fair",
  "regeneration_needed": true
}
```

## Testing the Feature

Run the test script to see the quality check in action:

```bash
python test_quality_check.py
```

This will analyze an existing variation image and show the quality assessment results.

## Integration

The quality check is seamlessly integrated into the main workflow:
1. No additional configuration required
2. Automatically runs for all generated variations
3. Adds minimal processing time
4. Results are included in the final analysis package 