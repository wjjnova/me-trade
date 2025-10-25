# Me Trade

**Natural Language-Driven Backtesting and Analysis App Using Backtrader**

A lightweight application for testing trading strategies using U.S. stock and option historical data. Describe strategies in natural language, and the system converts them into structured strategies and executable Backtrader Python code.

---

## 📋 Overview

**Me Trade** enables you to:

- 📝 Describe trading strategies in plain English or Chinese
- 📊 Download and cache stock/option data from Yahoo Finance
- 🧪 Backtest strategies using Backtrader
- 📈 Compare performance against market benchmarks (VOO, SPY, QQQ)
- 💾 Store all data and results in a local SQLite database

### In-Scope Symbols (Initial Focus)

`MSFT, PATH, GOOGL, TSLA, COST, NVDA, META, NFLX, AMZN, VOO, AAPL, BABA`

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd me-trade
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Dolt and download the options dataset** *(recommended for options backtesting)*:
  ```bash
  brew install dolt
  cd data
  dolt clone post-no-preference/options
  cd options
  dolt dump -r csv
  ```

  Verify your installation with a sample query:
  ```bash
  dolt sql -q "SELECT * FROM option_chain WHERE act_symbol = 'TSLA' LIMIT 3"
  ```

  Sample output:
  ```text
  +------------+------------+------------+--------+----------+--------+--------+--------+---------+--------+---------+--------+---------+
  | date       | act_symbol | expiration | strike | call_put | bid    | ask    | vol    | delta   | gamma  | theta   | vega   | rho     |
  +------------+------------+------------+--------+----------+--------+--------+--------+---------+--------+---------+--------+---------+
  | 2021-01-01 | TSLA       | 2021-01-15 | 495.00 | Call     | 210.80 | 211.90 | 0.8359 | 0.9853  | 0.0003 | -0.1498 | 0.0532 | 0.1987  |
  | 2021-01-01 | TSLA       | 2021-01-15 | 495.00 | Put      | 1.02   | 1.08   | 0.8990 | -0.0208 | 0.0004 | -0.2145 | 0.0715 | -0.0065 |
  | 2021-01-01 | TSLA       | 2021-01-15 | 510.00 | Call     | 196.00 | 197.15 | 0.8098 | 0.9804  | 0.0004 | -0.1857 | 0.0682 | 0.2034  |
  +------------+------------+------------+--------+----------+--------+--------+--------+---------+--------+---------+--------+---------+
  ```

### Running the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 🎯 Core Features

### 1. **Data Sourcing**

**Stocks:**
- Primary: Yahoo Finance via `yfinance`
- Daily and intraday data (where available)
- Automatic caching to SQLite
- Support for custom CSV uploads
- **NEW: Technical indicator visualization** - View stocks with SMA, EMA, RSI, MACD, Bollinger Bands

**Options:**
- Current option chains from Yahoo Finance
- Calls/puts with strikes, expirations, Greeks
- Snapshot caching for quasi-historical data

**Benchmarks:**
- VOO (S&P 500)
- SPY (S&P 500)
- QQQ (Nasdaq 100)

### 2. **Natural Language Strategy Builder**

Describe strategies in plain language:

```
Buy AAPL when the 50-day SMA crosses above the 200-day SMA and RSI is below 70.
Sell with an 8% trailing stop or 15% profit target.
Test from 2019-01-01 to 2024-12-31.
```

The app converts this to structured JSON and generates executable Backtrader code.

### 3. **Structured Strategy Format**

Strategies are represented as JSON:

```json
{
  "name": "SMA Cross with RSI Filter",
  "universe": ["AAPL", "MSFT"],
  "timeframe": {
    "start": "2019-01-01",
    "end": "2024-12-31",
    "interval": "1d"
  },
  "entry": [
    {
      "type": "indicator",
      "ind": "SMA",
      "period": 50,
      "op": ">",
      "rhs": {"ind": "SMA", "period": 200}
    }
  ],
  "exit": [
    {"type": "trailing_stop", "percent": 0.08},
    {"type": "take_profit", "percent": 0.15}
  ],
  "position": {
    "sizing": "percent_cash",
    "value": 0.25,
    "max_positions": 4
  },
  "costs": {
    "commission_per_share": 0.005,
    "slippage_bps": 5
  }
}
```

### 4. **Backtesting Engine**

- Powered by **Backtrader**
- Configurable commission and slippage
- Multi-symbol support
- Position sizing strategies
- Standard analyzers (Returns, Sharpe, Drawdown, Trades)

### 5. **Performance Metrics**

- Total Return
- CAGR (Compound Annual Growth Rate)
- Maximum Drawdown
- Sharpe Ratio
- Sortino Ratio (calculated from returns)
- Calmar Ratio
- Excess Return vs. Benchmark

### 6. **Visualization**

- Equity curves
- Drawdown charts
- Returns distribution
- Monthly returns heatmap
- Benchmark comparison charts

---

## 📁 Project Structure

```
me-trade/
├── app.py                      # Main Streamlit app
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── data/                       # SQLite database storage
│   └── metrade.db
├── files/                      # Exported artifacts (CSV, JSON)
├── pages/                      # Streamlit multi-page app
│   ├── 1_Data.py              # Data management page
│   ├── 2_Strategy_Builder.py  # Strategy creation page
│   ├── 3_Backtest.py          # Backtest execution page
│   └── 4_Results.py           # Results visualization page
└── src/                       # Core modules
    ├── db/                    # Database layer
    │   ├── __init__.py
    │   └── schema.py          # SQLite schema and operations
    ├── data/                  # Data sourcing
    │   ├── __init__.py
    │   ├── stocks.py          # Stock data manager
    │   ├── options.py         # Options data manager
    │   └── benchmarks.py      # Benchmark data manager
    ├── models/                # Pydantic models
    │   ├── __init__.py
    │   └── strategy.py        # Strategy, Backtest models
    ├── strategy/              # Strategy processing
    │   ├── __init__.py
    │   ├── nl_parser.py       # Natural language parser
    │   ├── compiler.py        # Code generator
    │   └── validator.py       # Code safety validator
    ├── backtest/              # Backtesting engine
    │   ├── __init__.py
    │   ├── engine.py          # Backtrader execution
    │   └── metrics.py         # Performance calculations
    └── visualization/         # Charts and plots
        ├── __init__.py
        └── charts.py          # Plotly chart generators
```

---

## 💾 Database Schema

The app uses **SQLite** with the following tables:

### `equities_ohlcv`
Stores stock OHLCV data with date, symbol, interval, and source information.

### `options_chain`
Stores option chain snapshots with strikes, expirations, bid/ask, volume, OI.

### `strategies`
Stores strategy definitions as JSON with versioning.

### `codes`
Stores generated Backtrader code linked to strategies.

### `backtests`
Stores backtest execution records with configuration and status.

### `metrics_run`
Stores calculated performance metrics for each backtest.

---

## 🛠️ Usage Guide

### Step 1: Download Data

1. Navigate to **Data** page
2. Enter symbols (comma-separated): `AAPL, MSFT, GOOGL`
3. Select date range and interval
4. Click **Download Stock Data**
5. Optionally download benchmarks (VOO, SPY, QQQ)

**NEW: View Indicators**
- Switch to **View Indicators** tab
- Select a symbol and date range
- Choose indicators (SMA, RSI, MACD, etc.)
- Click **Load Data** to see interactive charts
- Download data with indicators as CSV
- See [INDICATORS_GUIDE.md](INDICATORS_GUIDE.md) for detailed usage

### Step 2: Create Strategy

1. Navigate to **Strategy Builder** page
2. **Option A**: Describe strategy in natural language
   - Enter description in text area
   - Click **Parse Strategy**
   - Review and edit generated JSON
3. **Option B**: Write structured JSON directly
4. Click **Compile to Code** to generate Backtrader code
5. Click **Save Strategy** to persist to database

### Step 3: Run Backtest

1. Navigate to **Backtest** page
2. Select a saved strategy
3. Configure:
   - Trading universe (symbols)
   - Date range
   - Initial capital
   - Commission and slippage
   - Benchmarks for comparison
4. Click **Run Backtest**
5. View summary results

### Step 4: Analyze Results

1. Navigate to **Results** page
2. Select a completed backtest
3. View:
   - Performance metrics
   - Benchmark comparison
   - Strategy configuration
   - Export options (JSON, CSV)

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Database path
DB_PATH = "data/metrade.db"

# Default symbols
DEFAULT_SYMBOLS = ["MSFT", "AAPL", "GOOGL", ...]

# Benchmark symbols
BENCHMARK_SYMBOLS = ["VOO", "SPY", "QQQ"]

# Backtest defaults
DEFAULT_INITIAL_CASH = 100000.0
DEFAULT_COMMISSION = 0.005  # per share
DEFAULT_SLIPPAGE_BPS = 5  # basis points

# Execution limits
MAX_BACKTEST_RUNTIME = 300  # seconds
```

---

## 🧪 Development

### Adding New Indicators

Edit `src/strategy/compiler.py` to add new indicator support:

```python
elif ind_name == 'ATR':
    var_name = f"atr_{period}"
    code_lines.append(
        f"self.{var_name} = bt.indicators.ATR(period={period})"
    )
```

### Adding New Data Sources

Create a new adapter in `src/data/`:

```python
class NewDataSource:
    def download(self, symbols, start, end):
        # Implementation
        pass
```

### Future Enhancements

- [ ] LLM integration for NL parsing (OpenAI/Anthropic)
- [ ] Real-time equity curve tracking
- [ ] Multi-leg options strategies
- [ ] Portfolio rebalancing rules
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] FastAPI REST endpoints

---

## 📊 Example Strategies

### 1. **SMA Crossover**

```
Buy when 50-day SMA crosses above 200-day SMA.
Sell when 50-day SMA crosses below 200-day SMA.
```

### 2. **RSI Mean Reversion**

```
Buy when RSI drops below 30.
Sell when RSI rises above 70 or after 5 days.
```

### 3. **Bollinger Band Breakout**

```
Buy when price closes above upper Bollinger Band.
Sell with 10% stop loss or when price closes below middle band.
```

---

## 🔒 Safety & Security

- **Code Validation**: AST inspection prevents filesystem/network access
- **Sandboxed Execution**: No dangerous imports or builtins allowed
- **Runtime Limits**: Configurable timeout for backtest execution
- **Local-Only**: All data stored locally in SQLite

---

## 📝 CSV Upload Format

To upload custom data, use this CSV format:

```csv
date,open,high,low,close,volume
2024-01-01,150.00,155.00,149.00,154.50,1000000
2024-01-02,154.50,158.00,153.00,157.00,1200000
```

Optional column: `adj_close`

---

## 🐛 Troubleshooting

### Data Download Fails

- Check internet connection
- Verify symbol is valid on Yahoo Finance
- Try shorter date range
- Check Yahoo Finance API status

### Backtest Fails

- Ensure data is downloaded for all symbols in universe
- Verify date range has sufficient data
- Check strategy JSON is valid
- Review generated code for errors

### Database Issues

- Delete `data/metrade.db` to reset
- App will recreate schema on next run

---

## 📚 Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[INDICATORS_GUIDE.md](INDICATORS_GUIDE.md)** - Technical indicators visualization guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick start visual guide

---

## 📦 Dependencies

- **streamlit** - Web UI framework
- **backtrader** - Backtesting engine
- **yfinance** - Yahoo Finance data
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **pydantic** - Data validation
- **plotly** - Interactive charts
- **fastapi** - Optional API (future)

---

## 🤝 Contributing

This is an MVP/prototype. Contributions welcome!

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Submit pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Backtrader** - Excellent backtesting framework
- **yfinance** - Convenient Yahoo Finance API wrapper
- **Streamlit** - Rapid prototyping UI framework

---

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Happy Trading! 📈**
