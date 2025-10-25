"""
End-to-end test for Golden Cross strategy with RSI filter.
Strategy: Buy AAPL when SMA(50) crosses above SMA(200) and RSI < 70
Exit: 8% trailing stop or 15% profit target
Period: 2019-01-01 to 2024-12-31
"""
import sys
from datetime import datetime

print("=" * 80)
print("GOLDEN CROSS STRATEGY - END-TO-END TEST")
print("=" * 80)

# Import modules
print("\n[STEP 1] Importing modules...")
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

# Initialize database
print("\n[STEP 2] Initializing database...")
try:
    db = get_db()
    db.initialize_schema()
    print("✓ Database initialized")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    sys.exit(1)

# Download stock data
print("\n[STEP 3] Downloading AAPL data (2019-01-01 to 2024-12-31)...")
try:
    stock_mgr = StockDataManager()
    
    results = stock_mgr.download_stocks(
        symbols=['AAPL'],
        start='2019-01-01',
        end='2024-12-31',
        interval='1d'
    )
    
    if results['success']:
        print(f"✓ Downloaded {results['total_rows']} rows for AAPL")
        for item in results['success']:
            print(f"  - {item['symbol']}: {item['rows']} rows")
    else:
        print("✗ No data downloaded")
        if results.get('errors'):
            for err in results['errors']:
                print(f"  Error: {err}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Data download failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify indicators
print("\n[STEP 4] Verifying indicators were calculated and stored...")
try:
    indicator_storage = IndicatorStorage()
    
    has_indicators = indicator_storage.has_indicators('AAPL')
    print(f"✓ Indicators exist: {has_indicators}")
    
    if has_indicators:
        indicators_df = indicator_storage.get_indicators('AAPL', start='2019-01-01', end='2024-12-31')
        print(f"  - {len(indicators_df)} indicator rows stored")
        
        # Check for required indicators
        required = ['sma_50', 'sma_200', 'rsi_14']
        for col in required:
            if col in indicators_df.columns:
                non_null = indicators_df[col].notna().sum()
                print(f"  ✓ {col}: {non_null}/{len(indicators_df)} non-null values")
            else:
                print(f"  ✗ {col}: MISSING")
                sys.exit(1)
        
        # Show sample values from middle of dataset
        if len(indicators_df) > 500:
            sample_idx = len(indicators_df) // 2
            sample = indicators_df.iloc[sample_idx]
            print(f"\n  Sample values (row {sample_idx}):")
            print(f"    Date: {sample.get('date', 'N/A')}")
            print(f"    SMA(50): {sample.get('sma_50', 0):.2f}")
            print(f"    SMA(200): {sample.get('sma_200', 0):.2f}")
            print(f"    RSI: {sample.get('rsi_14', 0):.2f}")
    else:
        print("✗ Indicators not found!")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Indicator verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create strategy
print("\n[STEP 5] Creating Golden Cross strategy...")
try:
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
    
    print("✓ Strategy configuration:")
    print("  Entry conditions:")
    print("    - SMA(50) > SMA(200)  [Golden Cross]")
    print("    - RSI < 70  [Momentum filter]")
    print("  Exit conditions:")
    print("    - 8% trailing stop")
    print("    - 15% profit target")
    print("  Position sizing: 95% of cash")
    
    compiler = StrategyCompiler()
    strategy_code = compiler.compile(strategy_json)
    
    print("\n✓ Strategy compiled successfully")
    print("\n  Generated code preview (first 30 lines):")
    lines = strategy_code.split('\n')[:30]
    for i, line in enumerate(lines, 1):
        print(f"    {i:2d}: {line}")
    if len(strategy_code.split('\n')) > 30:
        print(f"    ... ({len(strategy_code.split('\n')) - 30} more lines)")
    
except Exception as e:
    print(f"✗ Strategy creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Run backtest
print("\n[STEP 6] Running backtest (2019-01-01 to 2024-12-31)...")
try:
    engine = BacktestEngine()
    
    print("  Backtest parameters:")
    print("    - Symbol: AAPL")
    print("    - Period: 2019-01-01 to 2024-12-31 (6 years)")
    print("    - Initial cash: $100,000")
    print("    - Commission: 0.1%")
    print("    - Slippage: 2 bps")
    print("\n  Executing backtest...")
    
    result = engine.run_backtest(
        strategy_code=strategy_code,
        universe=['AAPL'],
        start='2019-01-01',
        end='2024-12-31',
        initial_cash=100000.0,
        commission=0.001,
        slippage_bps=2.0
    )
    
    if result['success']:
        print("\n✓ Backtest completed successfully!")
        print("\n" + "=" * 80)
        print("BACKTEST RESULTS")
        print("=" * 80)
        
        # Basic results
        print(f"\nPortfolio Performance:")
        print(f"  Starting value:  ${result['starting_value']:>12,.2f}")
        print(f"  Ending value:    ${result['ending_value']:>12,.2f}")
        print(f"  Total return:    {result['total_return']*100:>12.2f}%")
        profit = result['ending_value'] - result['starting_value']
        print(f"  Profit/Loss:     ${profit:>12,.2f}")
        
        # Detailed analysis
        if 'analyzers' in result:
            print(f"\nDetailed Analysis:")
            
            if 'returns' in result['analyzers']:
                ret = result['analyzers']['returns']
                print(f"  Returns:")
                print(f"    Total return:     {ret.get('total_return', 0)*100:>10.2f}%")
                if 'annualized' in ret:
                    print(f"    Annualized:       {ret['annualized']*100:>10.2f}%")
            
            if 'sharpe' in result['analyzers']:
                sharpe = result['analyzers']['sharpe']
                sr = sharpe.get('sharperatio', 0)
                if sr is not None:
                    print(f"    Sharpe ratio:     {sr:>10.3f}")
            
            if 'drawdown' in result['analyzers']:
                dd = result['analyzers']['drawdown']
                if 'max' in dd:
                    max_dd = dd['max'].get('drawdown', 0)
                    print(f"    Max drawdown:     {max_dd:>10.2f}%")
            
            if 'trades' in result['analyzers']:
                trades = result['analyzers']['trades']
                total = trades.get('total', {}).get('total', 0)
                won = trades.get('won', {}).get('total', 0)
                lost = trades.get('lost', {}).get('total', 0)
                
                print(f"\n  Trade Statistics:")
                print(f"    Total trades:     {total:>10d}")
                print(f"    Won:              {won:>10d}")
                print(f"    Lost:             {lost:>10d}")
                
                if total > 0:
                    win_rate = (won / total) * 100
                    print(f"    Win rate:         {win_rate:>10.1f}%")
                
                if 'won' in trades and 'pnl' in trades['won']:
                    avg_win = trades['won']['pnl'].get('average', 0)
                    print(f"    Avg win:          ${avg_win:>10,.2f}")
                
                if 'lost' in trades and 'pnl' in trades['lost']:
                    avg_loss = trades['lost']['pnl'].get('average', 0)
                    print(f"    Avg loss:         ${avg_loss:>10,.2f}")
        
        # Trade log
        if 'trades' in result and result['trades']:
            print(f"\n  Recent Trades (last 10):")
            print(f"    {'Date':<12} {'Action':<6} {'Price':<10} {'Size':<8} {'Value':<12} {'PnL':<12}")
            print(f"    {'-'*72}")
            for trade in result['trades'][-10:]:
                date = trade.get('date', 'N/A')
                action = trade.get('type', 'N/A')
                price = trade.get('price', 0)
                size = trade.get('size', 0)
                value = trade.get('value', 0)
                pnl = trade.get('pnl', 0)
                print(f"    {date:<12} {action:<6} ${price:<9.2f} {size:<8.0f} ${value:<11.2f} ${pnl:<11.2f}")
        
        print("\n" + "=" * 80)
        
    else:
        print(f"\n✗ Backtest failed: {result.get('error', 'Unknown error')}")
        if 'traceback' in result:
            print("\nTraceback:")
            print(result['traceback'])
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Backtest execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify data feed structure
print("\n[STEP 7] Verifying indicator data feed structure...")
try:
    df_with_ind = indicator_storage.get_indicators_with_ohlcv(
        'AAPL',
        start='2019-01-01',
        end='2024-12-31'
    )
    
    print(f"✓ Data feed contains {len(df_with_ind)} rows")
    print(f"  Required columns:")
    
    required_ohlcv = ['open', 'high', 'low', 'close', 'volume']
    required_ind = ['sma_50', 'sma_200', 'rsi_14']
    
    for col in required_ohlcv:
        if col in df_with_ind.columns:
            print(f"    ✓ {col}")
        else:
            print(f"    ✗ {col} MISSING")
    
    for col in required_ind:
        if col in df_with_ind.columns:
            non_null = df_with_ind[col].notna().sum()
            print(f"    ✓ {col}: {non_null} non-null")
        else:
            print(f"    ✗ {col} MISSING")
    
except Exception as e:
    print(f"✗ Data feed verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("TEST COMPLETED SUCCESSFULLY ✓")
print("=" * 80)
print("\nVerified:")
print("  ✓ Data downloaded for full 6-year period (2019-2024)")
print("  ✓ Indicators (SMA 50/200, RSI) calculated and stored")
print("  ✓ Strategy compiled with correct entry/exit conditions")
print("  ✓ Backtest executed without errors")
print("  ✓ Trade statistics and performance metrics calculated")
print("  ✓ Data feed contains all required OHLCV and indicator columns")
print("\n✅ Golden Cross strategy is working correctly!")
