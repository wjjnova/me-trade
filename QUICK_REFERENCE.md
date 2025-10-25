# 🎯 Me-Trade: Quick Reference

## 🚀 One-Command Start

```bash
chmod +x start.sh && ./start.sh
```

## 📊 4-Step Workflow

```
┌─────────────┐
│   1. DATA   │  Download AAPL, MSFT, etc. from Yahoo Finance
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 2. STRATEGY │  "Buy when SMA50 > SMA200, sell with 8% stop"
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 3. BACKTEST │  Run 2019-2024, $100k initial, vs VOO benchmark
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 4. RESULTS  │  View return: +45%, Sharpe: 1.2, Max DD: -18%
└─────────────┘
```

## 🗂️ Project Map

```
me-trade/
│
├── 🏠 app.py                    ← START HERE (streamlit run app.py)
├── ⚙️  config.py                ← Settings
├── 📦 requirements.txt         ← Dependencies
├── 📖 README.md                ← Full docs
├── 🧪 example.py               ← Test script
├── ✅ test_basic.py            ← Unit tests
│
├── 📂 pages/                   ← Streamlit UI
│   ├── 1_Data.py              ← Download data
│   ├── 2_Strategy_Builder.py  ← Create strategies
│   ├── 3_Backtest.py          ← Run backtests
│   └── 4_Results.py           ← View results
│
└── 📂 src/                     ← Core logic
    ├── db/                    ← SQLite (auto-creates)
    ├── data/                  ← Stock/option downloaders
    ├── models/                ← Pydantic schemas
    ├── strategy/              ← NL parser + compiler
    ├── backtest/              ← Backtrader engine
    └── visualization/         ← Plotly charts
```

## 🎨 UI Pages

| Page | Purpose | Key Features |
|------|---------|-------------|
| **Home** | Welcome | Quick stats, navigation |
| **Data** | Download market data | Stocks, options, benchmarks |
| **Strategy Builder** | Create strategies | NL input → JSON → Code |
| **Backtest** | Run tests | Configure & execute |
| **Results** | Analyze | Metrics, charts, export |

## 📈 Example Strategy

### Input (Natural Language)
```
Buy AAPL when 50-day SMA crosses above 200-day SMA and RSI < 70.
Sell with 8% trailing stop or 15% profit target.
Test from 2019 to 2024 with $100k initial capital.
```

### Output (Structured JSON)
```json
{
  "name": "Golden Cross with RSI",
  "universe": ["AAPL"],
  "timeframe": {"start": "2019-01-01", "end": "2024-12-31"},
  "entry": [
    {"type": "indicator", "ind": "SMA", "period": 50, "op": ">", 
     "rhs": {"ind": "SMA", "period": 200}},
    {"type": "indicator", "ind": "RSI", "period": 14, "op": "<", "rhs": 70}
  ],
  "exit": [
    {"type": "trailing_stop", "percent": 0.08},
    {"type": "take_profit", "percent": 0.15}
  ]
}
```

### Result
```
✓ Total Return: +45.2%
✓ Sharpe Ratio: 1.32
✓ Max Drawdown: -18.5%
✓ Outperformance vs VOO: +8.7%
```

## 🔧 Common Commands

```bash
# Install
pip install -r requirements.txt

# Run app
streamlit run app.py

# Run example
python example.py

# Run tests
pytest test_basic.py -v

# Reset database
rm data/metrade.db
```

## 📊 Supported Indicators

- **Trend**: SMA, EMA
- **Momentum**: RSI, MACD
- **Volatility**: Bollinger Bands, ATR (future)
- **Custom**: Upload CSV with your own signals

## 🎯 Performance Metrics

| Metric | Description |
|--------|-------------|
| Total Return | (End - Start) / Start |
| CAGR | Annualized compound growth |
| Max Drawdown | Largest peak-to-trough decline |
| Sharpe Ratio | Risk-adjusted return |
| Sortino Ratio | Downside risk-adjusted |
| Calmar Ratio | Return / Max Drawdown |
| Excess Return | Strategy - Benchmark |

## 🔐 Safety Features

- ✅ AST code validation (no dangerous imports)
- ✅ No filesystem access
- ✅ No network access in strategies
- ✅ Runtime timeout limits
- ✅ SQLite injection protection

## 🌟 Pro Tips

1. **Download data first** - App won't run backtests without cached data
2. **Start simple** - Test with 1 symbol before expanding universe
3. **Use benchmarks** - Always compare to VOO/SPY for context
4. **Check date ranges** - Ensure data coverage matches backtest period
5. **Save strategies** - Reuse and iterate on successful patterns

## 📞 Need Help?

1. Read `README.md` for detailed docs
2. Run `python example.py` to see working demo
3. Check `IMPLEMENTATION_SUMMARY.md` for technical details
4. Open an issue on GitHub

## 🎉 Quick Win

```bash
# 1. Start app
streamlit run app.py

# 2. Go to Data page → Download "AAPL" (2020-2024)

# 3. Go to Strategy Builder → Use example strategy → Save

# 4. Go to Backtest → Select strategy → Run

# 5. Go to Results → View performance!

Total time: ~3 minutes 🚀
```

## 📚 Learn More

- **Backtrader Docs**: https://www.backtrader.com/
- **yfinance**: https://pypi.org/project/yfinance/
- **Streamlit**: https://streamlit.io/

---

**Built with ❤️ for algorithmic traders**
