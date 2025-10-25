# Vibe Coding: Me‑Trade

---

## **Project Overview**

**Title:** Natural‑Language‑Driven Backtesting and Analysis App Using Backtrader

**Objective:** Develop a simple, lightweight application to **test trading strategies** using **U.S. stock and option historical data**. Users describe strategies in **natural language (NL)**, and the system converts them into a **structured strategy description** for confirmation. Once approved, the structured strategy is compiled into **Backtrader‑compatible Python code** and executed for backtesting. The app stores datasets and results in a lightweight **SQLite database**.

**In‑Scope Symbols (Initial Focus):** `MSFT, PATH (UiPath), GOOGL, TSLA, COST, NVDA, META, NFLX, AMZN, VOO, AAPL, BABA`

---

## **Core Features**

### 1. **Data Sourcing (Stocks)**

- Integrate with **free and public providers** (primary: `yfinance`/Yahoo Finance; alternatives: **Stooq**, **Alpha Vantage**).
- Default coverage includes the symbols listed above.
- Allow users to select **time ranges**, **granularity** (daily or intraday, if supported), and **adjusted/unadjusted prices**.
- Use a **local cache** (SQLite + filesystem) to avoid redundant API calls.
- Enable users to **add more tickers** or **upload custom CSVs** following the documented schema.

### 2. **Data Sourcing (Options)**

- Retrieve **option chain data** (calls/puts, strikes, expirations, Greeks when available) from free sources.
- Candidate data sources:
  - **Yahoo Finance options API** (`yfinance`, unofficial but convenient).
  - **OCC (Options Clearing Corporation)** public summaries.
  - **Nasdaq Data Link** free datasets (select coverage).
- Provide a modular **Option Data Adapter** interface for easy integration of new sources.
- Store normalized option data (symbol, date, expiration, strike, type, bid/ask/last, volume, OI) locally.

### 3. **Natural Language → Structured Strategy → Code Workflow**

1. **Capture:** User describes a trading strategy in English or Chinese.
2. **LLM Parsing:** The app converts NL text into a **structured JSON** strategy for review and fine‑tuning.
3. **Compilation:** After confirmation, the structured JSON becomes executable **Backtrader code**.
4. **Execution:** Backtrader runs the strategy for a given **time window** and **stock universe**, saving results.
5. **Safety:** Sandboxed execution—AST inspection, no file/network access, enforced runtime limits.

**Example Structured Strategy Schema (MVP)**

```json
{
  "name": "SMA Cross with RSI Filter",
  "universe": ["AAPL", "MSFT"],
  "timeframe": {"start": "2019-01-01", "end": "2024-12-31", "interval": "1d"},
  "entry": [
    {"type": "indicator", "ind": "SMA", "period": 50, "op": ">", "rhs": {"ind": "SMA", "period": 200}},
    {"type": "indicator", "ind": "RSI", "period": 14, "op": "<", "rhs": 60}
  ],
  "exit": [
    {"type": "trailing_stop", "percent": 0.08},
    {"type": "take_profit", "percent": 0.2}
  ],
  "position": {"sizing": "percent_cash", "value": 0.25, "max_positions": 4},
  "costs": {"commission_per_share": 0.005, "slippage_bps": 5}
}
```

This schema is intentionally compact and human‑readable. It can be extended for multi‑leg options, hedging, or rebalancing.

### 4. **Backtesting Engine**

- Use **Backtrader** to execute strategies across a defined time window and stock universe.
- Configure key parameters: initial capital, position sizing, commission/slippage, and benchmarks.
- Support multiple symbols (multi‑asset) and multi‑timeframe expansion later.
- Persist structured strategy JSON, generated code, and run results in **SQLite**.

### 5. **Metrics, Benchmarks, and Outperformance**

- Compute standard **technical indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, volatility, drawdown.
- Implement basic **options analytics**: theoretical price and Greeks via Black‑Scholes.
- Compare strategy results with **VOO/SPY (S&P 500)** and **QQQ (Nasdaq 100)** benchmarks.
- Display cumulative return, CAGR, max drawdown, Sharpe ratio, and **excess return** (strategy − benchmark).

### 6. **Visualization & Reporting**

- Show interactive charts for equity curves, buy/sell signals, drawdown, and volatility.
- Provide tables of trades, performance metrics, and benchmark comparisons.
- Support exports: **CSV**, **JSON**, or **HTML** summary reports.

### 7. **Web UI (Streamlit‑Based)**

- Lightweight **Streamlit** interface for all functionality:
  - Dashboard, Data, Strategy Builder, Backtests, Reports.
- Host on a single server (Docker or bare‑metal) and access via browser.

### 8. **Backend (Python)**

- Core backend written in Python 3.11+, using **FastAPI** (optional) or native Streamlit actions.
- Store data and results in **SQLite**.
- No external dependencies beyond standard open‑source libraries.

---

## **Database Schema (SQLite)**

The schema defines tables for equities, options, strategies, code, backtests, and performance metrics. Each table uses pragmatic indexing for efficient queries.

(DDL content retained from the draft; ready to execute on startup.)

---

## **Minimal Streamlit App (MVP)**

A single‑page Streamlit app that lets users:

1. Download stock data via `yfinance`.
2. Write a natural‑language strategy description.
3. Confirm the generated structured JSON.
4. Compile and view Backtrader code.
5. Run backtests and view equity results versus benchmarks.

A simple directory structure and installation guide ensure ease of setup and iteration.

---

## **How to Run**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run once to create the SQLite schema, then start the app.

---

## **Next Development Steps**

1. Add full SQLite write‑back for strategies, code, backtests, and metrics.
2. Include automatic benchmark downloading (VOO/SPY/QQQ).
3. Replace the rule‑based `propose_structure()` stub with an LLM call.
4. Enhance the compiler to generate dynamic indicators from the structured JSON.
5. Implement CSV upload and option‑chain visualization pages.

---

## **Success Metrics**

- Backtesting runs complete under 30 seconds for a single stock (5‑year daily window).
- Users can test strategies entirely in natural language.
- Results clearly show profit/loss and comparison to major benchmarks.
- The system remains lightweight, transparent, and easy to modify.

---

## **Finalized Spec (Code-Friendly)**

### A) Finalized Free Data Sources

- **Stocks (historical OHLCV):**
  - Primary: **Yahoo Finance** via `yfinance` (free, unofficial; daily & some intraday).
  - Secondary: **Stooq** (daily); fallback for resilience.
- **Options (chains; free, limited history):**
  - Primary: **Yahoo Finance options** via `yfinance` (current chains; cache snapshots for quasi-history).
  - Supplement: **OCC** daily summaries (parse to enrich OI/volume; no quotes history).
- **Benchmarks:**
  - **VOO** (S&P 500), **SPY** (S&P 500), **QQQ** (Nasdaq 100) via `yfinance`.

> Policy: Use free sources for initial/backfill. Support **on‑demand** fetch for additional ranges/symbols via the same adapters.

---

### B) Finalized Technical Framework & Libraries (Simple First)

- **Language:** Python 3.11+
- **UI:** **Streamlit** (single‑server, simple state, fast iteration)
- **Backtesting:** **Backtrader** (vanilla analyzers + small custom analyzers)
- **Data/ETL:** `pandas`, `yfinance`; simple OCC parser (local file ingest)
- **Math/Utils:** `numpy`, built‑in `datetime`
- **Charts:** Streamlit native + `plotly`/`matplotlib`
- **Schema/Validation:** `pydantic` (models) + JSON Schema export
- **Storage:** **SQLite** (`sqlite3`), files on disk (CSV/Parquet, /files artifacts)
- **Optional API (later):** **FastAPI** with `uvicorn` (kept minimal)

---

### C) Finalized Data Schema

> Storage is SQLite. JSON payloads use compact, tool‑friendly keys.

**Tables (SQLite DDL – authoritative)**

```sql
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS equities_ohlcv (
  symbol TEXT NOT NULL,
  date TEXT NOT NULL,
  interval TEXT NOT NULL,
  open REAL, high REAL, low REAL, close REAL,
  adj_close REAL, volume INTEGER,
  source TEXT, asof TEXT,
  PRIMARY KEY (symbol, date, interval)
);
CREATE INDEX IF NOT EXISTS idx_equities_symbol_date ON equities_ohlcv(symbol, date);

CREATE TABLE IF NOT EXISTS options_chain (
  symbol TEXT NOT NULL,
  trade_date TEXT NOT NULL,
  expiration TEXT NOT NULL,
  right TEXT NOT NULL,
  strike REAL NOT NULL,
  bid REAL, ask REAL, last REAL, mid REAL,
  volume INTEGER, open_interest INTEGER,
  implied_vol REAL, underlying_price REAL,
  source TEXT, asof TEXT,
  PRIMARY KEY (symbol, trade_date, expiration, right, strike)
);
CREATE INDEX IF NOT EXISTS idx_options_symbol_trade ON options_chain(symbol, trade_date);

CREATE TABLE IF NOT EXISTS strategies (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version INTEGER NOT NULL,
  json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS codes (
  id TEXT PRIMARY KEY,
  strategy_id TEXT NOT NULL,
  language TEXT NOT NULL,
  code TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(strategy_id) REFERENCES strategies(id)
);

CREATE TABLE IF NOT EXISTS backtests (
  id TEXT PRIMARY KEY,
  strategy_id TEXT NOT NULL,
  code_id TEXT NOT NULL,
  universe TEXT NOT NULL,
  start TEXT NOT NULL,
  end TEXT NOT NULL,
  initial_cash REAL NOT NULL,
  benchmarks TEXT,
  status TEXT NOT NULL,
  artifacts TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(strategy_id) REFERENCES strategies(id),
  FOREIGN KEY(code_id) REFERENCES codes(id)
);

CREATE TABLE IF NOT EXISTS metrics_run (
  bt_id TEXT PRIMARY KEY,
  tot_return REAL, cagr REAL, max_dd REAL,
  sharpe REAL, sortino REAL, calmar REAL,
  excess_return REAL,
  benchmarks TEXT,
  FOREIGN KEY(bt_id) REFERENCES backtests(id)
);
```

**JSON: Structured Strategy (authoritative schema)**

```json
{
  "name": "<string>",
  "universe": ["AAPL"],
  "timeframe": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "interval": "1d|1h|15m|5m"},
  "entry": [ {"type": "indicator", "ind": "SMA|EMA|RSI|MACD|BBANDS", "period": <int>, "op": ">|<|>=|<=|==", "rhs": <number|indicator> } ],
  "exit":  [ {"type": "trailing_stop", "percent": <float>} , {"type": "take_profit", "percent": <float>} ],
  "position": {"sizing": "percent_cash|fixed", "value": <float>, "max_positions": <int>},
  "costs": {"commission_per_share": <float>, "slippage_bps": <float>},
  "options": null
}
```

**JSON: Backtest Request (minimal)**

```json
{
  "strategy_id": "strat_001",
  "code_id": "code_001",
  "universe": ["AAPL","MSFT"],
  "start": "2019-01-01",
  "end": "2024-12-31",
  "initial_cash": 100000,
  "benchmarks": ["VOO"]
}
```

**JSON: Backtest Result (summary)**

```json
{
  "id": "bt_7f3e2b",
  "performance": {"tot_return": 0.96, "cagr": 0.18, "max_dd": -0.22, "sharpe": 1.32, "excess_return": 0.22},
  "benchmarks": {"VOO": {"tot_return": 0.74, "cagr": 0.14}},
  "artifacts": {"equity_csv": "/files/bt_7f3e2b_equity.csv"}
}
```

---

### D) Finalized Minimal API Contract (FastAPI, optional)

**OpenAPI 3.1 (YAML)**

```yaml
openapi: 3.1.0
info:
  title: Me-Trade API (MVP)
  version: 0.1.0
paths:
  /data/stocks/download:
    post:
      summary: Download equities data
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                symbols: { type: array, items: { type: string } }
                start: { type: string, format: date }
                end: { type: string, format: date }
                interval: { type: string, enum: ["1d","1h","15m","5m"] }
              required: [symbols, start, end]
      responses: { '202': { description: Accepted } }
  /data/options/download:
    post:
      summary: Download option chains (snapshot)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                symbols: { type: array, items: { type: string } }
              required: [symbols]
      responses: { '202': { description: Accepted } }
  /strategy/nl_to_struct:
    post:
      summary: Convert NL to structured strategy
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                text: { type: string }
              required: [text]
      responses:
        '200':
          description: Structured strategy
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Strategy' }
  /strategy/confirm:
    post:
      summary: Store structured strategy
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/Strategy' }
      responses: { '201': { description: Created } }
  /strategy/compile/{strategy_id}:
    post:
      summary: Compile structured strategy to Backtrader code
      parameters:
        - in: path
          name: strategy_id
          required: true
          schema: { type: string }
      responses: { '201': { description: Code stored } }
  /backtest/run:
    post:
      summary: Run a backtest
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BacktestRequest'
      responses: { '202': { description: Accepted } }
  /backtest/result/{id}:
    get:
      summary: Get backtest results
      parameters:
        - in: path
          name: id
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Backtest summary
          content:
            application/json:
              schema: { $ref: '#/components/schemas/BacktestResult' }
components:
  schemas:
    Strategy:
      type: object
      properties:
        name: { type: string }
        universe: { type: array, items: { type: string } }
        timeframe:
          type: object
          properties:
            start: { type: string, format: date }
            end: { type: string, format: date }
            interval: { type: string, enum: ["1d","1h","15m","5m"] }
          required: [start, end, interval]
        entry: { type: array, items: { type: object } }
        exit: { type: array, items: { type: object } }
        position:
          type: object
          properties:
            sizing: { type: string, enum: ["percent_cash","fixed"] }
            value: { type: number }
            max_positions: { type: integer }
          required: [sizing, value]
        costs:
          type: object
          properties:
            commission_per_share: { type: number }
            slippage_bps: { type: number }
          required: [commission_per_share]
      required: [name, universe, timeframe, entry, exit, position, costs]
    BacktestRequest:
      type: object
      properties:
        strategy_id: { type: string }
        code_id: { type: string }
        universe: { type: array, items: { type: string } }
        start: { type: string, format: date }
        end: { type: string, format: date }
        initial_cash: { type: number }
        benchmarks: { type: array, items: { type: string } }
      required: [strategy_id, universe, start, end, initial_cash]
    BacktestResult:
      type: object
      properties:
        id: { type: string }
        performance:
          type: object
          properties:
            tot_return: { type: number }
            cagr: { type: number }
            max_dd: { type: number }
            sharpe: { type: number }
            excess_return: { type: number }
        benchmarks: { type: object }
        artifacts: { type: object }
```

---

### E) Finalized UX Flow (Happy Path)

1. **Data** → User selects symbols/time range → click **Download** → data cached (stocks; options snapshot optional).
2. **Strategy Builder** → User writes NL → click **Propose Structure** → app shows **structured JSON** → user edits/approves → **Compile** code.
3. **Backtest** → User selects **universe**, **time window**, **initial cash**, **benchmark (VOO/SPY/QQQ)** → **Run**.
4. **Results** → Show equity vs benchmark, P&L metrics, trades; allow CSV/HTML export.
5. **Iterate** → Tweak structured JSON or NL; rerun.

---

### F) Validation & Acceptance Criteria (Success)

- **Data Integrity**: Random spot‑checks confirm OHLCV totals and split/adjust alignment with source for ≥ 95% of sampled days.
- **Backtest Reproducibility**: Same inputs → identical results (hash match on equity CSV) across two runs.
- **Benchmark Parity**: Benchmark total return within ±0.5% of direct calculation from downloaded prices over the tested window.
- **Latency**: Single‑symbol 5‑year daily backtest completes ≤ 30s on baseline hardware.
- **Outperformance Visibility**: UI shows **excess return** (strategy − benchmark) and **cumulative curve overlay**.
- **Safety**: AST‑based code validation blocks filesystem/network access; run timeouts enforced.
- **Simplicity**: Codebase bootstraps with `pip install -r requirements.txt` and `streamlit run app.py` without additional services.

---

### G) Engineering Checklist (Build Order)

-

---

**End of Specification — Vibe Coding: Me‑Trade**

