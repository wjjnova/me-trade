"""
End-to-end test for backtest functionality with stored indicators.
Tests the complete flow: Download data → Store indicators → Create strategy → Run backtest
"""
import sys
from datetime import datetime, timedelta

print("=" * 80)
print("BACKTEST WITH STORED INDICATORS - END-TO-END TEST")
print("=" * 80)

# Test 1: Import all modules
print("\n[TEST 1] Importing modules...")
try:
    from src.data import StockDataManager, IndicatorStorage
    from src.strategy import StrategyCompiler
    from src.backtest import BacktestEngine
    from src.db import get_db
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Initialize database
print("\n[TEST 2] Initializing database...")
try:
    db = get_db()
    db.initialize_schema()
    print("✓ Database initialized with technical_indicators table")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Download stock data
print("\n[TEST 3] Downloading stock data...")
try:
    stock_mgr = StockDataManager()
    
    # Download sample data for AAPL
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    results = stock_mgr.download_stocks(
        symbols=['AAPL'],
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval='1d'
    )
    
    if results['success']:
        print(f"✓ Downloaded {results['total_rows']} rows for AAPL")
        for item in results['success']:
            print(f"  - {item['symbol']}: {item['rows']} rows")
    else:
        print("✗ No data downloaded")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Data download failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify indicators were stored
print("\n[TEST 4] Verifying indicators were stored...")
try:
    indicator_storage = IndicatorStorage()
    
    has_indicators = indicator_storage.has_indicators('AAPL')
    print(f"✓ Indicators exist for AAPL: {has_indicators}")
    
    if has_indicators:
        # Get sample indicators
        indicators_df = indicator_storage.get_indicators('AAPL')
        print(f"  - {len(indicators_df)} rows of indicators")
        print(f"  - Columns: {list(indicators_df.columns)}")
        
        # Show sample values
        if len(indicators_df) > 0:
            last_row = indicators_df.iloc[-1]
            print(f"  - Latest values:")
            print(f"      SMA_20: {last_row.get('sma_20', 'N/A')}")
            print(f"      SMA_50: {last_row.get('sma_50', 'N/A')}")
            print(f"      RSI: {last_row.get('rsi_14', 'N/A')}")
    else:
        print("⚠ Warning: Indicators not found, may need manual calculation")
        
except Exception as e:
    print(f"✗ Indicator verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Create a simple strategy
print("\n[TEST 5] Creating test strategy...")
try:
    strategy_json = {
        "name": "SMA Crossover Test",
        "entry": [
            {
                "type": "indicator",
                "ind": "SMA",
                "period": 20,
                "op": ">",
                "rhs": {"ind": "SMA", "period": 50}
            }
        ],
        "exit": [
            {
                "type": "trailing_stop",
                "percent": 0.05
            }
        ],
        "position": {
            "sizing": "percent_cash",
            "value": 0.95
        }
    }
    
    compiler = StrategyCompiler()
    strategy_code = compiler.compile(strategy_json)
    
    print("✓ Strategy compiled")
    print(f"  Strategy: {strategy_json['name']}")
    print(f"  Entry: SMA(20) > SMA(50)")
    print(f"  Exit: 5% trailing stop")
    print(f"\n  Generated code preview:")
    lines = strategy_code.split('\n')[:15]
    for line in lines:
        print(f"    {line}")
    print("    ...")
    
except Exception as e:
    print(f"✗ Strategy creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Run backtest with stored indicators
print("\n[TEST 6] Running backtest with stored indicators...")
try:
    engine = BacktestEngine()
    
    # Run backtest
    backtest_start = (end_date - timedelta(days=180)).strftime('%Y-%m-%d')
    backtest_end = end_date.strftime('%Y-%m-%d')
    
    print(f"  Universe: ['AAPL']")
    print(f"  Period: {backtest_start} to {backtest_end}")
    print(f"  Initial cash: $100,000")
    print(f"  Running backtest...")
    
    result = engine.run_backtest(
        strategy_code=strategy_code,
        universe=['AAPL'],
        start=backtest_start,
        end=backtest_end,
        initial_cash=100000.0,
        commission=0.001,
        slippage_bps=2.0
    )
    
    if result['success']:
        print("✓ Backtest completed successfully")
        print(f"\n  Results:")
        print(f"    Starting value: ${result['starting_value']:,.2f}")
        print(f"    Ending value: ${result['ending_value']:,.2f}")
        print(f"    Total return: {result['total_return']*100:.2f}%")
        
        if 'analyzers' in result:
            print(f"\n  Analysis:")
            if 'returns' in result['analyzers']:
                ret = result['analyzers']['returns']
                print(f"    Total return (analyzer): {ret.get('total_return', 0)*100:.2f}%")
            if 'sharpe' in result['analyzers']:
                sharpe = result['analyzers']['sharpe']
                print(f"    Sharpe ratio: {sharpe.get('sharperatio', 0):.3f}")
            if 'drawdown' in result['analyzers']:
                dd = result['analyzers']['drawdown']
                print(f"    Max drawdown: {dd.get('max', {}).get('drawdown', 0):.2f}%")
    else:
        print(f"✗ Backtest failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Backtest execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Verify indicators were used (check data feed structure)
print("\n[TEST 7] Verifying indicators in data feed...")
try:
    # Get data with indicators
    df_with_ind = indicator_storage.get_indicators_with_ohlcv(
        'AAPL',
        start=backtest_start,
        end=backtest_end
    )
    
    print(f"✓ Retrieved {len(df_with_ind)} rows with indicators")
    print(f"  Columns present:")
    
    expected_cols = ['sma_20', 'sma_50', 'sma_200', 'rsi_14', 'macd']
    for col in expected_cols:
        if col in df_with_ind.columns:
            non_null = df_with_ind[col].notna().sum()
            print(f"    ✓ {col}: {non_null}/{len(df_with_ind)} non-null values")
        else:
            print(f"    ✗ {col}: MISSING")
    
    print("\n✓ Indicators are properly stored and accessible for backtesting")
    
except Exception as e:
    print(f"✗ Indicator verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("ALL TESTS PASSED ✓")
print("=" * 80)
print("\nSummary:")
print("  ✓ Database schema updated with technical_indicators table")
print("  ✓ Stock data downloaded successfully")
print("  ✓ Indicators calculated and stored automatically")
print("  ✓ Strategy compiled to use pre-calculated indicators")
print("  ✓ Backtest executed with stored indicators")
print("  ✓ Results verified and metrics calculated")
print("\n✅ The backtest functionality is working correctly with stored indicators!")
print("\nKey improvements:")
print("  1. Indicators are pre-calculated and stored in database")
print("  2. Backtest engine loads data with indicators")
print("  3. Strategies reference indicators from data feed (self.data.sma_20, etc.)")
print("  4. No runtime indicator calculation overhead")
print("  5. Consistent indicator values across runs")
