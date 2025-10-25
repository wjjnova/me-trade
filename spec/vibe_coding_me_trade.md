# Vibe Coding: Me-Trade

---

## Project Snapshot

**Goal.** Deliver a Streamlit application that lets power users describe equity trading ideas in natural language, convert them into structured definitions and executable Backtrader strategies, run historical backtests, and review the output in one workspace.

**Tech Stack.** Python 3.11+, Streamlit multi-page app, Backtrader, yfinance/pandas, Plotly, SQLite (WAL). Core code now lives in `src/`, UI pages in `pages/`, tests/debug utilities in `tests/`, and specs in `spec/`.

**Key Capabilities (implemented 2025-10).**
- Cached equity/indicator/benchmark data management with on-demand downloads and CSV ingest helpers.
- Options-chain ingestion via yfinance plus Dolt-style CSV importer, complete with search/browsing UI.
- Natural-language strategy builder with LLM-backed parsing, JSON + code editors, validation, and persistence.
- Backtest launcher that compiles stored strategies, runs Backtrader, and keeps metrics/artifacts in SQLite.
- Results dashboard for historical runs, equity curves, metrics, and benchmark comparisons.
- Settings page to configure multiple LLM providers (OpenAI, Anthropic) via encrypted SQLite storage.
- English/Chinese UI localization driven by `src/ui/i18n.py`.

---

## Implemented Features

### Data Management (`pages/1_Data.py`)
- **Stocks.** Use `StockDataManager` to download OHLCV data (daily interval) through yfinance, persist to `equities_ohlcv`, and auto-refresh cached technical indicators. Includes favorites list, latest-cache stats, symbol-specific viewers, and bulk S&P 500 bundle downloader (`src/download_sp500_data.py`).
- **Options.** `OptionsDataManager` supports live yfinance pulls and offline CSV imports. Users can browse trade dates, expirations, individual contracts (with greeks), and timeline visualizations. Missing data surfaces via contextual warnings.
- **Benchmarks.** Managed download queue for index ETFs (VOO, SPY, QQQ, etc.) with success/error reporting and cached overview.
- **Indicators View.** Combined OHLCV + indicators explorer with quick-range presets, overlay toggles, Plotly charts, and CSV export.
- **Data Hygiene.** UI controls exist for deleting individual symbols or wiping caches (equities, indicators, options).

### Strategy Builder (`pages/2_Strategy_Builder.py`)
- **LLM Parsing.** `NLParser` toggles between rule-based parsing and provider-specific LLM calls using saved credentials. JSON schema covers universe, entry/exit logic, position sizing, and risk controls.
- **Triple Editor.** Human-readable summary, structured JSON, and generated Backtrader code stay in sync. Users can update and validate each format independently.
- **Validation Pipeline.** `StrategyCompiler` and `CodeValidator` ensure JSON adheres to schema and generated code passes static checks. Errors and warnings surface inline.
- **Persistence.** Strategies save into `strategies` table along with synced JSON/code artifacts in `codes`. Saved strategies list supports load/edit/delete operations.

### Backtesting (`pages/3_Backtest.py` & `src/backtest/engine.py`)
- **Strategy Selection.** Pull the most recent strategy snapshot, show metadata, and gate execution if code is missing.
- **Run Configuration.** Users override universe, capital, commission, and slippage; choose benchmark ETFs (from `config.BENCHMARK_SYMBOLS`).
- **Data Checks.** Integration with `StockDataManager` to detect missing OHLCV rows before launching.
- **Execution.** `BacktestEngine` wraps Backtrader runs, stores metadata in `backtests`, trades/equity curves in filesystem artifacts, and metrics via `MetricsCalculator` (Sharpe, Sortino, drawdown, total return, etc.).
- **Recent History.** Sidebar summary lists recent runs, including return figures, success/failure, and links to Results page.

### Results Viewer (`pages/4_Results.py`)
- **Run Browser.** Paginated list of completed backtests with filters and status indicators.
- **Metrics Panel.** Displays key stats, configuration recap, benchmark comparisons, and equity curve charts.
- **Artifacts.** Provides download links for stored CSV outputs when available.
- **Localization.** All UI strings translated through `t()` helper into English and Chinese.

### Settings & Admin (`pages/5_Settings.py`)
- **LLM Configurations.** CRUD interface for multiple provider/model/API-key combos stored in `llm_configs`. Active config is masked, timestamped, and used across pages.
- **Testing Harness.** Run sample NL descriptions through the active LLM pipeline inside the UI and inspect human/JSON/code outputs.
- **Language Selector.** Global sidebar language switch ensures consistent localization while suppressing Streamlit’s default page nav in favor of custom links.

### Supporting Utilities
- `src/data/indicators.py`: Indicator cache builder with batch refresh for SMA/EMA/RSI/MACD/Bollinger values.
- `src/data/benchmarks.py`: Benchmark download helpers.
- `src/models/strategy.py`: Strategy ORM helpers for persistence.
- `src/db/schema.py`: Schema migration helper that ensures legacy compatibility (column backfill, WAL mode, etc.).
- `tests/`: Pytest suites plus debugging scripts relocated from repo root; runnable via `pytest`.
- `start.sh`: Bootstrap script for virtualenv setup, dependency install, DB initialization, and Streamlit launch.

---

## Architecture Notes

- **App Entry.** `app.py` sets Streamlit page config, initializes database via `st.cache_resource`, and renders the landing page with live DB metrics.
- **Navigation.** Custom sidebar (`use_language_selector`) replaces default navigation, linking to `pages/1_...` through `pages/5_...`.
- **Configuration Module.** `src/config.py` centralizes defaults (DB path, file storage directory, initial cash/commission/slippage, benchmark list). Paths resolve relative to repository root.
- **Database.** SQLite file at `data/metrade.db` (auto-created). Key tables include:
  - `equities_ohlcv`, `technical_indicators`, `options_chain`, `options_volatility`
  - `strategies`, `codes`, `backtests`, `metrics_run`
  - `llm_configs`, plus helper tables for caching/backtest artifacts
- **Data Files.** Download artifacts and CSV exports live in `/files`. Option CSV imports read from `data/option/` by default.
- **LLM Integration.** Provider-agnostic configuration; NL parser dispatches to OpenAI or Anthropic clients when keys exist, otherwise falls back to deterministic parsing.

---

## Usage Guide

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Or run `./start.sh` to automate environment creation, dependency install, DB initialization, and Streamlit launch.

**First Run Tips.**
- Use the Data page to download equities before running a strategy. Indicator refresh may take a few seconds per symbol.
- Import or download at least one options chain if you plan to explore the Options tab.
- Configure an LLM provider in Settings so the Strategy Builder can parse natural-language input.
- Saved strategies populate the Backtest page dropdown automatically.

**Testing.** Execute `pytest` from repo root to run the relocated suites (`tests/test_basic.py`, etc.). Debug scripts inside `tests/debug_*.py` can be invoked directly with `python` for targeted diagnostics.

---

## Future Enhancements (Backlog)

1. Expand indicator set (e.g., ATR, stochastic oscillators) and surface them in the Strategy Builder schema.
2. Persist detailed trade logs and equity curves as structured tables for faster drill-down in Results.
3. Introduce portfolio-level backtesting (multi-strategy or allocation schedules) and cash management analytics.
4. Add notebook or API interfaces (FastAPI) for programmatic access to data downloads and backtests.
5. Implement role-based workspace sharing and API key encryption at rest beyond SQLite.
6. Enhance options analytics with volatility surfaces and scenario analysis.
7. Package the Streamlit app as a Docker image for easier deployment.

---

## Reference Locations

- Core modules: `src/`
- Streamlit pages: `pages/`
- Specs & docs: `spec/`
- Tests & debug utilities: `tests/`
- Cached data: `data/`
- Generated artifacts: `files/`

This document stays aligned with the codebase as of October 2025. Update alongside functional changes to keep stakeholders informed.
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

