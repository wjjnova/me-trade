"""
Test the actual strategy execution by enabling logging.
"""
import sys
from datetime import datetime

print("=" * 80)
print("GOLDEN CROSS STRATEGY - DETAILED EXECUTION LOG")
print("=" * 80)

from src.data import StockDataManager, IndicatorStorage
from src.strategy import StrategyCompiler
from src.backtest import BacktestEngine
from src.db import get_db

# Initialize
db = get_db()
db.initialize_schema()

# Ensure we have data
stock_mgr = StockDataManager()
results = stock_mgr.download_stocks(
    symbols=['AAPL'],
    start='2019-01-01',
    end='2024-12-31',
    interval='1d'
)

print(f"\nData available: {results['total_rows']} rows")

# Create strategy with logging enabled
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

# Modify strategy to add debug logging
debug_strategy = strategy_code.replace(
    "def next(self):",
    """def next(self):
        # Debug: Check values on known crossover dates
        date_str = self.data.datetime.date(0).isoformat()
        if date_str in ['2019-10-16', '2022-09-26', '2019-10-15', '2019-10-17', '2022-09-23', '2022-09-27']:
            print(f"DEBUG {date_str}: SMA50={self.data.sma_50[0]:.2f}, SMA200={self.data.sma_200[0]:.2f}, RSI={self.data.rsi_14[0]:.2f}, Position={self.position.size}")"""
)

# Also add logging to buy/sell
debug_strategy = debug_strategy.replace(
    "self.buy()",
    """print(f"  >>> BUYING on {self.data.datetime.date(0)}: Price=${self.data.close[0]:.2f}, SMA50={self.data.sma_50[0]:.2f}, SMA200={self.data.sma_200[0]:.2f}, RSI={self.data.rsi_14[0]:.2f}")
                self.buy()"""
)

debug_strategy = debug_strategy.replace(
    "self.sell()",
    """print(f"  <<< SELLING on {self.data.datetime.date(0)}: Price=${self.data.close[0]:.2f}, Entry=${self.buy_price:.2f}, Profit={(self.data.close[0]/self.buy_price - 1)*100:.2f}%")
                self.sell()"""
)

print("\nModified strategy with debug logging:")
print("=" * 80)
print(debug_strategy)
print("=" * 80)

print("\n\nRunning backtest with debug logging...")
print("Looking for entries around 2019-10-16 and 2022-09-26")
print("=" * 80)

engine = BacktestEngine()
result = engine.run_backtest(
    strategy_code=debug_strategy,
    universe=['AAPL'],
    start='2019-01-01',
    end='2024-12-31',
    initial_cash=100000.0,
    commission=0.001,
    slippage_bps=2.0
)

print("\n" + "=" * 80)
print("BACKTEST RESULTS")
print("=" * 80)
print(f"Success: {result['success']}")
print(f"Starting value: ${result['starting_value']:,.2f}")
print(f"Ending value: ${result['ending_value']:,.2f}")
print(f"Total return: {result['total_return']*100:.2f}%")

if 'analyzers' in result and 'trades' in result['analyzers']:
    trades = result['analyzers']['trades']
    total = trades.get('total', {}).get('total', 0)
    print(f"Total trades: {total}")

if not result['success']:
    print(f"Error: {result.get('error', 'Unknown')}")
    if 'traceback' in result:
        print("\nTraceback:")
        print(result['traceback'])
