"""
Me Trade: Natural Language-Driven Backtesting App
Main Streamlit application entry point
"""
import streamlit as st

from src import config
from src.db import get_db
from src.ui import t, use_language_selector


# Page configuration
st.set_page_config(
    page_title="Me Trade",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

use_language_selector()


@st.cache_resource
def init_database():
    """Initialize database schema."""
    db = get_db()
    return db


db = init_database()

# Main page
st.title(t("app.title"))
st.subheader(t("app.subtitle"))

st.markdown(
    t(
        "app.home.content",
        symbols=", ".join(config.DEFAULT_SYMBOLS),
        initial_cash=config.DEFAULT_INITIAL_CASH,
        commission=config.DEFAULT_COMMISSION,
        slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
    )
)

# Sidebar info
with st.sidebar:
    st.markdown(t("app.sidebar.database_info_heading"))
    
    # Show cached data stats
    try:
        stocks_count = db.fetchone("SELECT COUNT(DISTINCT symbol) as count FROM equities_ohlcv", ())
        if stocks_count:
            st.metric(t("app.sidebar.cached_symbols"), stocks_count.get('count', 0))
        
        strategies_count = db.fetchone("SELECT COUNT(*) as count FROM strategies", ())
        if strategies_count:
            st.metric(t("app.sidebar.saved_strategies"), strategies_count.get('count', 0))
        
        backtests_count = db.fetchone("SELECT COUNT(*) as count FROM backtests", ())
        if backtests_count:
            st.metric(t("app.sidebar.total_backtests"), backtests_count.get('count', 0))
    except:
        pass
    
    st.divider()
    st.markdown(t("app.sidebar.about_heading"))
    st.markdown(t("app.sidebar.about_content"))
