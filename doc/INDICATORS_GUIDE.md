# Technical Indicators Guide

## Overview

Me Trade now includes a powerful indicator visualization tool that allows you to view stock price data with commonly used technical indicators calculated in real-time.

## Available Indicators

### Moving Averages
- **SMA 20** - Simple Moving Average (20 days)
- **SMA 50** - Simple Moving Average (50 days)
- **SMA 200** - Simple Moving Average (200 days)
- **EMA 12** - Exponential Moving Average (12 days)

### Momentum Indicators
- **RSI** - Relative Strength Index (14 days)
  - Shows overbought (>70) and oversold (<30) levels
  
### Volatility Indicators
- **Bollinger Bands** - 20-day SMA with 2 standard deviation bands
  - Upper band, Middle band (SMA 20), Lower band

### Trend Indicators
- **MACD** - Moving Average Convergence Divergence
  - MACD Line (12 EMA - 26 EMA)
  - Signal Line (9 EMA of MACD)
  - Histogram (MACD - Signal)

## How to Use

### Step 1: Access the Indicator View
1. Open the Me Trade application
2. Navigate to **Data Management** page (1_Data)
3. Click on the **"View Indicators"** tab

### Step 2: Select Your Stock
1. Choose a symbol from the dropdown (only shows stocks with cached data)
2. Set your date range for analysis
3. Check the indicators you want to display

### Step 3: Load and Analyze
1. Click **"Load Data"** button
2. View the interactive chart with:
   - Price chart with overlaid moving averages and Bollinger Bands
   - RSI subplot (if selected)
   - MACD subplot (if selected)
3. Scroll through the data table below the chart
4. Download the data with indicators as CSV

## Interactive Features

### Chart Interactions
- **Zoom**: Click and drag on the chart
- **Pan**: Hold shift and drag
- **Hover**: See exact values for all indicators at any point
- **Legend**: Click items to show/hide
- **Reset**: Double-click to reset zoom

### Data Export
The CSV export includes:
- All OHLCV data
- All calculated indicator values
- Properly formatted for further analysis

## Indicator Formulas

### SMA (Simple Moving Average)
```
SMA = Sum(Close prices over n periods) / n
```

### EMA (Exponential Moving Average)
```
EMA today = (Close today × k) + (EMA yesterday × (1 - k))
where k = 2 / (n + 1)
```

### RSI (Relative Strength Index)
```
RS = Average Gain / Average Loss (over 14 periods)
RSI = 100 - (100 / (1 + RS))
```
- RSI > 70: Potentially overbought
- RSI < 30: Potentially oversold

### MACD
```
MACD Line = 12 EMA - 26 EMA
Signal Line = 9 EMA of MACD Line
Histogram = MACD Line - Signal Line
```
- Bullish signal: MACD crosses above Signal
- Bearish signal: MACD crosses below Signal

### Bollinger Bands
```
Middle Band = 20-day SMA
Upper Band = Middle Band + (2 × Standard Deviation)
Lower Band = Middle Band - (2 × Standard Deviation)
```
- Price at upper band: Potentially overbought
- Price at lower band: Potentially oversold
- Bands squeeze: Low volatility (potential breakout)
- Bands widen: High volatility

## Tips for Analysis

### Trend Following
1. Use **SMA 50** and **SMA 200** for long-term trends
   - Price above both = Strong uptrend
   - Price below both = Strong downtrend
   - "Golden Cross": SMA 50 crosses above SMA 200 (bullish)
   - "Death Cross": SMA 50 crosses below SMA 200 (bearish)

### Mean Reversion
1. Use **Bollinger Bands** to identify extreme moves
2. Use **RSI** to confirm overbought/oversold conditions
3. Look for price reversals when both indicators align

### Momentum Trading
1. Use **MACD** for trend changes
2. Use **EMA 12** for short-term momentum
3. Combine with **RSI** to avoid false signals

### Multi-Indicator Confirmation
Combine multiple indicators for stronger signals:
- **Bullish Setup**: Price > SMA 50, RSI > 50, MACD > Signal
- **Bearish Setup**: Price < SMA 50, RSI < 50, MACD < Signal

## Common Patterns

### Divergence
When price and RSI/MACD move in opposite directions:
- **Bullish Divergence**: Price makes lower lows, but RSI makes higher lows
- **Bearish Divergence**: Price makes higher highs, but RSI makes lower highs

### Support and Resistance
- Moving averages often act as dynamic support/resistance
- Bollinger Bands can identify breakout levels

## Integration with Backtesting

The same indicators you view here can be used in your backtesting strategies:

1. Analyze indicators visually first
2. Identify patterns and levels
3. Create a strategy using those insights
4. Backtest with the Strategy Builder

## Performance Notes

- Indicators are calculated on-demand (not stored)
- Calculation is fast even for large datasets
- First 20-200 data points may have NaN for indicators (warm-up period)
- Use at least 200 days of data for best results with SMA 200

## Next Steps

After analyzing indicators:
1. Note successful patterns
2. Create a strategy in the Strategy Builder
3. Backtest your strategy
4. Compare results with benchmarks

## Examples

### Example 1: Trend Following Strategy
```
Observation: AAPL price stays above SMA 50 during uptrends
Strategy: Buy when close > SMA 50, Sell when close < SMA 50
```

### Example 2: RSI Mean Reversion
```
Observation: MSFT often bounces when RSI < 30
Strategy: Buy when RSI < 30, Sell when RSI > 70
```

### Example 3: MACD Crossover
```
Observation: TSLA trends well after MACD crosses signal
Strategy: Buy when MACD crosses above signal, Sell when crosses below
```

## Troubleshooting

**Problem**: No symbols available
- **Solution**: Download stock data first in the "Stocks" tab

**Problem**: Indicators show NaN values
- **Solution**: Need more historical data (at least 200 days for SMA 200)

**Problem**: Chart is too crowded
- **Solution**: Select fewer indicators or zoom into a specific date range

**Problem**: Slow performance
- **Solution**: Reduce date range or number of indicators displayed

## API Reference

The `IndicatorCalculator` class is available for programmatic use:

```python
from src.data.indicators import IndicatorCalculator
import pandas as pd

# Calculate individual indicators
sma = IndicatorCalculator.calculate_sma(df, period=20)
rsi = IndicatorCalculator.calculate_rsi(df, period=14)
macd_data = IndicatorCalculator.calculate_macd(df)
bbands = IndicatorCalculator.calculate_bollinger_bands(df)

# Calculate multiple at once
df_with_indicators = IndicatorCalculator.calculate_all(
    df, 
    indicators=['sma_20', 'sma_50', 'rsi', 'macd']
)
```

## Further Reading

- **Moving Averages**: Used for trend identification
- **RSI**: Developed by J. Welles Wilder
- **MACD**: Developed by Gerald Appel
- **Bollinger Bands**: Developed by John Bollinger

Happy trading! 📈
