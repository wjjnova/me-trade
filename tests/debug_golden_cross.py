"""
Debug script to investigate why Golden Cross strategy generated 0 trades.
"""
import pandas as pd
from src.data import IndicatorStorage

print("=" * 80)
print("DEBUGGING GOLDEN CROSS STRATEGY - WHY NO TRADES?")
print("=" * 80)

indicator_storage = IndicatorStorage()

# Get data with indicators
print("\n[1] Loading AAPL data with indicators...")
df = indicator_storage.get_indicators_with_ohlcv('AAPL', start='2019-01-01', end='2024-12-31')
print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Check for NaN values
print("\n[2] Checking for NaN values in key indicators...")
print(f"SMA(50) NaN count: {df['sma_50'].isna().sum()} / {len(df)}")
print(f"SMA(200) NaN count: {df['sma_200'].isna().sum()} / {len(df)}")
print(f"RSI NaN count: {df['rsi_14'].isna().sum()} / {len(df)}")

# Drop rows where we can't evaluate conditions
df_clean = df.dropna(subset=['sma_50', 'sma_200', 'rsi_14'])
print(f"\nRows with all indicators available: {len(df_clean)}")

# Check entry conditions
print("\n[3] Checking entry conditions...")
print("    Entry: SMA(50) > SMA(200) AND RSI < 70")

# Condition 1: SMA(50) > SMA(200)
df_clean['sma_cross'] = df_clean['sma_50'] > df_clean['sma_200']
crosses = df_clean['sma_cross'].sum()
print(f"\n  SMA(50) > SMA(200): {crosses} / {len(df_clean)} days ({crosses/len(df_clean)*100:.1f}%)")

# Condition 2: RSI < 70
df_clean['rsi_ok'] = df_clean['rsi_14'] < 70
rsi_ok = df_clean['rsi_ok'].sum()
print(f"  RSI < 70: {rsi_ok} / {len(df_clean)} days ({rsi_ok/len(df_clean)*100:.1f}%)")

# Both conditions
df_clean['entry_signal'] = df_clean['sma_cross'] & df_clean['rsi_ok']
entry_signals = df_clean['entry_signal'].sum()
print(f"  BOTH conditions met: {entry_signals} / {len(df_clean)} days ({entry_signals/len(df_clean)*100:.1f}%)")

# Show sample days where conditions are met
if entry_signals > 0:
    print("\n[4] Sample days where entry conditions are met:")
    entry_days = df_clean[df_clean['entry_signal']]
    print(f"\nFirst 10 entry signals:")
    print(entry_days[['date', 'close', 'sma_50', 'sma_200', 'rsi_14']].head(10).to_string(index=False))
    
    print(f"\nLast 10 entry signals:")
    print(entry_days[['date', 'close', 'sma_50', 'sma_200', 'rsi_14']].tail(10).to_string(index=False))
else:
    print("\n[4] No days found where entry conditions are met!")

# Analyze the SMA crossover pattern
print("\n[5] Analyzing SMA crossover events...")
df_clean['prev_sma_50'] = df_clean['sma_50'].shift(1)
df_clean['prev_sma_200'] = df_clean['sma_200'].shift(1)
df_clean['prev_cross'] = df_clean['prev_sma_50'] > df_clean['prev_sma_200']

# Detect crossover (was below, now above)
df_clean['golden_cross'] = (~df_clean['prev_cross']) & df_clean['sma_cross']
golden_crosses = df_clean[df_clean['golden_cross']]

print(f"Golden Cross events (50 crosses above 200): {len(golden_crosses)}")
if len(golden_crosses) > 0:
    print("\nGolden Cross dates:")
    for idx, row in golden_crosses.iterrows():
        print(f"  {row['date']}: Close=${row['close']:.2f}, SMA50={row['sma_50']:.2f}, SMA200={row['sma_200']:.2f}, RSI={row['rsi_14']:.2f}")
        
        # Check if RSI was < 70 at crossover
        if row['rsi_14'] < 70:
            print(f"    ✓ RSI < 70 - ENTRY SIGNAL!")
        else:
            print(f"    ✗ RSI >= 70 - No entry")

# Check strategy logic in generated code
print("\n[6] Checking if strategy logic matches our analysis...")
print("\nThe strategy should check:")
print("  1. self.data.sma_50[0] > self.data.sma_200[0]")
print("  2. self.data.rsi_14[0] < 70")
print("\nLet me check the generated strategy code...")

from src.strategy import StrategyCompiler

strategy_json = {
    "name": "Golden Cross with RSI Filter",
    "entry": [
        {
            "type": "indicator",
            "ind": "SMA",
            "period": 50,
            "op": ">",
            "rhs": {"ind": "SMA", "period": 200}
        },
        {
            "type": "indicator",
            "ind": "RSI",
            "period": 14,
            "op": "<",
            "rhs": 70
        }
    ],
    "exit": [
        {
            "type": "trailing_stop",
            "percent": 0.08
        },
        {
            "type": "profit_target",
            "percent": 0.15
        }
    ],
    "position": {
        "sizing": "percent_cash",
        "value": 0.95
    }
}

compiler = StrategyCompiler()
strategy_code = compiler.compile(strategy_json)

# Extract the next() method
lines = strategy_code.split('\n')
in_next = False
next_method = []
for line in lines:
    if 'def next(self)' in line:
        in_next = True
    if in_next:
        next_method.append(line)
        if line.strip() and not line.strip().startswith('#') and in_next and line.strip().startswith('def ') and 'def next' not in line:
            break

print("\nGenerated next() method:")
print('\n'.join(next_method[:40]))

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
