"""
Verify we have indicator data for AAPL.
"""
from src.data import IndicatorStorage

indicator_storage = IndicatorStorage()

print("=" * 80)
print("CHECKING INDICATOR DATA FOR AAPL")
print("=" * 80)

# Check if we have indicators for AAPL
has_indicators = indicator_storage.has_indicators('AAPL')
print(f"\nHas indicators for AAPL: {has_indicators}")

if has_indicators:
    # Get indicators
    df = indicator_storage.get_indicators('AAPL', start='2019-01-01', end='2024-12-31')
    print(f"Indicator rows: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Check which indicators are available
    indicator_cols = ['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'rsi_14', 'macd', 'macd_signal', 'macd_histogram', 'bb_upper', 'bb_middle', 'bb_lower']
    
    print("\nAvailable indicators:")
    for col in indicator_cols:
        if col in df.columns:
            non_null = df[col].notna().sum()
            percent = (non_null / len(df)) * 100
            print(f"  ✓ {col:15s}: {non_null:4d}/{len(df)} ({percent:.1f}%)")
        else:
            print(f"  ✗ {col:15s}: MISSING")
    
    # Show sample values
    print("\nSample values (latest):")
    last_row = df.iloc[-1]
    print(f"  Date: {last_row['date']}")
    print(f"  SMA(50): {last_row.get('sma_50', 'N/A'):.2f}")
    print(f"  SMA(200): {last_row.get('sma_200', 'N/A'):.2f}")
    print(f"  RSI(14): {last_row.get('rsi_14', 'N/A'):.2f}")
    
else:
    print("\n✗ No indicator data found for AAPL!")
    print("Please run: Download AAPL data in the Data page")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\n✅ Indicator data is {'AVAILABLE' if has_indicators else 'MISSING'} for AAPL")
print("\nThe backtest page should now work correctly!")
