"""
Me-Trade: Natural Language-Driven Backtesting App
Main Streamlit application entry point
"""
import streamlit as st
from src.db import get_db
import config


# Page configuration
st.set_page_config(
    page_title="Me-Trade",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on startup
@st.cache_resource
def init_database():
    """Initialize database schema."""
    db = get_db()
    return db

# Initialize
db = init_database()

# Main page
st.title("📈 Me-Trade")
st.subheader("Natural Language-Driven Backtesting for U.S. Stocks & Options")

st.markdown("""
Welcome to **Me-Trade**, a lightweight application for testing trading strategies using natural language.

### 🚀 Quick Start

1. **Data** - Download stock and option data from Yahoo Finance
2. **Strategy Builder** - Describe your strategy in plain English or structured JSON
3. **Backtest** - Run your strategy against historical data
4. **Results** - Analyze performance metrics and compare to benchmarks

### 📊 Features

- **Natural Language Strategy Definition** - Describe strategies in plain English
- **Multiple Data Sources** - Yahoo Finance for stocks and options
- **Comprehensive Backtesting** - Powered by Backtrader
- **Benchmark Comparison** - Compare against VOO, SPY, QQQ
- **Risk Metrics** - Sharpe, Sortino, Calmar ratios, max drawdown
- **Local Storage** - SQLite database for data and results

### 🎯 Supported Symbols (Initial Focus)

{symbols}

### 📖 How to Use

Navigate using the sidebar to access different sections:

- **Data**: Download and manage market data
- **Strategy Builder**: Create and edit trading strategies  
- **Backtest**: Execute strategies and view basic results
- **Results**: Detailed analysis and metrics visualization

### ⚙️ Configuration

- **Initial Capital**: ${initial_cash:,.0f}
- **Commission**: ${commission:.4f} per share
- **Slippage**: {slippage_bps} basis points

---

**Get Started**: Use the sidebar to navigate to the Data page and download some market data!
""".format(
    symbols=", ".join(config.DEFAULT_SYMBOLS),
    initial_cash=config.DEFAULT_INITIAL_CASH,
    commission=config.DEFAULT_COMMISSION,
    slippage_bps=config.DEFAULT_SLIPPAGE_BPS
))

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Database Info")
    
    # Show cached data stats
    try:
        stocks_count = db.fetchone("SELECT COUNT(DISTINCT symbol) as count FROM equities_ohlcv", ())
        if stocks_count:
            st.metric("Cached Symbols", stocks_count.get('count', 0))
        
        strategies_count = db.fetchone("SELECT COUNT(*) as count FROM strategies", ())
        if strategies_count:
            st.metric("Saved Strategies", strategies_count.get('count', 0))
        
        backtests_count = db.fetchone("SELECT COUNT(*) as count FROM backtests", ())
        if backtests_count:
            st.metric("Total Backtests", backtests_count.get('count', 0))
    except:
        pass
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Version**: 0.1.0 (MVP)
    
    **Tech Stack**:
    - Streamlit (UI)
    - Backtrader (Backtesting)
    - yfinance (Data)
    - SQLite (Storage)
    - Plotly (Charts)
    
    **Source**: [GitHub](#)
    """)
