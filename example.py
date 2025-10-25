"""
Example: End-to-End Strategy Creation and Backtesting
This script demonstrates the complete workflow programmatically.
"""
from src.data import StockDataManager, BenchmarkManager
from src.strategy import NLParser, StrategyCompiler, CodeValidator
from src.backtest import BacktestEngine, MetricsCalculator
from src.db import get_db
import json
from datetime import datetime
import uuid


def main():
    """Run end-to-end example."""
    
    print("=" * 60)
    print("Me-Trade: End-to-End Example")
    print("=" * 60)
    
    # Initialize components
    stock_mgr = StockDataManager()
    benchmark_mgr = BenchmarkManager()
    parser = NLParser()
    compiler = StrategyCompiler()
    validator = CodeValidator()
    engine = BacktestEngine()
    metrics_calc = MetricsCalculator()
    db = get_db()
    
    # Step 1: Download Data
    print("\n📊 Step 1: Downloading data...")
    print("-" * 60)
    
    symbols = ["AAPL"]
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    print(f"Downloading {symbols} from {start_date} to {end_date}...")
    
    results = stock_mgr.download_stocks(
        symbols=symbols,
        start=start_date,
        end=end_date,
        interval="1d"
    )
    
    if results["success"]:
        print(f"✓ Downloaded {results['total_rows']} rows")
    else:
        print("✗ Download failed!")
        return
    
    # Download benchmark
    print("\nDownloading VOO benchmark...")
    bench_results = benchmark_mgr.download_benchmarks(
        start=start_date,
        end=end_date,
        benchmarks=["VOO"]
    )
    
    if bench_results["success"]:
        print(f"✓ Downloaded benchmark data")
    
    # Step 2: Create Strategy
    print("\n📝 Step 2: Creating strategy...")
    print("-" * 60)
    
    nl_description = """
    Buy AAPL when the 50-day SMA crosses above the 200-day SMA.
    Sell with an 8% trailing stop or 15% profit target.
    """
    
    print("Natural language input:")
    print(nl_description)
    
    strategy_dict = parser.parse(nl_description, symbols=symbols)
    strategy_dict["timeframe"]["start"] = start_date
    strategy_dict["timeframe"]["end"] = end_date
    
    print("\n✓ Strategy parsed:")
    print(json.dumps(strategy_dict, indent=2))
    
    # Step 3: Compile Strategy
    print("\n⚙️  Step 3: Compiling strategy to code...")
    print("-" * 60)
    
    code = compiler.compile(strategy_dict)
    
    print("✓ Code generated:")
    print("\n" + code[:500] + "\n...(truncated)")
    
    # Validate code
    is_valid, violations = validator.validate_backtrader_strategy(code)
    
    if is_valid:
        print("\n✓ Code validation passed")
    else:
        print("\n✗ Code validation failed:")
        for v in violations:
            print(f"  - {v}")
        return
    
    # Step 4: Save Strategy
    print("\n💾 Step 4: Saving strategy...")
    print("-" * 60)
    
    strategy_id = f"strat_{uuid.uuid4().hex[:8]}"
    code_id = f"code_{uuid.uuid4().hex[:8]}"
    
    db.execute(
        """INSERT INTO strategies (id, name, version, json, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (strategy_id, strategy_dict["name"], 1, 
         json.dumps(strategy_dict), datetime.now().isoformat())
    )
    
    db.execute(
        """INSERT INTO codes (id, strategy_id, language, code, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (code_id, strategy_id, 'python', code, datetime.now().isoformat())
    )
    
    print(f"✓ Strategy saved with ID: {strategy_id}")
    
    # Step 5: Run Backtest
    print("\n🚀 Step 5: Running backtest...")
    print("-" * 60)
    
    backtest_results = engine.run_backtest(
        strategy_code=code,
        universe=symbols,
        start=start_date,
        end=end_date,
        initial_cash=100000.0,
        commission=0.005,
        slippage_bps=5.0
    )
    
    if not backtest_results["success"]:
        print(f"✗ Backtest failed: {backtest_results.get('error')}")
        return
    
    print("✓ Backtest completed")
    
    # Step 6: Display Results
    print("\n📈 Step 6: Results")
    print("-" * 60)
    
    print(f"\nStarting Value:  ${backtest_results['starting_value']:,.2f}")
    print(f"Ending Value:    ${backtest_results['ending_value']:,.2f}")
    print(f"Total Return:    {backtest_results['total_return'] * 100:.2f}%")
    
    analyzers = backtest_results.get('analyzers', {})
    
    if 'sharpe' in analyzers:
        sharpe = analyzers['sharpe'].get('sharpe_ratio', 0)
        print(f"Sharpe Ratio:    {sharpe:.3f}")
    
    if 'drawdown' in analyzers:
        max_dd = analyzers['drawdown'].get('max_drawdown_pct', 0)
        print(f"Max Drawdown:    {max_dd:.2f}%")
    
    if 'trades' in analyzers:
        trades = analyzers['trades']
        total = trades.get('total_trades', 0)
        won = trades.get('won_trades', 0)
        lost = trades.get('lost_trades', 0)
        print(f"\nTotal Trades:    {total}")
        print(f"Won:             {won}")
        print(f"Lost:            {lost}")
        if total > 0:
            win_rate = (won / total) * 100
            print(f"Win Rate:        {win_rate:.1f}%")
    
    # Compare to benchmark
    print("\n🎯 Benchmark Comparison")
    print("-" * 60)
    
    bench_data = stock_mgr.get_cached_data("VOO", start_date, end_date)
    
    if not bench_data.empty:
        bench_start = bench_data['close'].iloc[0]
        bench_end = bench_data['close'].iloc[-1]
        bench_return = (bench_end - bench_start) / bench_start
        
        print(f"VOO Return:      {bench_return * 100:.2f}%")
        print(f"Outperformance:  {(backtest_results['total_return'] - bench_return) * 100:.2f}%")
    
    print("\n" + "=" * 60)
    print("✓ Example completed successfully!")
    print("=" * 60)
    print("\nYou can now run 'streamlit run app.py' to use the web interface.")


if __name__ == "__main__":
    main()
