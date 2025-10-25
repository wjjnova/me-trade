## Fixed: "Missing data for: SMA, SMA, RSI" Issue

### Problem
The backtest page was showing a warning: **"Missing data for: SMA, SMA, RSI"** even though we have all the required indicator data for AAPL.

### Root Cause
The natural language parser (`src/strategy/nl_parser.py`) was incorrectly extracting indicator names as stock symbols when parsing the strategy text:
- Input: "Buy AAPL when the 50-day SMA crosses above the 200-day SMA and RSI is below 70"
- Bug: The `_extract_symbols()` method used regex `r'\b([A-Z]{1,5})\b'` to find all uppercase words
- Result: Extracted `['AAPL', 'SMA', 'SMA', 'RSI']` as the "universe" (trading symbols)
- Impact: Backtest page checked if symbols "SMA", "SMA", and "RSI" had stock data → failed → showed warning

### Solution

#### 1. Fixed the Parser (`src/strategy/nl_parser.py`)
**Before:**
```python
# Filter out common words
common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH'}
symbols = [s for s in matches if s not in common_words]
```

**After:**
```python
# Filter out common words and indicator names
common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH'}
indicator_names = {'SMA', 'EMA', 'RSI', 'MACD', 'BB', 'ATR', 'ADX', 'CCI', 'ROC', 'OBV', 'VWAP'}
excluded = common_words | indicator_names
symbols = [s for s in matches if s not in excluded]
```

#### 2. Fixed Existing Database Records
Created and ran `fix_strategy_universe.py` to clean up the existing strategy:
- **Before**: `universe: ['AAPL', 'SMA', 'SMA', 'RSI']`
- **After**: `universe: ['AAPL']`

### Verification

✅ **Parser Fix Verified**
- Indicator names (SMA, EMA, RSI, MACD, etc.) are now excluded from symbol extraction
- Future strategies will have clean universe fields with only actual stock symbols

✅ **Database Fix Verified**
- Existing strategy now has correct universe: `['AAPL']`
- No indicator names in the universe field

✅ **Data Availability Verified**
- AAPL has 1,510 rows of indicator data (2019-01-02 to 2024-12-31)
- All required indicators available:
  - SMA(50): 1,461 rows (96.8%)
  - SMA(200): 1,311 rows (86.8%)
  - RSI(14): 1,497 rows (99.1%)

✅ **Backtest Page Logic Verified**
- Simulated the backtest page's data check
- No missing symbols detected
- Warning message will no longer appear

### Result
The backtest page now correctly:
1. Shows only actual stock symbols in the universe field
2. Validates data availability for those symbols (not indicator names)
3. Finds all required OHLCV and indicator data for AAPL
4. **No warning message displayed** ✅

The issue is completely resolved!
