# Strategy Builder Quick Start Guide

## Overview
The Strategy Builder has been redesigned with a streamlined interface that supports three interchangeable strategy formats.

## Setup (LLM Integration - Optional)

To enable AI-powered strategy parsing with GPT-4:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Or add to .env file (create if doesn't exist)
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

**Note**: Without an API key, the system uses rule-based parsing (still functional but less accurate).

## Creating a Strategy - 3 Simple Steps

### Step 1: Describe Your Strategy
Navigate to **Strategy Builder** → **Define Strategy** tab.

Write your strategy in plain English or Chinese, for example:
```
Buy AAPL when the 50-day SMA crosses above the 200-day SMA and RSI is below 70.
Sell with an 8% trailing stop or 15% profit target.
Test from 2019-01-01 to 2024-12-31.
```

### Step 2: Parse with LLM
Click **"Parse Strategy"** button. The system will:
- ✅ Generate Human Readable description
- ✅ Generate JSON definition
- ✅ Generate Backtrader Python code

All three formats appear in sub-tabs below.

### Step 3: Review, Edit & Save
- Switch between the three format tabs (📖 Human Readable, ⚙️ JSON, 💻 Code)
- Edit any format directly
- Use **Validate** or **Compile** buttons to check your changes
- Enter a strategy name
- Click **💾 Save Strategy**

## The Three Strategy Formats

### 📖 Human Readable
Clear, structured plain text description:
```
Strategy: Golden Cross Strategy

Trading Universe: AAPL
Timeframe: 2019-01-01 to 2024-12-31 (1d)

Entry Conditions:
  1. SMA(50) > SMA(200)
  2. RSI(14) < 70

Exit Conditions:
  1. Trailing Stop: 8.0%
  2. Take Profit: 15.0%

Position Sizing: percent_cash at 25%
Max Positions: 1
```

**When to edit**: For documentation, sharing with non-technical users.

### ⚙️ JSON Definition
Structured data format:
```json
{
  "name": "Golden Cross Strategy",
  "universe": ["AAPL"],
  "timeframe": {
    "start": "2019-01-01",
    "end": "2024-12-31",
    "interval": "1d"
  },
  "entry": [
    {
      "type": "indicator",
      "ind": "SMA",
      "period": 50,
      "op": ">",
      "rhs": {"ind": "SMA", "period": 200}
    }
  ],
  "exit": [
    {"type": "trailing_stop", "percent": 0.08}
  ]
}
```

**When to edit**: For precise control over strategy parameters.

### 💻 Backtrader Code
Executable Python strategy:
```python
import backtrader as bt

class GeneratedStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        # Indicators pre-calculated in data feed
        
    def next(self):
        if not self.position:
            if self.data.sma_50 > self.data.sma_200:
                self.buy()
```

**When to edit**: For advanced customization, debugging, or adding custom logic.

## Working with Saved Strategies

### Viewing Saved Strategies
Go to **Saved Strategies** tab to see all your saved strategies.

Each strategy card shows:
- Strategy name and version
- Creation date
- Three format tabs for viewing/editing

### Editing Saved Strategies
1. Expand the strategy you want to edit
2. Click on the format tab (Human/JSON/Code)
3. Make your edits in the text area
4. Click **Validate** to check validity (optional)
5. Click **Update** to save changes

### Loading to Editor
To continue working on a saved strategy:
1. Find your strategy in Saved Strategies tab
2. Click **"Load to Editor"** button
3. Switch to Define Strategy tab
4. All three formats are now loaded for editing

### Deleting Strategies
Click the **Delete** button on any strategy card to remove it permanently.

## Common Workflows

### Workflow 1: Natural Language → JSON → Code
1. Write strategy description
2. Parse with LLM
3. Fine-tune JSON parameters
4. Review generated code
5. Save

### Workflow 2: Start with JSON Template
1. Go to JSON Definition tab
2. Edit the example JSON directly
3. Click "Validate JSON"
4. Click "Compile to Code" to generate Backtrader code
5. Review Human Readable (auto-generated)
6. Save

### Workflow 3: Modify Existing Strategy
1. Load saved strategy to editor
2. Edit in preferred format (Human/JSON/Code)
3. Re-validate or recompile as needed
4. Save with new name or update existing

### Workflow 4: Code-First Approach
1. Go to Backtrader Code tab
2. Write or paste Python code directly
3. Click "Validate Code"
4. Manually create JSON definition (or leave it synced)
5. Save

## Tips & Best Practices

### For Natural Language Input
- ✅ Be specific about indicators (e.g., "50-day SMA" not just "moving average")
- ✅ Mention entry AND exit conditions
- ✅ Include date ranges for testing
- ✅ Specify symbols explicitly
- ❌ Avoid vague terms like "good price" or "market conditions"

### For JSON Editing
- ✅ Use "Validate JSON" frequently to catch syntax errors
- ✅ Reference the example JSON structure
- ✅ Keep indicator names uppercase (SMA, EMA, RSI, MACD)
- ✅ Use decimals for percentages (0.08 for 8%)

### For Code Editing
- ✅ Reference pre-calculated indicators: `self.data.sma_20`, `self.data.rsi_14`
- ✅ Use "Validate Code" to check for common issues
- ✅ Don't calculate indicators manually; they're in the data feed
- ⚠️ Advanced Python knowledge required

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Switch tabs | `Tab` / `Shift+Tab` |
| Save strategy | (no shortcut, use button) |
| Validate | (no shortcut, use button) |

## Troubleshooting

### "Parse Strategy" Does Nothing
- **Cause**: Missing OPENAI_API_KEY
- **Solution**: Set API key or continue with rule-based parsing
- **Fallback**: System uses rule-based parser automatically

### JSON Validation Errors
- Check for missing commas, quotes, or brackets
- Ensure all strings are in double quotes
- Verify indicator names are uppercase
- Use online JSON validator if needed

### Code Compilation Warnings
- Usually safe to ignore minor warnings
- Red errors must be fixed before running backtest
- Check indicator references match available data

### Strategy Won't Save
- Ensure at least JSON definition is populated
- Click "Parse Strategy" or "Validate JSON" first
- Check for validation errors above save button

## Format Reference

### Supported Indicators
- `SMA` - Simple Moving Average
- `EMA` - Exponential Moving Average
- `RSI` - Relative Strength Index
- `MACD` - Moving Average Convergence Divergence
- `BBANDS` - Bollinger Bands

### Entry Condition Operators
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `==` - Equal to

### Exit Types
- `trailing_stop` - Percentage-based trailing stop
- `take_profit` - Fixed profit target
- `stop_loss` - Hard stop loss

### Position Sizing
- `percent_cash` - Percentage of available cash (e.g., 0.25 = 25%)
- `fixed` - Fixed dollar amount per trade

## Need Help?

- 📖 See `STRATEGY_BUILDER_REDESIGN.md` for technical details
- 🐛 Check error messages in the Streamlit interface
- 💬 Review example strategies in Saved Strategies tab
- 🔍 Validate frequently to catch issues early

---

**Version**: 2.0.0
**Last Updated**: October 25, 2025
