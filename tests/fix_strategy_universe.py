"""
Fix the existing strategy in the database to remove indicator names from universe.
"""
from src.db import get_db
import json

db = get_db()

print("=" * 80)
print("FIXING STRATEGY DATABASE")
print("=" * 80)

# Get all strategies
strategies = db.fetchall("SELECT id, name, json FROM strategies")

for strat in strategies:
    strategy_id = strat['id']
    strategy_name = strat['name']
    data = json.loads(strat['json'])
    
    # Get current universe
    old_universe = data.get('universe', [])
    print(f"\nStrategy: {strategy_name}")
    print(f"  Old universe: {old_universe}")
    
    # Filter out indicator names
    indicator_names = {'SMA', 'EMA', 'RSI', 'MACD', 'BB', 'ATR', 'ADX', 'CCI', 'ROC', 'OBV', 'VWAP'}
    new_universe = [s for s in old_universe if s not in indicator_names]
    
    # Ensure at least one symbol
    if not new_universe:
        new_universe = ['AAPL']
    
    print(f"  New universe: {new_universe}")
    
    # Update the data
    data['universe'] = new_universe
    
    # Save back to database
    db.execute(
        "UPDATE strategies SET json = ? WHERE id = ?",
        (json.dumps(data), strategy_id)
    )
    
    print(f"  ✓ Updated!")

print("\n" + "=" * 80)
print("ALL STRATEGIES FIXED")
print("=" * 80)
