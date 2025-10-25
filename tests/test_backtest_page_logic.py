"""
Test that simulates what the backtest page does to check for missing data.
"""
from src.data import StockDataManager
from src.db import get_db
import json

print("=" * 80)
print("SIMULATING BACKTEST PAGE DATA CHECK")
print("=" * 80)

# Initialize
stock_mgr = StockDataManager()
db = get_db()

# Load the strategy (same as backtest page does)
strategy = db.fetchone("SELECT id, name, json FROM strategies ORDER BY created_at DESC LIMIT 1")

if strategy:
    print(f"\nStrategy: {strategy['name']}")
    print(f"ID: {strategy['id']}")
    
    # Parse JSON
    strategy_data = json.loads(strategy['json'])
    universe = strategy_data.get('universe', ['AAPL'])
    
    print(f"\nUniverse from strategy JSON: {universe}")
    
    # Check available symbols (exactly what the backtest page does)
    available_symbols = stock_mgr.get_available_symbols()
    print(f"\nAvailable symbols in database: {available_symbols}")
    
    # Check for missing symbols (same logic as backtest page)
    missing_symbols = [s for s in universe if s not in available_symbols]
    
    print(f"\nMissing symbols: {missing_symbols if missing_symbols else 'None'}")
    
    if missing_symbols:
        print(f"\n✗ WOULD SHOW WARNING: Missing data for: {', '.join(missing_symbols)}")
    else:
        print(f"\n✅ ALL SYMBOLS HAVE DATA - NO WARNING WILL BE SHOWN")
        print("\nThe backtest page will now work correctly!")
else:
    print("\n✗ No strategy found in database")

print("\n" + "=" * 80)
