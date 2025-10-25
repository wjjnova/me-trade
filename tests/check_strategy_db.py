"""
Check what's stored in the strategy database.
"""
from src.db import get_db
import json

db = get_db()

# Get all strategies
strategies = db.fetchall("SELECT id, name, json FROM strategies ORDER BY created_at DESC")

print("=" * 80)
print("STRATEGIES IN DATABASE")
print("=" * 80)

for strat in strategies:
    print(f"\nStrategy: {strat['name']} (ID: {strat['id']})")
    print("-" * 80)
    
    # Parse JSON
    data = json.loads(strat['json'])
    
    # Show universe
    universe = data.get('universe', [])
    print(f"Universe: {universe}")
    
    # Show entry conditions
    if 'entry' in data:
        print(f"Entry conditions: {len(data['entry'])} conditions")
        for i, cond in enumerate(data['entry'], 1):
            print(f"  {i}. {cond}")
    
    # Show exit conditions
    if 'exit' in data:
        print(f"Exit conditions: {len(data['exit'])} conditions")
        for i, cond in enumerate(data['exit'], 1):
            print(f"  {i}. {cond}")
    
    print()

print("=" * 80)
print("\nPROBLEM: The 'universe' field should only contain stock symbols like ['AAPL']")
print("It should NOT contain indicator names like 'SMA', 'SMA', 'RSI'")
print("\nThese indicator names are coming from the entry conditions and getting")
print("incorrectly added to the universe during strategy creation.")
