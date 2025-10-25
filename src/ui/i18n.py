"""Internationalization utilities for Streamlit UI."""
from __future__ import annotations

from typing import Dict

_DEFAULT_LANGUAGE = "en"
_LANGUAGE_WIDGET_KEY = "language_selector"
_LANGUAGE_CHOICES = [
    ("en", "English"),
    ("zh", "中文"),
]

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "common.language_label": "Language / 语言",
        "common.start_date": "Start Date",
        "common.end_date": "End Date",
    "app.title": "📈 Me Trade",
        "app.subtitle": "Natural Language-Driven Backtesting for U.S. Stocks & Options",
        "app.home.content": (
            "Welcome to **Me Trade**, a lightweight application for testing trading strategies using natural language.\n\n"
            "### 🚀 Quick Start\n\n"
            "1. **Data** - Download stock and option data from Yahoo Finance\n"
            "2. **Strategy Builder** - Describe your strategy in plain English or structured JSON\n"
            "3. **Backtest** - Run your strategy against historical data\n"
            "4. **Results** - Analyze performance metrics and compare to benchmarks\n\n"
            "### 📊 Features\n\n"
            "- **Natural Language Strategy Definition** - Describe strategies in plain English\n"
            "- **Multiple Data Sources** - Yahoo Finance for stocks and options\n"
            "- **Comprehensive Backtesting** - Powered by Backtrader\n"
            "- **Benchmark Comparison** - Compare against VOO, SPY, QQQ\n"
            "- **Risk Metrics** - Sharpe, Sortino, Calmar ratios, max drawdown\n"
            "- **Local Storage** - SQLite database for data and results\n\n"
            "### 🎯 Supported Symbols (Initial Focus)\n\n"
            "{symbols}\n\n"
            "### 📖 How to Use\n\n"
            "Navigate using the sidebar to access different sections:\n\n"
            "- **Data**: Download and manage market data\n"
            "- **Strategy Builder**: Create and edit trading strategies  \n"
            "- **Backtest**: Execute strategies and view basic results\n"
            "- **Results**: Detailed analysis and metrics visualization\n\n"
            "### ⚙️ Configuration\n\n"
            "- **Initial Capital**: ${initial_cash:,.0f}\n"
            "- **Commission**: ${commission:.4f} per share\n"
            "- **Slippage**: {slippage_bps} basis points\n\n"
            "---\n\n"
            "**Get Started**: Use the sidebar to navigate to the Data page and download some market data!"
        ),
    "app.sidebar.navigation_heading": "### 🧭 Navigation",
        "app.sidebar.database_info_heading": "### 📊 Database Info",
        "app.sidebar.cached_symbols": "Cached Symbols",
        "app.sidebar.saved_strategies": "Saved Strategies",
        "app.sidebar.total_backtests": "Total Backtests",
        "app.sidebar.about_heading": "### ℹ️ About",
        "app.sidebar.about_content": (
            "**Version**: 0.1.0 (MVP)\n\n"
            "**Tech Stack**:\n"
            "- Streamlit (UI)\n"
            "- Backtrader (Backtesting)\n"
            "- yfinance (Data)\n"
            "- SQLite (Storage)\n"
            "- Plotly (Charts)\n\n"
            "**Source**: [GitHub](#)"
        ),
        "backtest.title": "Run Backtest",
        "backtest.subtitle": "Execute strategies and analyze results",
        "backtest.warning.no_strategies": "No strategies available. Create one in the Strategy Builder first!",
        "backtest.section.select_strategy": "1. Select Strategy",
        "backtest.form.choose_strategy": "Choose a strategy",
        "backtest.error.no_code": "No code found for this strategy!",
        "backtest.expander.strategy_details": "Strategy Details",
        "backtest.section.configure": "2. Configure Backtest",
        "backtest.form.universe": "Trading Universe (symbols)",
        "backtest.warning.missing_data": "Missing data for: {symbols}",
        "backtest.info.download_data": "Download data in the Data page first!",
        "backtest.form.initial_cash": "Initial Capital ($)",
        "backtest.form.commission": "Commission per share ($)",
        "backtest.form.slippage": "Slippage (basis points)",
        "backtest.section.benchmarks": "3. Select Benchmarks",
        "backtest.form.compare_against": "Compare against",
        "backtest.button.run": "🚀 Run Backtest",
        "backtest.spinner.running": "Running backtest... This may take a moment.",
        "backtest.success.completed": "✓ Backtest completed! ID: {bt_id}",
        "backtest.section.results_summary": "Results Summary",
        "backtest.metric.starting_value": "Starting Value",
        "backtest.metric.ending_value": "Ending Value",
        "backtest.metric.total_return": "Total Return",
        "backtest.metric.total_trades": "Total Trades",
        "backtest.info.view_results": "View detailed results in the Results page",
        "backtest.error.failed": "Backtest failed: {message}",
        "backtest.error.exception": "Backtest error: {message}",
        "backtest.section.recent": "Recent Backtests",
        "backtest.recent.item": "{status_icon} **{name}** - {bt_id} - Return: {return_str} - {created}",
        "backtest.info.no_backtests": "No backtests run yet",
        "data.title": "Data Management",
        "data.subtitle": "Download and manage stock and options data",
    "data.favorites.header": "Favorite Symbols",
    "data.favorites.help": "These symbols appear at the top of selectors across the Data page.",
    "data.favorites.list": "Favorites: {symbols}",
    "data.favorites.list_empty": "Favorites: none yet",
    "data.favorites.add_label": "Add symbol",
    "data.favorites.add_placeholder": "e.g. SPY",
    "data.favorites.add_button": "Add",
    "data.favorites.add_invalid": "Enter a symbol before adding.",
    "data.favorites.add_exists": "{symbol} is already in favorites.",
    "data.favorites.add_success": "Added {symbol} to favorites.",
    "data.favorites.remove_label": "Remove symbol",
    "data.favorites.remove_button": "Remove",
    "data.favorites.remove_success": "Removed {symbol} from favorites.",
    "data.favorites.remove_empty": "No favorite symbols to remove.",
        "data.tabs.stocks": "📈 Stocks",
        "data.tabs.options": "📊 Options",
        "data.tabs.benchmarks": "🎯 Benchmarks",
        "data.tabs.indicators": "📉 View Indicators",
    "data.stocks.header": "Daily Price Data",
        "data.stocks.download_title": "Refresh Daily Price Cache",
        "data.stocks.symbols_label": "Symbols (comma-separated)",
        "data.stocks.symbols_help": "Enter ticker symbols to refresh their daily price history",
        "data.stocks.fixed_window_note": "Daily downloads cover a fixed window from {start} to {end}.",
        "data.stocks.download_full_button": "Redownload Full History (2019→Today)",
        "data.stocks.download_latest_button": "Download Latest Daily Bars",
        "data.stocks.spinner": "Fetching daily bars...",
        "data.stocks.download_success": "✓ Downloaded {rows} rows for {symbol_count} symbols",
        "data.stocks.download_latest_up_to_date": "No updates required; cache is already current.",
        "data.stocks.download_latest_up_to_date_with_date": "All selected symbols already include data through {date}.",
        "data.stocks.download_latest_skipped": "Skipped {count} symbols with no newer data: {symbols}",
        "data.stocks.no_symbols": "Enter at least one symbol to update the cache.",
        "data.stocks.last_cached_info": "Most recent cached date: {date} (covering {count} of {total} symbols).",
        "data.stocks.last_cached_missing": "No cached data found for these symbols.",
        "data.common.download_failed": "Some downloads failed:",
        "data.common.success_item": "- {symbol}: {rows} rows",
        "data.common.error_item": "- {symbol}: {error}",
        "data.stocks.cached_title": "Daily Cache Overview",
        "data.stocks.cached_none": "No cached data yet",
        "data.stocks.cached_page_size": "Rows per page",
        "data.stocks.cached_page": "Page",
        "data.stocks.cached_stats": "Showing page {page} of {pages} ({total} symbols).",
        "data.stocks.cached_selector_label": "Jump to symbol",
        "data.stocks.cached_col_symbol": "Symbol",
        "data.stocks.cached_col_rows": "Rows",
        "data.stocks.cached_col_start": "First Date",
        "data.stocks.cached_col_end": "Last Date",
        "data.stocks.viewer_title": "Inspect Daily Bars",
        "data.stocks.viewer_select_label": "Symbol",
        "data.stocks.viewer_page_size": "Rows per page",
        "data.stocks.viewer_page": "Page",
        "data.stocks.viewer_empty": "No cached data available yet.",
        "data.stocks.viewer_no_rows": "No daily bars cached for this symbol yet.",
        "data.stocks.viewer_stats": "Showing page {page} of {pages} ({total} rows).",
        "data.stocks.delete_symbol_section_title": "Delete all data for {symbol}",
        "data.stocks.delete_symbol_confirm": "Yes, delete all data for {symbol}",
        "data.stocks.delete_symbol_button": "Delete symbol data",
        "data.stocks.delete_symbol_success": "Removed {equity_rows} equity rows and {indicator_rows} indicator rows for {symbol}.",
        "data.stocks.delete_symbol_failure": "Failed to delete {symbol}: {error}",
        "data.stocks.delete_all_title": "Clear entire equity cache",
        "data.stocks.delete_all_warning": "This removes **all** stored prices and indicators. This action cannot be undone.",
        "data.stocks.delete_all_confirm": "Yes, delete everything",
        "data.stocks.delete_all_button": "Delete all equity data",
        "data.stocks.delete_all_success": "Cleared {equity_rows} equity rows and {indicator_rows} indicator rows.",
        "data.stocks.bulk_title": "Download Top S&P 500 Bundle",
        "data.stocks.bulk_description": (
            "Download 100 popular S&P 500 constituents since January 1, 2019 plus key ETFs "
            "(VOO, QQQ, SPY, ARK funds, VTI, VT, IWM, EFA, EEM, DIA) and major "
            "indices (S&P 500, NASDAQ-100, Dow Jones, Russell 2000, VIX)."
        ),
        "data.stocks.bulk_button": "Download Top S&P 500 + ETFs",
        "data.stocks.bulk_spinner": "Downloading curated S&P 500 bundle...",
        "data.stocks.bulk_success": "✓ Downloaded data for {count} symbols (of {total}) totaling {rows} rows.",
        "data.stocks.bulk_failed_summary": "Failed symbols ({count}):",
        "data.stocks.bulk_error": "Download failed: {error}",
        "data.stocks.bulk_error_lxml": "Download failed: missing dependency 'lxml'. Run `pip install lxml` and try again.",
        "data.stocks.bulk_error_ssl": (
            "Download failed: SSL certificate verification problem. Install system root certificates "
            "or update Python's certificate store, then retry."
        ),
        "data.stocks.bulk_symbol_total": "Universe size: {total} symbols.",
        "data.stocks.bulk_preview": "Preview (top 5): {preview}",
        "data.upload.title": "Upload Custom Data",
        "data.upload.file_label": "Upload CSV file",
        "data.upload.help": "CSV must have columns: date, open, high, low, close, volume",
        "data.upload.symbol_label": "Symbol for uploaded data",
        "data.upload.process_button": "Process Upload",
        "data.upload.success": "✓ Uploaded {rows} rows for {symbol}",
        "data.upload.error": "Upload failed: {error}",
        "data.options.header": "Options Chain Data",
    "data.options.import_hint": "Tip: place Dolt CSV exports in `data/option_chain/` and use the importer above to populate this view.",
        "data.options.view_title": "View Cached Options",
        "data.options.select_symbol": "Select symbol",
        "data.options.available_expirations": "**Available expirations:** {count}",
        "data.options.select_expiration": "Expiration",
    "data.options.import_title": "Import Historical CSV Data",
    "data.options.import_help": "Load Dolt-exported CSV files from {path} into the local SQLite cache.",
    "data.options.import_button": "Import Option CSV Files",
    "data.options.import_spinner": "Importing CSV files...",
    "data.options.import_no_files": "No CSV files found in the option_chain folder.",
    "data.options.import_success": "✓ Imported {rows} option rows from {files} file(s).",
    "data.options.import_error_summary": "Import completed with {count} file error(s):",
    "data.options.import_error_item": "- {file}: {error}",
    "data.options.no_cached_data": "No cached option data yet. Download or import data to begin.",
    "data.options.no_trade_dates": "No trade dates found for this symbol.",
    "data.options.select_trade_date": "Trade date",
    "data.options.trade_date_view": "Select trade date",
    "data.options.trade_date_prev": "Previous",
    "data.options.trade_date_next": "Next",
    "data.options.trade_date_latest": "Latest",
    "data.options.expiration_label": "Expiration",
    "data.options.expiration_prev": "Previous",
    "data.options.expiration_next": "Next",
    "data.options.expiration_latest": "Nearest",
    "data.options.no_expirations": "No expirations available for the selected trade date.",
    "data.options.table_page_size": "Rows per page",
    "data.options.table_page": "Page",
    "data.options.table_stats": "Showing page {page} of {pages} ({total} strikes)",
    "data.options.col.call_bid": "Call Bid",
    "data.options.col.call_ask": "Call Ask",
    "data.options.col.strike": "Strike",
    "data.options.col.put_bid": "Put Bid",
    "data.options.col.put_ask": "Put Ask",
    "data.options.greeks_none": "No call or put data available for the selected strike.",
    "data.options.greeks_side_label": "View details for",
    "data.options.side.call": "Call",
    "data.options.side.put": "Put",
    "data.options.metric.bid": "Bid",
    "data.options.metric.ask": "Ask",
        "data.options.row_label.underlying": "Underlying Close",
    "data.options.metric.last": "Last",
    "data.options.metric.mid": "Mid",
    "data.options.metric.volume": "Volume",
    "data.options.metric.open_interest": "Open Interest",
    "data.options.metric.implied_vol": "Implied Vol",
    "data.options.metric.delta": "Delta",
    "data.options.metric.gamma": "Gamma",
    "data.options.metric.theta": "Theta",
    "data.options.metric.vega": "Vega",
    "data.options.metric.rho": "Rho",
    "data.options.metric.price": "Price",
    "data.options.metric.generic": "Value",
    "data.options.greeks_title": "{side} contract details for strike {strike}",
    "data.options.timeline_no_data": "No historical records available for this contract.",
    "data.options.timeline_trade_title": "Daily prices • {side} • Strike {strike} • Exp {expiration}",
    "data.options.timeline_trade_greeks": "Daily Greeks • {side} • Strike {strike} • Exp {expiration}",
    "data.options.timeline_axis_trade_date": "Trade date",
    "data.options.timeline_axis_expiration": "Expiration date",
    "data.options.timeline_expiration_no_data": "No alternative expirations recorded for this date.",
    "data.options.timeline_expiration_title": "Expiration curve • {side} • Strike {strike} • Trade {trade_date}",
    "data.options.timeline_expiration_greeks": "Expiration Greeks • {side} • Strike {strike} • Trade {trade_date}",
        "data.options.no_data": "No option chain data available for this symbol",
    "data.options.delete_title": "Delete Option Data",
    "data.options.delete_symbol_label": "Select symbol to delete",
    "data.options.delete_symbol_confirm": "Remove all option data for {symbol}",
    "data.options.delete_symbol_button": "Delete symbol data",
    "data.options.delete_symbol_success": "✓ Removed {rows} option rows for {symbol}.",
    "data.options.delete_all_title": "Delete All Cached Options",
    "data.options.delete_all_confirm": "I understand this removes every cached option row",
    "data.options.delete_all_button": "Delete all option data",
    "data.options.delete_all_success": "✓ Removed {rows} option rows.",
        "data.benchmarks.header": "Benchmark Data",
        "data.benchmarks.description": "Download benchmark indices for comparison",
        "data.benchmarks.list": "**Benchmarks:** {symbols}",
        "data.benchmarks.start": "Benchmark Start Date",
        "data.benchmarks.end": "Benchmark End Date",
        "data.benchmarks.download_button": "Download Benchmarks",
        "data.benchmarks.spinner": "Downloading benchmark data...",
        "data.benchmarks.success": "✓ Downloaded benchmark data",
        "data.benchmarks.success_item": "- {symbol}: {rows} rows",
        "data.benchmarks.failed": "Some downloads failed:",
        "data.benchmarks.cached_title": "Cached Benchmark Data",
        "data.indicators.header": "View Stock Data with Indicators",
        "data.indicators.no_data": "No stock data available. Please download data in the Stocks tab first.",
        "data.indicators.select_symbol": "Symbol",
        "data.indicators.date_range": "Date Range",
    "data.indicators.date_preset.label": "Quick range",
    "data.indicators.date_preset.custom": "Custom range",
    "data.indicators.date_preset.last_week": "Last Week",
    "data.indicators.date_preset.last_month": "Last Month",
    "data.indicators.date_preset.last_three_months": "Last 3 Months",
    "data.indicators.date_preset.last_year": "Last Year",
    "data.indicators.date_preset.last_two_years": "Last 2 Years",
    "data.indicators.date_preset.last_three_years": "Last 3 Years",
    "data.indicators.date_preset.last_five_years": "Last 5 Years",
        "data.indicators.from": "From",
        "data.indicators.to": "To",
        "data.indicators.section_title": "Overlay Indicators",
        "data.indicators.checkbox.sma20": "SMA 20",
        "data.indicators.checkbox.sma50": "SMA 50",
        "data.indicators.checkbox.sma200": "SMA 200",
        "data.indicators.checkbox.ema12": "EMA 12",
        "data.indicators.checkbox.ema26": "EMA 26",
        "data.indicators.checkbox.rsi": "RSI",
        "data.indicators.checkbox.macd": "MACD",
        "data.indicators.checkbox.bbands": "Bollinger Bands",
        "data.indicators.stored_available": "📊 Stored indicators available",
        "data.indicators.stored_missing": "⚠️ No stored indicators. Values will be calculated on the fly.",
        "data.indicators.refresh_button": "Refresh Indicators",
        "data.indicators.refresh_help": "Rebuild cached indicators from stored OHLCV data",
        "data.indicators.refresh_spinner": "Refreshing indicator cache...",
        "data.indicators.refresh_success": "✓ Stored indicators refreshed",
        "data.indicators.refresh_no_source": "Raw OHLCV data for {symbol} is missing in the selected window.",
        "data.indicators.loading_spinner": "Loading indicators...",
        "data.indicators.load_no_data": "No data available for {symbol} in the selected date range",
    "data.indicators.chart_title": "{symbol} · Price and Indicator Dashboard",
        "data.indicators.subplot.price": "Price",
        "data.indicators.subplot.rsi": "RSI",
        "data.indicators.subplot.macd": "MACD",
        "data.indicators.legend.close": "Close Price",
    "data.indicators.legend.candles": "Price candles",
        "data.indicators.legend.ema12": "EMA 12",
        "data.indicators.legend.bb_upper": "BB Upper",
        "data.indicators.legend.bb_middle": "BB Middle",
        "data.indicators.legend.bb_lower": "BB Lower",
        "data.indicators.legend.macd_signal": "Signal",
        "data.indicators.legend.macd_histogram": "Histogram",
        "data.indicators.xaxis.date": "Date",
        "data.indicators.yaxis.price": "Price ($)",
        "data.indicators.table_title": "Indicator Data",
        "data.indicators.table_page_size": "Rows per page",
        "data.indicators.table_page": "Page",
        "data.indicators.table_stats": "Showing page {page} of {pages} · {total} rows total",
        "data.indicators.download_button": "Download full dataset",
        "builder.title": "Strategy Builder",
        "builder.subtitle": "Create trading strategies using natural language or structured definitions",
        "builder.tabs.define": "📝 Define Strategy",
        "builder.tabs.saved": "💾 Saved Strategies",
        
        # Define Strategy Tab
        "builder.define.header": "Define Trade Strategy",
        "builder.define.description": "Describe your trading strategy in plain English or Chinese, and we'll convert it to all three formats",
        "builder.define.sample": (
            "Buy AAPL when the 50-day SMA crosses above the 200-day SMA and RSI is below 70.\n"
            "Sell with an 8% trailing stop or 15% profit target.\n"
            "Test from 2019-01-01 to 2024-12-31."
        ),
        "builder.define.nl_input_label": "Strategy Description",
        "builder.define.override_label": "Override Symbols (optional)",
        "builder.define.override_placeholder": "AAPL, MSFT, GOOGL",
        "builder.define.parse_button": "Parse Strategy",
        "builder.define.spinner": "Parsing strategy with LLM...",
        "builder.define.success": "✓ Strategy parsed successfully into three formats!",
        
        # Three formats section
        "builder.define.formats_header": "Strategy Formats (All Editable)",
        "builder.define.format_human": "📖 Human Readable",
        "builder.define.format_json": "⚙️ JSON Definition",
        "builder.define.format_code": "💻 Backtrader Code",
        
        # Human Readable
        "builder.define.human_description": "A clear, structured description of your strategy",
        "builder.define.human_label": "Human-Readable Strategy",
        "builder.define.update_human": "Update Human Description",
        
        # JSON Definition
        "builder.define.json_description": "Structured JSON strategy definition (editable)",
        "builder.define.json_label": "Strategy JSON",
        "builder.define.validate_json": "Validate JSON",
        "builder.define.validate_success": "✓ Strategy JSON is valid!",
        "builder.define.validate_error": "Validation error: {error}",
        "builder.define.compile_json": "Compile to Code",
        "builder.define.compile_success": "✓ Code compiled and validated!",
        "builder.define.compile_warning": "Code compiled but has validation warnings:",
        "builder.define.compile_error": "Compilation error: {error}",
        
        # Backtrader Code
        "builder.define.code_description": "Complete Backtrader strategy class (editable)",
        "builder.define.code_label": "Backtrader Python Code",
        "builder.define.validate_code": "Validate Code",
        "builder.define.code_valid": "✓ Code is valid!",
        "builder.define.code_warnings": "Code has validation warnings:",
        "builder.define.update_code": "Update Code",
        
        # Save section
        "builder.define.save_header": "Save Strategy",
        "builder.define.strategy_name": "Strategy Name",
        "builder.define.save_button": "💾 Save Strategy",
        "builder.define.save_success": "✓ Strategy saved! ID: {strategy_id}",
        "builder.define.save_error_no_data": "Please parse or define a strategy first",
        "builder.define.update_success": "✓ Updated successfully!",
        
        # Saved Strategies Tab
        "builder.saved.header": "Saved Strategies",
        "builder.saved.id": "**ID:** {value}",
        "builder.saved.created": "**Created:** {value}",
        "builder.saved.format_human": "📖 Human Readable",
        "builder.saved.format_json": "⚙️ JSON",
        "builder.saved.format_code": "💻 Code",
        "builder.saved.human_label": "Human-Readable Description",
        "builder.saved.json_label": "JSON Definition",
        "builder.saved.code_label": "Backtrader Code",
        "builder.saved.validate_button": "Validate",
        "builder.saved.validate_success": "✓ Valid!",
        "builder.saved.validate_error": "Error: {error}",
        "builder.saved.code_valid": "✓ Code is valid!",
        "builder.saved.code_warnings": "Code has warnings:",
        "builder.saved.update_button": "Update",
        "builder.saved.update_success": "✓ Updated!",
        "builder.saved.update_error": "Update error: {error}",
        "builder.saved.load_button": "Load to Editor",
        "builder.saved.load_success": "Strategy loaded to editor!",
        "builder.saved.load_error": "Load error: {error}",
        "builder.saved.delete_button": "Delete",
        "builder.saved.delete_success": "Strategy deleted!",
        "builder.saved.empty": "No saved strategies yet. Create one using the Define Strategy tab!",
        
        # Settings Page
        "settings.title": "Settings",
        "settings.subtitle": "Configure application settings and LLM integrations",
        
        # LLM Configuration
        "settings.llm.header": "LLM Configuration",
        "settings.llm.description": "Configure AI models for natural language strategy parsing. Supports OpenAI (GPT) and Anthropic (Claude).",
        "settings.llm.add_config": "➕ Add New LLM Configuration",
        "settings.llm.form_title": "LLM Provider Settings",
        "settings.llm.provider_label": "Provider",
        "settings.llm.provider_help": "Choose between OpenAI (GPT models) or Anthropic (Claude models)",
        "settings.llm.model_label": "Model",
        "settings.llm.model_help": "Select the specific model version to use",
        "settings.llm.api_key_label": "API Key",
        "settings.llm.api_key_help": "Enter your API key (will be stored securely and masked in the UI)",
        "settings.llm.api_key_required": "API Key is required",
        "settings.llm.save_button": "💾 Save Configuration",
        "settings.llm.save_success": "✓ LLM configuration saved and activated!",
        "settings.llm.current_config": "Active Configuration",
        "settings.llm.config_updated": "Last updated: {date}",
        "settings.llm.delete_button": "🗑️ Delete",
        "settings.llm.delete_success": "Configuration deleted successfully",
        "settings.llm.all_configs": "All Saved Configurations",
        "settings.llm.no_configs": "No LLM configurations saved yet. Add one above to enable AI-powered strategy parsing.",
        "settings.llm.created": "Created",
        "settings.llm.status": "Status",
        "settings.llm.active": "Active",
        "settings.llm.inactive": "Inactive",
        "settings.llm.activate_button": "✅ Activate",
        "settings.llm.activate_success": "Configuration activated successfully",
        "settings.llm.test_header": "Test LLM Connection",
        "settings.llm.test_input_label": "Test Strategy Description",
        "settings.llm.test_button": "🧪 Test Connection",
        "settings.llm.test_spinner": "Testing LLM connection...",
        "settings.llm.test_success": "✓ LLM connection successful!",
        "settings.llm.test_show_results": "View Test Results",
        "settings.llm.test_error": "Test failed: {error}",
        "settings.llm.test_no_config": "No active LLM configuration. Add one above to test.",
        
        # Strategy Builder LLM status
        "builder.define.llm_active": "LLM Active",
        "builder.define.llm_inactive": "⚠️ No LLM configured. Using rule-based parsing. Configure LLM in Settings page for better results.",
        
        "results.title": "Backtest Results",
        "results.subtitle": "Analyze backtest performance and metrics",
        "results.info.no_completed": "No completed backtests yet. Run a backtest first!",
        "results.section.select": "Select Backtest",
        "results.form.choose_backtest": "Choose backtest",
        "results.warning.no_metrics": "No metrics available for this backtest",
        "results.section.summary": "Performance Summary",
        "results.metric.total_return": "Total Return",
        "results.metric.sharpe": "Sharpe Ratio",
        "results.metric.max_dd": "Max Drawdown",
        "results.metric.excess_return": "Excess Return",
        "results.metric.cagr": "CAGR",
        "results.metric.sortino": "Sortino Ratio",
        "results.metric.calmar": "Calmar Ratio",
        "results.tabs.equity": "📈 Equity Curve",
        "results.tabs.metrics": "📊 Metrics",
        "results.tabs.trades": "📝 Trades",
        "results.tabs.benchmark": "🎯 Benchmark Comparison",
        "results.tabs.details": "📋 Details",
        "results.tabs.equity_header": "Equity Trend",
        "results.tabs.metrics_header": "Performance Metrics",
        "results.tabs.trades_header": "Executed Trades",
        "results.tabs.benchmark_header": "Benchmark Comparison",
        "results.chart.equity_trend": "Equity Trend",
        "results.chart.daily_returns": "Daily Gain/Loss",
        "results.caption.sessions": "Gain sessions: {gains} | Loss sessions: {losses}",
        "results.section.top_gains": "Top Gain Sessions",
        "results.section.top_losses": "Top Loss Sessions",
        "results.info.no_gain_sessions": "No gain sessions recorded",
        "results.info.no_loss_sessions": "No loss sessions recorded",
        "results.info.no_equity": "No equity curve data available for this backtest yet.",
        "results.table.metric": "Metric",
        "results.table.value": "Value",
        "results.text.benchmarks": "**Benchmarks:** {benchmarks}",
        "results.warning.no_benchmark_data": "Benchmark data not available. Download benchmark data in the Data page.",
        "results.info.no_benchmarks": "No benchmarks selected for this backtest",
        "results.benchmark.symbol": "Symbol",
        "results.benchmark.outperformance": "Strategy Outperformance",
        "results.section.configuration": "Backtest Configuration",
        "results.config.backtest_id": "**Backtest ID:** {value}",
        "results.config.strategy": "**Strategy:** {value}",
        "results.config.status": "**Status:** {value}",
        "results.config.created": "**Created:** {value}",
        "results.config.universe": "**Universe:** {value}",
        "results.config.start": "**Start Date:** {value}",
        "results.config.end": "**End Date:** {value}",
        "results.config.initial_cash": "**Initial Cash:** {value}",
        "results.section.strategy_definition": "Strategy Definition",
        "results.section.export": "Export Results",
        "results.button.export_json": "Export as JSON",
        "results.button.download_json": "Download JSON",
        "results.button.export_metrics": "Export Metrics as CSV",
        "results.button.download_csv": "Download CSV",
        "results.info.export_html": "HTML export coming soon",
        "results.gain_loss.date": "Date",
        "results.gain_loss.return": "Return (%)",
        "results.gain_loss.value": "Portfolio Value ($)",
        "results.gain_loss.pnl": "Cumulative PnL ($)",
        "results.trades.metric.trades": "Trade Events",
        "results.trades.metric.realized": "Realized P/L",
        "results.trades.metric.win_rate": "Win Rate",
        "results.trades.metric.avg_allocation": "Avg Allocation",
        "results.trades.caption.avg_hold": "Average holding period: {bars} bars",
        "results.trades.no_data": "No trades were executed for this backtest.",
        "results.trades.column.timestamp": "Date",
        "results.trades.column.symbol": "Symbol",
        "results.trades.column.action": "Side",
        "results.trades.column.size": "Size",
        "results.trades.column.price": "Price",
        "results.trades.column.value": "Value",
        "results.trades.column.commission": "Commission",
        "results.trades.column.pnl": "P/L",
        "results.trades.column.pnl_pct": "P/L %",
        "results.trades.column.alloc_pct": "Allocation %",
        "results.trades.column.holding": "Hold (bars)",
        "results.trades.column.reason": "Reason",
        "app.nav.home": "🏠 Home",
        "app.nav.data": "📦 Data",
        "app.nav.builder": "🛠️ Strategy Builder",
        "app.nav.backtest": "🚀 Backtest",
    "app.nav.results": "📊 Results",
    "app.nav.settings": "⚙️ Settings",
    },
    "zh": {
        "common.language_label": "语言 / Language",
        "common.start_date": "开始日期",
        "common.end_date": "结束日期",
    "app.title": "📈 Me Trade",
        "app.subtitle": "面向美股与期权的自然语言回测平台",
        "app.home.content": (
            "欢迎来到 **Me Trade**，一个通过自然语言快速构建并测试交易策略的轻量级应用。\n\n"
            "### 🚀 快速上手\n\n"
            "1. **数据** - 从 Yahoo Finance 下载股票与期权数据\n"
            "2. **策略构建器** - 使用自然语言或结构化 JSON 描述策略\n"
            "3. **回测** - 在历史数据上运行策略\n"
            "4. **结果** - 分析绩效指标并对比基准\n\n"
            "### 📊 功能亮点\n\n"
            "- **自然语言策略定义** - 直接用英文或中文描述策略\n"
            "- **多数据源支持** - 基于 Yahoo Finance 的股票与期权数据\n"
            "- **全面回测引擎** - 使用 Backtrader 驱动\n"
            "- **基准对比** - 支持与 VOO、SPY、QQQ 等指数比较\n"
            "- **风险指标** - 提供夏普、索提诺、卡尔玛以及最大回撤\n"
            "- **本地存储** - SQLite 保存数据与回测结果\n\n"
            "### 🎯 支持的标的（初始推荐）\n\n"
            "{symbols}\n\n"
            "### 📖 使用指南\n\n"
            "请通过侧边栏导航至以下页面：\n\n"
            "- **数据**：下载与管理市场数据\n"
            "- **策略构建器**：创建或编辑交易策略  \n"
            "- **回测**：运行策略并查看基础结果\n"
            "- **结果**：深入分析绩效指标与图表\n\n"
            "### ⚙️ 配置参数\n\n"
            "- **初始资金**：${initial_cash:,.0f}\n"
            "- **佣金**：每股 ${commission:.4f}\n"
            "- **滑点**：{slippage_bps} 基点\n\n"
            "---\n\n"
            "**快速开始**：先进入“数据”页面下载行情，再构建并运行策略吧！"
        ),
    "app.sidebar.navigation_heading": "### 🧭 导航",
        "app.sidebar.database_info_heading": "### 📊 数据库信息",
        "app.sidebar.cached_symbols": "已缓存标的数",
        "app.sidebar.saved_strategies": "已保存策略数",
        "app.sidebar.total_backtests": "累计回测次数",
        "app.sidebar.about_heading": "### ℹ️ 关于",
        "app.sidebar.about_content": (
            "**版本**：0.1.0（MVP）\n\n"
            "**技术栈**：\n"
            "- Streamlit（界面）\n"
            "- Backtrader（回测）\n"
            "- yfinance（数据）\n"
            "- SQLite（存储）\n"
            "- Plotly（图表）\n\n"
            "**源码**： [GitHub](#)"
        ),
        "backtest.title": "运行回测",
        "backtest.subtitle": "执行策略并分析结果",
        "backtest.warning.no_strategies": "当前没有可用策略，请先在“策略构建器”页面创建。",
        "backtest.section.select_strategy": "1. 选择策略",
        "backtest.form.choose_strategy": "选择策略",
        "backtest.error.no_code": "未找到该策略对应的代码！",
        "backtest.expander.strategy_details": "策略详情",
        "backtest.section.configure": "2. 配置回测",
        "backtest.form.universe": "交易标的（可输入多个代码）",
        "backtest.warning.missing_data": "缺少以下标的的数据：{symbols}",
        "backtest.info.download_data": "请先在“数据”页面下载所需行情。",
        "backtest.form.initial_cash": "初始资金（美元）",
        "backtest.form.commission": "每股佣金（美元）",
        "backtest.form.slippage": "滑点（基点）",
        "backtest.section.benchmarks": "3. 选择基准",
        "backtest.form.compare_against": "选择对比基准",
        "backtest.button.run": "🚀 运行回测",
        "backtest.spinner.running": "正在运行回测……请稍候。",
        "backtest.success.completed": "✓ 回测完成！ID：{bt_id}",
        "backtest.section.results_summary": "结果概览",
        "backtest.metric.starting_value": "起始市值",
        "backtest.metric.ending_value": "结束市值",
        "backtest.metric.total_return": "总收益率",
        "backtest.metric.total_trades": "交易次数",
        "backtest.info.view_results": "详细指标可在“结果”页面查看。",
        "backtest.error.failed": "回测失败：{message}",
        "backtest.error.exception": "回测出现错误：{message}",
        "backtest.section.recent": "近期回测",
        "backtest.recent.item": "{status_icon} **{name}** - {bt_id} - 收益：{return_str} - {created}",
        "backtest.info.no_backtests": "尚未运行任何回测",
        "data.title": "数据管理",
        "data.subtitle": "下载并管理股票与期权数据",
    "data.favorites.header": "自选列表",
    "data.favorites.help": "这些标的会在数据页的选择器顶部显示。",
    "data.favorites.list": "当前自选：{symbols}",
    "data.favorites.list_empty": "当前自选：暂无",
    "data.favorites.add_label": "添加标的",
    "data.favorites.add_placeholder": "例如 SPY",
    "data.favorites.add_button": "添加",
    "data.favorites.add_invalid": "请输入要添加的标的代码。",
    "data.favorites.add_exists": "{symbol} 已在自选列表中。",
    "data.favorites.add_success": "已将 {symbol} 添加到自选列表。",
    "data.favorites.remove_label": "移除标的",
    "data.favorites.remove_button": "移除",
    "data.favorites.remove_success": "已从自选列表移除 {symbol}。",
    "data.favorites.remove_empty": "当前没有可移除的自选标的。",
        "data.tabs.stocks": "📈 股票",
        "data.tabs.options": "📊 期权",
        "data.tabs.benchmarks": "🎯 基准",
        "data.tabs.indicators": "📉 指标查看",
    "data.stocks.header": "日线数据",
        "data.stocks.download_title": "更新日线数据缓存",
        "data.stocks.symbols_label": "股票代码（逗号分隔）",
        "data.stocks.symbols_help": "请输入要更新日线数据的代码，多个代码用逗号分隔",
        "data.stocks.fixed_window_note": "日线下载窗口固定为 {start} 至 {end}。",
        "data.stocks.download_full_button": "重新下载 2019→现在 的全部日线",
        "data.stocks.download_latest_button": "下载最新日线数据",
        "data.stocks.spinner": "正在获取日线数据……",
        "data.stocks.download_success": "✓ 已为 {symbol_count} 个标的下载 {rows} 行日线数据",
        "data.stocks.download_latest_up_to_date": "全部标的已是最新日线数据。",
        "data.stocks.download_latest_up_to_date_with_date": "所有标的的日线已覆盖至 {date}。",
        "data.stocks.download_latest_skipped": "以下 {count} 个标的没有更新被跳过：{symbols}",
        "data.stocks.no_symbols": "请输入至少一个股票/指数代码以更新缓存。",
        "data.stocks.last_cached_info": "最新缓存日期：{date}（覆盖 {total} 个标的中的 {count} 个）。",
        "data.stocks.last_cached_missing": "这些标的尚未缓存任何数据。",
        "data.common.download_failed": "部分下载失败：",
        "data.common.success_item": "- {symbol}：{rows} 行",
        "data.common.error_item": "- {symbol}：{error}",
        "data.stocks.cached_title": "日线缓存概览",
        "data.stocks.cached_none": "暂无缓存数据",
        "data.stocks.cached_page_size": "每页数量",
        "data.stocks.cached_page": "页码",
        "data.stocks.cached_stats": "第 {page} / {pages} 页，共 {total} 个标的。",
        "data.stocks.cached_selector_label": "跳转到标的",
        "data.stocks.cached_col_symbol": "标的",
        "data.stocks.cached_col_rows": "行数",
        "data.stocks.cached_col_start": "起始日期",
        "data.stocks.cached_col_end": "最新日期",
        "data.stocks.viewer_title": "查看日线明细",
        "data.stocks.viewer_select_label": "选择标的",
        "data.stocks.viewer_page_size": "每页行数",
        "data.stocks.viewer_page": "页码",
        "data.stocks.viewer_empty": "尚无缓存数据。",
        "data.stocks.viewer_no_rows": "该标的尚无日线数据。",
        "data.stocks.viewer_stats": "第 {page} / {pages} 页，共 {total} 行。",
        "data.stocks.delete_symbol_section_title": "删除 {symbol} 的全部数据",
        "data.stocks.delete_symbol_confirm": "确认删除 {symbol} 的全部数据",
        "data.stocks.delete_symbol_button": "删除该标的",
        "data.stocks.delete_symbol_success": "已删除 {symbol} 的 {equity_rows} 行行情数据和 {indicator_rows} 行指标数据。",
        "data.stocks.delete_symbol_failure": "删除 {symbol} 失败：{error}",
        "data.stocks.delete_all_title": "清空全部行情缓存",
        "data.stocks.delete_all_warning": "这将删除所有已存价格与指标，且无法撤销。",
        "data.stocks.delete_all_confirm": "确认清空全部数据",
        "data.stocks.delete_all_button": "删除全部行情数据",
        "data.stocks.delete_all_success": "已删除 {equity_rows} 行行情数据与 {indicator_rows} 行指标数据。",
        "data.stocks.bulk_title": "批量下载标普500热门组合",
        "data.stocks.bulk_description": (
            "自 2019-01-01 起下载 100 只最受关注的标普500成分股，以及核心 ETF（VOO、QQQ、SPY、ARK 系列、VTI、VT、IWM、EFA、EEM、DIA）"
            "与主要市场指数（标普500、纳指100、道琼斯、罗素2000、VIX）。"
        ),
        "data.stocks.bulk_button": "下载标普热门股 + ETF",
        "data.stocks.bulk_spinner": "正在下载标普热门组合……",
        "data.stocks.bulk_success": "✓ 已为 {total} 个标的中的 {count} 个下载成功，共插入 {rows} 行数据。",
        "data.stocks.bulk_failed_summary": "下载失败的标的（{count}）：",
        "data.stocks.bulk_error": "下载失败：{error}",
        "data.stocks.bulk_error_lxml": "下载失败：缺少依赖 lxml，请执行 `pip install lxml` 后重试。",
        "data.stocks.bulk_error_ssl": "下载失败：SSL 证书校验失败，请安装系统根证书或更新 Python 证书后重试。",
        "data.stocks.bulk_symbol_total": "标的数量：{total} 个。",
        "data.stocks.bulk_preview": "前 5 个标的预览：{preview}",
        "data.upload.title": "上传自定义数据",
        "data.upload.file_label": "上传 CSV 文件",
        "data.upload.help": "CSV 需包含列：date、open、high、low、close、volume",
        "data.upload.symbol_label": "上传数据对应的代码",
        "data.upload.process_button": "处理上传",
        "data.upload.success": "✓ 已为 {symbol} 上传 {rows} 行数据",
        "data.upload.error": "上传失败：{error}",
        "data.options.header": "期权链数据",
    "data.options.import_hint": "提示：将 Dolt 导出的 CSV 放入 data/option_chain/ 中，然后使用上方导入工具填充数据。",
        "data.options.view_title": "查看已缓存期权",
        "data.options.select_symbol": "选择代码",
        "data.options.available_expirations": "**可用到期日：** {count}",
        "data.options.select_expiration": "到期日",
    "data.options.import_title": "导入历史 CSV 数据",
    "data.options.import_help": "将 {path} 中的 Dolt 导出 CSV 文件导入本地 SQLite 缓存。",
    "data.options.import_button": "导入期权 CSV 文件",
    "data.options.import_spinner": "正在导入 CSV 数据……",
    "data.options.import_no_files": "option_chain 文件夹内未找到 CSV 文件。",
    "data.options.import_success": "✓ 已从 {files} 个文件导入 {rows} 条期权记录。",
    "data.options.import_error_summary": "导入完成，但有 {count} 个文件出错：",
    "data.options.import_error_item": "- {file}：{error}",
    "data.options.no_cached_data": "当前没有期权缓存，请先下载或导入数据。",
    "data.options.no_trade_dates": "该标的没有可用的交易日。",
    "data.options.select_trade_date": "交易日",
    "data.options.trade_date_view": "选择交易日",
    "data.options.trade_date_prev": "上一日",
    "data.options.trade_date_next": "下一日",
    "data.options.trade_date_latest": "最新",
    "data.options.expiration_label": "到期日",
    "data.options.expiration_prev": "前一个",
    "data.options.expiration_next": "后一个",
    "data.options.expiration_latest": "最近",
    "data.options.no_expirations": "所选交易日没有可用的到期日。",
    "data.options.table_page_size": "每页行数",
    "data.options.table_page": "页码",
    "data.options.table_stats": "第 {page} / {pages} 页，共 {total} 个行权价",
    "data.options.col.call_bid": "看涨买价",
    "data.options.col.call_ask": "看涨卖价",
    "data.options.col.strike": "行权价",
    "data.options.col.put_bid": "看跌买价",
    "data.options.col.put_ask": "看跌卖价",
    "data.options.greeks_none": "当前行没有可用的看涨或看跌数据。",
    "data.options.greeks_side_label": "查看合约",
    "data.options.side.call": "看涨",
    "data.options.side.put": "看跌",
    "data.options.metric.bid": "买价",
    "data.options.metric.ask": "卖价",
        "data.options.row_label.underlying": "标的收盘价",
    "data.options.metric.last": "最新价",
    "data.options.metric.mid": "中间价",
    "data.options.metric.volume": "成交量",
    "data.options.metric.open_interest": "未平仓量",
    "data.options.metric.implied_vol": "隐含波动率",
    "data.options.metric.delta": "Delta",
    "data.options.metric.gamma": "Gamma",
    "data.options.metric.theta": "Theta",
    "data.options.metric.vega": "Vega",
    "data.options.metric.rho": "Rho",
    "data.options.metric.price": "价格",
    "data.options.metric.generic": "数值",
    "data.options.greeks_title": "{side}合约：行权价 {strike}",
    "data.options.timeline_no_data": "暂无该合约的历史记录。",
    "data.options.timeline_trade_title": "按交易日 • {side} • 行权价 {strike} • 到期 {expiration}",
    "data.options.timeline_trade_greeks": "Greeks 日线 • {side} • 行权价 {strike} • 到期 {expiration}",
    "data.options.timeline_axis_trade_date": "交易日",
    "data.options.timeline_axis_expiration": "到期日",
    "data.options.timeline_expiration_no_data": "所选交易日没有其他到期日记录。",
    "data.options.timeline_expiration_title": "按到期日 • {side} • 行权价 {strike} • 交易日 {trade_date}",
    "data.options.timeline_expiration_greeks": "Greeks 到期曲线 • {side} • 行权价 {strike} • 交易日 {trade_date}",
        "data.options.no_data": "该标的暂无期权链数据",
    "data.options.delete_title": "删除期权数据",
    "data.options.delete_symbol_label": "选择要删除的代码",
    "data.options.delete_symbol_confirm": "删除 {symbol} 的全部期权数据",
    "data.options.delete_symbol_button": "删除该代码",
    "data.options.delete_symbol_success": "✓ 已删除 {symbol} 的 {rows} 条期权记录。",
    "data.options.delete_all_title": "清空全部期权缓存",
    "data.options.delete_all_confirm": "我确认删除所有缓存的期权数据",
    "data.options.delete_all_button": "删除全部期权数据",
    "data.options.delete_all_success": "✓ 已删除 {rows} 条期权记录。",
        "data.benchmarks.header": "基准数据",
        "data.benchmarks.description": "下载基准指数用于对比",
        "data.benchmarks.list": "**基准：** {symbols}",
        "data.benchmarks.start": "基准开始日期",
        "data.benchmarks.end": "基准结束日期",
        "data.benchmarks.download_button": "下载基准数据",
        "data.benchmarks.spinner": "正在下载基准数据……",
        "data.benchmarks.success": "✓ 基准数据下载完成",
        "data.benchmarks.success_item": "- {symbol}：{rows} 行",
        "data.benchmarks.failed": "部分下载失败：",
        "data.benchmarks.cached_title": "已缓存基准数据",
        "data.indicators.header": "指标可视化",
        "data.indicators.no_data": "暂无股票数据，请先在“股票”标签下载行情。",
        "data.indicators.select_symbol": "股票代码",
        "data.indicators.date_range": "日期范围",
    "data.indicators.date_preset.label": "快捷区间",
    "data.indicators.date_preset.custom": "自定义区间",
    "data.indicators.date_preset.last_week": "最近一周",
    "data.indicators.date_preset.last_month": "最近一月",
    "data.indicators.date_preset.last_three_months": "最近三个月",
    "data.indicators.date_preset.last_year": "最近一年",
    "data.indicators.date_preset.last_two_years": "最近两年",
    "data.indicators.date_preset.last_three_years": "最近三年",
    "data.indicators.date_preset.last_five_years": "最近五年",
        "data.indicators.from": "起始日期",
        "data.indicators.to": "结束日期",
        "data.indicators.section_title": "指标叠加",
        "data.indicators.checkbox.sma20": "SMA 20",
        "data.indicators.checkbox.sma50": "SMA 50",
        "data.indicators.checkbox.sma200": "SMA 200",
        "data.indicators.checkbox.ema12": "EMA 12",
        "data.indicators.checkbox.ema26": "EMA 26",
        "data.indicators.checkbox.rsi": "RSI",
        "data.indicators.checkbox.macd": "MACD",
        "data.indicators.checkbox.bbands": "布林带",
        "data.indicators.stored_available": "📊 已有存储的指标数据",
        "data.indicators.stored_missing": "⚠️ 暂无存储的指标，将在查看时即时计算。",
        "data.indicators.refresh_button": "刷新指标缓存",
        "data.indicators.refresh_help": "基于已缓存的行情重新生成指标",
        "data.indicators.refresh_spinner": "正在刷新指标缓存……",
        "data.indicators.refresh_success": "✓ 指标缓存已更新",
        "data.indicators.refresh_no_source": "所选区间内缺少 {symbol} 的原始行情，请先下载或刷新行情数据。",
        "data.indicators.loading_spinner": "正在加载指标……",
        "data.indicators.load_no_data": "在所选日期范围内，{symbol} 暂无数据",
    "data.indicators.chart_title": "{symbol} · 价格与指标看板",
        "data.indicators.subplot.price": "价格",
        "data.indicators.subplot.rsi": "RSI",
        "data.indicators.subplot.macd": "MACD",
        "data.indicators.legend.close": "收盘价",
    "data.indicators.legend.candles": "K线",
        "data.indicators.legend.ema12": "EMA 12",
        "data.indicators.legend.bb_upper": "布林带上轨",
        "data.indicators.legend.bb_middle": "布林带中轨",
        "data.indicators.legend.bb_lower": "布林带下轨",
        "data.indicators.legend.macd_signal": "信号线",
        "data.indicators.legend.macd_histogram": "柱状图",
        "data.indicators.xaxis.date": "日期",
        "data.indicators.yaxis.price": "价格（美元）",
        "data.indicators.table_title": "指标明细",
        "data.indicators.table_page_size": "每页行数",
        "data.indicators.table_page": "页码",
        "data.indicators.table_stats": "第 {page} / {pages} 页，共 {total} 行",
        "data.indicators.download_button": "下载全量数据",
        "builder.title": "策略构建器",
        "builder.subtitle": "通过自然语言或结构化定义创建交易策略",
        "builder.tabs.define": "📝 定义策略",
        "builder.tabs.saved": "💾 已保存策略",
        
        # Define Strategy Tab
        "builder.define.header": "定义交易策略",
        "builder.define.description": "使用英文或中文描述你的交易策略，系统将自动转换为三种格式",
        "builder.define.sample": (
            "当 50 日均线上穿 200 日均线且 RSI 低于 70 时买入 AAPL。\n"
            "设置 8% 跟踪止损或 15% 止盈。\n"
            "测试区间：2019-01-01 至 2024-12-31。"
        ),
        "builder.define.nl_input_label": "策略描述",
        "builder.define.override_label": "覆盖默认标的（可选）",
        "builder.define.override_placeholder": "AAPL, MSFT, GOOGL",
        "builder.define.parse_button": "解析策略",
        "builder.define.spinner": "正在使用 LLM 解析策略……",
        "builder.define.success": "✓ 策略已成功解析为三种格式！",
        
        # Three formats section
        "builder.define.formats_header": "策略格式（均可编辑）",
        "builder.define.format_human": "📖 人类可读",
        "builder.define.format_json": "⚙️ JSON 定义",
        "builder.define.format_code": "💻 Backtrader 代码",
        
        # Human Readable
        "builder.define.human_description": "清晰、结构化的策略描述",
        "builder.define.human_label": "人类可读策略",
        "builder.define.update_human": "更新人类可读描述",
        
        # JSON Definition
        "builder.define.json_description": "结构化 JSON 策略定义（可编辑）",
        "builder.define.json_label": "策略 JSON",
        "builder.define.validate_json": "校验 JSON",
        "builder.define.validate_success": "✓ 策略 JSON 有效！",
        "builder.define.validate_error": "校验错误：{error}",
        "builder.define.compile_json": "编译为代码",
        "builder.define.compile_success": "✓ 代码编译并通过校验！",
        "builder.define.compile_warning": "代码已生成，但存在以下校验警告：",
        "builder.define.compile_error": "编译错误：{error}",
        
        # Backtrader Code
        "builder.define.code_description": "完整的 Backtrader 策略类（可编辑）",
        "builder.define.code_label": "Backtrader Python 代码",
        "builder.define.validate_code": "校验代码",
        "builder.define.code_valid": "✓ 代码有效！",
        "builder.define.code_warnings": "代码存在校验警告：",
        "builder.define.update_code": "更新代码",
        
        # Save section
        "builder.define.save_header": "保存策略",
        "builder.define.strategy_name": "策略名称",
        "builder.define.save_button": "💾 保存策略",
        "builder.define.save_success": "✓ 策略已保存！ID：{strategy_id}",
        "builder.define.save_error_no_data": "请先解析或定义一个策略",
        "builder.define.update_success": "✓ 更新成功！",
        
        # Saved Strategies Tab
        "builder.saved.header": "已保存策略",
        "builder.saved.id": "**ID：** {value}",
        "builder.saved.created": "**创建时间：** {value}",
        "builder.saved.format_human": "📖 人类可读",
        "builder.saved.format_json": "⚙️ JSON",
        "builder.saved.format_code": "💻 代码",
        "builder.saved.human_label": "人类可读描述",
        "builder.saved.json_label": "JSON 定义",
        "builder.saved.code_label": "Backtrader 代码",
        "builder.saved.validate_button": "校验",
        "builder.saved.validate_success": "✓ 有效！",
        "builder.saved.validate_error": "错误：{error}",
        "builder.saved.code_valid": "✓ 代码有效！",
        "builder.saved.code_warnings": "代码存在警告：",
        "builder.saved.update_button": "更新",
        "builder.saved.update_success": "✓ 已更新！",
        "builder.saved.update_error": "更新错误：{error}",
        "builder.saved.load_button": "加载到编辑器",
        "builder.saved.load_success": "策略已加载到编辑器！",
        "builder.saved.load_error": "加载错误：{error}",
        "builder.saved.delete_button": "删除",
        "builder.saved.delete_success": "策略已删除！",
        "builder.saved.empty": "目前还没有保存的策略，快去定义策略标签页创建一个吧！",
        
        # Settings Page
        "settings.title": "设置",
        "settings.subtitle": "配置应用设置和 LLM 集成",
        
        # LLM Configuration
        "settings.llm.header": "LLM 配置",
        "settings.llm.description": "配置 AI 模型用于自然语言策略解析。支持 OpenAI (GPT) 和 Anthropic (Claude)。",
        "settings.llm.add_config": "➕ 添加新 LLM 配置",
        "settings.llm.form_title": "LLM 提供商设置",
        "settings.llm.provider_label": "提供商",
        "settings.llm.provider_help": "选择 OpenAI (GPT 模型) 或 Anthropic (Claude 模型)",
        "settings.llm.model_label": "模型",
        "settings.llm.model_help": "选择要使用的具体模型版本",
        "settings.llm.api_key_label": "API 密钥",
        "settings.llm.api_key_help": "输入您的 API 密钥（将被安全存储并在界面中隐藏）",
        "settings.llm.api_key_required": "API 密钥是必需的",
        "settings.llm.save_button": "💾 保存配置",
        "settings.llm.save_success": "✓ LLM 配置已保存并激活！",
        "settings.llm.current_config": "当前活动配置",
        "settings.llm.config_updated": "最后更新：{date}",
        "settings.llm.delete_button": "🗑️ 删除",
        "settings.llm.delete_success": "配置删除成功",
        "settings.llm.all_configs": "所有已保存配置",
        "settings.llm.no_configs": "尚未保存 LLM 配置。在上方添加一个以启用 AI 驱动的策略解析。",
        "settings.llm.created": "创建时间",
        "settings.llm.status": "状态",
        "settings.llm.active": "活动",
        "settings.llm.inactive": "未激活",
        "settings.llm.activate_button": "✅ 激活",
        "settings.llm.activate_success": "配置激活成功",
        "settings.llm.test_header": "测试 LLM 连接",
        "settings.llm.test_input_label": "测试策略描述",
        "settings.llm.test_button": "🧪 测试连接",
        "settings.llm.test_spinner": "正在测试 LLM 连接……",
        "settings.llm.test_success": "✓ LLM 连接成功！",
        "settings.llm.test_show_results": "查看测试结果",
        "settings.llm.test_error": "测试失败：{error}",
        "settings.llm.test_no_config": "没有活动的 LLM 配置。在上方添加一个以进行测试。",
        
        # Strategy Builder LLM status
        "builder.define.llm_active": "LLM 已激活",
        "builder.define.llm_inactive": "⚠️ 未配置 LLM。使用基于规则的解析。在设置页面配置 LLM 以获得更好的结果。",
        
        "results.title": "回测结果",
        "results.subtitle": "分析回测绩效与核心指标",
        "results.info.no_completed": "暂无已完成的回测，请先在“回测”页面运行一次。",
        "results.section.select": "选择回测",
        "results.form.choose_backtest": "选择回测记录",
        "results.warning.no_metrics": "该回测暂未生成指标数据",
        "results.section.summary": "绩效概览",
        "results.metric.total_return": "总收益率",
        "results.metric.sharpe": "夏普比率",
        "results.metric.max_dd": "最大回撤",
        "results.metric.excess_return": "超额收益",
        "results.metric.cagr": "年化收益率",
        "results.metric.sortino": "索提诺比率",
        "results.metric.calmar": "卡尔玛比率",
        "results.tabs.equity": "📈 权益曲线",
        "results.tabs.metrics": "📊 指标",
        "results.tabs.trades": "📝 交易记录",
        "results.tabs.benchmark": "🎯 基准对比",
        "results.tabs.details": "📋 详情",
        "results.tabs.equity_header": "权益走势",
        "results.tabs.metrics_header": "绩效指标",
        "results.tabs.trades_header": "成交明细",
        "results.tabs.benchmark_header": "基准比较",
        "results.chart.equity_trend": "权益走势",
        "results.chart.daily_returns": "每日盈亏",
        "results.caption.sessions": "盈利天数：{gains} | 亏损天数：{losses}",
        "results.section.top_gains": "最高收益日",
        "results.section.top_losses": "最大亏损日",
        "results.info.no_gain_sessions": "尚无盈利日记录",
        "results.info.no_loss_sessions": "尚无亏损日记录",
        "results.info.no_equity": "当前回测尚未记录权益曲线数据。",
        "results.table.metric": "指标",
        "results.table.value": "数值",
        "results.text.benchmarks": "**基准：** {benchmarks}",
        "results.warning.no_benchmark_data": "未找到基准数据，请先在“数据”页面下载相应行情。",
        "results.info.no_benchmarks": "该回测未选择基准",
        "results.benchmark.symbol": "代码",
        "results.benchmark.outperformance": "策略超额收益",
        "results.section.configuration": "回测配置",
        "results.config.backtest_id": "**回测 ID：** {value}",
        "results.config.strategy": "**策略：** {value}",
        "results.config.status": "**状态：** {value}",
        "results.config.created": "**创建时间：** {value}",
        "results.config.universe": "**交易标的：** {value}",
        "results.config.start": "**开始日期：** {value}",
        "results.config.end": "**结束日期：** {value}",
        "results.config.initial_cash": "**初始资金：** {value}",
        "results.section.strategy_definition": "策略定义",
        "results.section.export": "导出结果",
        "results.button.export_json": "导出 JSON",
        "results.button.download_json": "下载 JSON",
        "results.button.export_metrics": "导出指标 CSV",
        "results.button.download_csv": "下载 CSV",
        "results.info.export_html": "HTML 导出功能即将上线",
        "results.gain_loss.date": "日期",
        "results.gain_loss.return": "收益率（%）",
        "results.gain_loss.value": "组合市值（美元）",
        "results.gain_loss.pnl": "累计盈亏（美元）",
        "results.trades.metric.trades": "交易笔数",
        "results.trades.metric.realized": "已实现盈亏",
        "results.trades.metric.win_rate": "胜率",
        "results.trades.metric.avg_allocation": "平均仓位比例",
        "results.trades.caption.avg_hold": "平均持仓时长：{bars} 根K线",
        "results.trades.no_data": "本次回测没有产生任何交易。",
        "results.trades.column.timestamp": "日期",
        "results.trades.column.symbol": "标的",
        "results.trades.column.action": "方向",
        "results.trades.column.size": "数量",
        "results.trades.column.price": "价格",
        "results.trades.column.value": "成交金额",
        "results.trades.column.commission": "佣金",
        "results.trades.column.pnl": "盈亏",
        "results.trades.column.pnl_pct": "盈亏百分比",
        "results.trades.column.alloc_pct": "仓位比例",
        "results.trades.column.holding": "持有bar数",
        "results.trades.column.reason": "触发原因",
        "app.nav.home": "🏠 首页",
        "app.nav.data": "📦 数据",
        "app.nav.builder": "🛠️ 策略构建",
        "app.nav.backtest": "🚀 回测",
    "app.nav.results": "📊 结果",
    "app.nav.settings": "⚙️ 设置",
    },
}

def _init_language_state():
    import streamlit as st

    if "language" not in st.session_state:
        st.session_state["language"] = _DEFAULT_LANGUAGE


def get_language() -> str:
    """Return the current UI language code."""
    import streamlit as st

    _init_language_state()
    return str(st.session_state.get("language", _DEFAULT_LANGUAGE))


def set_language(lang: str) -> None:
    """Set the current UI language code."""
    import streamlit as st

    _init_language_state()
    codes = {code for code, _ in _LANGUAGE_CHOICES}
    st.session_state["language"] = lang if lang in codes else _DEFAULT_LANGUAGE


def t(key: str, **kwargs) -> str:
    """Translate a string by key with optional formatting."""
    language = get_language()
    template = TRANSLATIONS.get(language, {}).get(key)

    if template is None:
        template = TRANSLATIONS.get(_DEFAULT_LANGUAGE, {}).get(key, key)

    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def use_language_selector() -> str:
    """Render a sidebar language selector and return the selected code."""
    import streamlit as st

    _init_language_state()
    label = t("common.language_label")
    options = [label for _, label in _LANGUAGE_CHOICES]
    current_code = get_language()
    code_to_label = {code: label for code, label in _LANGUAGE_CHOICES}
    label_to_code = {label: code for code, label in _LANGUAGE_CHOICES}
    current_label = code_to_label.get(current_code, options[0])
    try:
        current_index = options.index(current_label)
    except ValueError:
        current_index = 0

    selected_label = st.sidebar.selectbox(
        label,
        options,
        index=current_index,
        key=_LANGUAGE_WIDGET_KEY,
    )

    selected_code = label_to_code.get(selected_label, _DEFAULT_LANGUAGE)
    if selected_code != current_code:
        set_language(selected_code)

    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()
    st.sidebar.markdown(t("app.sidebar.navigation_heading"))
    st.sidebar.page_link("app.py", label=t("app.nav.home"))
    st.sidebar.page_link("pages/1_Data.py", label=t("app.nav.data"))
    st.sidebar.page_link("pages/2_Strategy_Builder.py", label=t("app.nav.builder"))
    st.sidebar.page_link("pages/3_Backtest.py", label=t("app.nav.backtest"))
    st.sidebar.page_link("pages/4_Results.py", label=t("app.nav.results"))
    st.sidebar.page_link("pages/5_Settings.py", label=t("app.nav.settings"))
    st.sidebar.divider()

    return get_language()
