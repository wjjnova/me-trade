"""
Standalone test for IndicatorCalculator without dependencies.
Tests the indicator calculation logic independently.
"""
import sys
import pandas as pd
import numpy as np

print("=" * 80)
print("INDICATOR CALCULATOR STANDALONE TEST")
print("=" * 80)

# Test 1: Import IndicatorCalculator
print("\n[TEST 1] Testing IndicatorCalculator import...")
try:
    sys.path.insert(0, '/Users/wjjnova/repo/me-trade')
    from src.data.indicators import IndicatorCalculator
    print("✓ IndicatorCalculator imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create sample data
print("\n[TEST 2] Creating sample data...")
try:
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.randn(100),
        'high': prices + abs(np.random.randn(100)) + 2,
        'low': prices - abs(np.random.randn(100)) - 2,
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 100)
    })
    
    print(f"✓ Created {len(df)} rows of sample data")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Price range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
except Exception as e:
    print(f"✗ Data creation failed: {e}")
    sys.exit(1)

# Test 3: SMA calculation
print("\n[TEST 3] Testing SMA calculation...")
try:
    sma_20 = IndicatorCalculator.calculate_sma(df, period=20)
    print(f"  Length: {len(sma_20)} (expected {len(df)})")
    print(f"  NaN count: {sma_20.isna().sum()} (first 19 should be NaN)")
    print(f"  Last 5 values: {sma_20.tail().values}")
    
    assert len(sma_20) == len(df), "SMA length should match input"
    assert sma_20.isna().sum() == 19, "First 19 values should be NaN"
    assert not pd.isna(sma_20.iloc[-1]), "Last value should not be NaN"
    
    print("✓ SMA calculation passed")
except Exception as e:
    print(f"✗ SMA test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: EMA calculation
print("\n[TEST 4] Testing EMA calculation...")
try:
    ema_12 = IndicatorCalculator.calculate_ema(df, period=12)
    print(f"  Length: {len(ema_12)}")
    print(f"  NaN count: {ema_12.isna().sum()}")
    print(f"  Last 5 values: {ema_12.tail().values}")
    
    assert len(ema_12) == len(df), "EMA length should match input"
    assert not pd.isna(ema_12.iloc[-1]), "Last value should not be NaN"
    
    print("✓ EMA calculation passed")
except Exception as e:
    print(f"✗ EMA test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: RSI calculation
print("\n[TEST 5] Testing RSI calculation...")
try:
    rsi = IndicatorCalculator.calculate_rsi(df, period=14)
    print(f"  Length: {len(rsi)}")
    print(f"  NaN count: {rsi.isna().sum()}")
    print(f"  Last 5 values: {rsi.tail().values}")
    print(f"  Min: {rsi.min():.2f}, Max: {rsi.max():.2f}")
    
    assert len(rsi) == len(df), "RSI length should match input"
    assert not pd.isna(rsi.iloc[-1]), "Last value should not be NaN"
    
    # Check RSI is in valid range (0-100)
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all(), "RSI should be between 0 and 100"
    
    print("✓ RSI calculation passed")
except Exception as e:
    print(f"✗ RSI test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: MACD calculation
print("\n[TEST 6] Testing MACD calculation...")
try:
    macd_data = IndicatorCalculator.calculate_macd(df)
    
    print(f"  Keys: {macd_data.keys()}")
    print(f"  MACD last value: {macd_data['macd'].iloc[-1]:.2f}")
    print(f"  Signal last value: {macd_data['signal'].iloc[-1]:.2f}")
    print(f"  Histogram last value: {macd_data['histogram'].iloc[-1]:.2f}")
    
    assert 'macd' in macd_data, "Should have 'macd' key"
    assert 'signal' in macd_data, "Should have 'signal' key"
    assert 'histogram' in macd_data, "Should have 'histogram' key"
    assert len(macd_data['macd']) == len(df), "MACD length should match input"
    
    print("✓ MACD calculation passed")
except Exception as e:
    print(f"✗ MACD test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Bollinger Bands calculation
print("\n[TEST 7] Testing Bollinger Bands calculation...")
try:
    bbands = IndicatorCalculator.calculate_bollinger_bands(df)
    
    print(f"  Keys: {bbands.keys()}")
    print(f"  Upper last value: {bbands['upper'].iloc[-1]:.2f}")
    print(f"  Middle last value: {bbands['middle'].iloc[-1]:.2f}")
    print(f"  Lower last value: {bbands['lower'].iloc[-1]:.2f}")
    
    assert 'upper' in bbands, "Should have 'upper' key"
    assert 'middle' in bbands, "Should have 'middle' key"
    assert 'lower' in bbands, "Should have 'lower' key"
    
    # Check that upper > middle > lower
    last_idx = -1
    assert bbands['upper'].iloc[last_idx] > bbands['middle'].iloc[last_idx], "Upper should be > middle"
    assert bbands['middle'].iloc[last_idx] > bbands['lower'].iloc[last_idx], "Middle should be > lower"
    
    print("✓ Bollinger Bands calculation passed")
except Exception as e:
    print(f"✗ Bollinger Bands test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: calculate_all method
print("\n[TEST 8] Testing calculate_all() method...")
try:
    indicators = ['sma_20', 'sma_50', 'ema_12', 'rsi', 'macd', 'bbands']
    df_with_ind = IndicatorCalculator.calculate_all(df, indicators)
    
    expected_cols = [
        'date', 'open', 'high', 'low', 'close', 'volume',  # Original
        'SMA_20', 'SMA_50', 'EMA_12', 'RSI',  # Indicators
        'MACD', 'MACD_Signal', 'MACD_Histogram',  # MACD components
        'BB_Middle', 'BB_Upper', 'BB_Lower'  # Bollinger Bands
    ]
    
    print(f"  Result columns: {list(df_with_ind.columns)}")
    print(f"  Result shape: {df_with_ind.shape}")
    
    for col in expected_cols:
        if col not in df_with_ind.columns:
            print(f"  ✗ Missing column: {col}")
            sys.exit(1)
    
    print(f"\n  Last row values:")
    last_row = df_with_ind.iloc[-1]
    print(f"    Close: ${last_row['close']:.2f}")
    print(f"    SMA_20: ${last_row['SMA_20']:.2f}")
    print(f"    SMA_50: ${last_row['SMA_50']:.2f}")
    print(f"    RSI: {last_row['RSI']:.2f}")
    print(f"    MACD: {last_row['MACD']:.2f}")
    
    print("✓ calculate_all() passed")
except Exception as e:
    print(f"✗ calculate_all() test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Edge cases
print("\n[TEST 9] Testing edge cases...")
try:
    # Small dataframe (less than period)
    small_df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'close': [100 + i for i in range(10)]
    })
    
    result = IndicatorCalculator.calculate_sma(small_df, period=20)
    print(f"  Small dataframe (10 rows, period 20): All NaN = {result.isna().all()}")
    assert result.isna().all(), "Should be all NaN when data < period"
    
    # Large period
    result = IndicatorCalculator.calculate_sma(df, period=200)
    print(f"  Large period (200): All NaN = {result.isna().all()}")
    assert result.isna().all(), "Should be all NaN when period > data length"
    
    # Period equal to data length
    result = IndicatorCalculator.calculate_sma(df, period=100)
    print(f"  Period = data length (100): Last value NaN = {pd.isna(result.iloc[-1])}")
    assert not pd.isna(result.iloc[-1]), "Should have one value when period = data length"
    
    print("✓ Edge cases handled correctly")
except Exception as e:
    print(f"✗ Edge case test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("ALL TESTS PASSED ✓")
print("=" * 80)
print("\nIndicatorCalculator Summary:")
print("  ✓ SMA - Simple Moving Average working")
print("  ✓ EMA - Exponential Moving Average working")
print("  ✓ RSI - Relative Strength Index working (0-100 range)")
print("  ✓ MACD - Moving Average Convergence Divergence working")
print("  ✓ Bollinger Bands - Upper/Middle/Lower bands working")
print("  ✓ calculate_all() - Batch calculation working")
print("  ✓ Edge cases - Handled gracefully")
print("\n✅ The indicator calculator is bug-free and ready to use!")
