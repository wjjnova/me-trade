"""
Backtest execution page.
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from src.backtest import BacktestEngine
from src.db import get_db
from src.data import StockDataManager
import uuid
import config


def show():
    """Display the backtest page."""
    st.title("Run Backtest")
    st.write("Execute strategies and analyze results")
    
    # Initialize components
    engine = BacktestEngine()
    db = get_db()
    stock_mgr = StockDataManager()
    
    # Load saved strategies
    strategies = db.fetchall("SELECT id, name FROM strategies ORDER BY created_at DESC")
    
    if not strategies:
        st.warning("No strategies available. Create one in the Strategy Builder first!")
        return
    
    # Strategy selection
    st.subheader("1. Select Strategy")
    
    strategy_options = {f"{s['name']} ({s['id']})": s['id'] for s in strategies}
    selected_strategy = st.selectbox(
        "Choose a strategy",
        options=list(strategy_options.keys())
    )
    
    strategy_id = strategy_options[selected_strategy]
    
    # Load strategy details
    strategy_rec = db.fetchone(
        "SELECT json FROM strategies WHERE id = ?",
        (strategy_id,)
    )
    strategy_data = json.loads(strategy_rec['json'])
    
    # Load code
    code_rec = db.fetchone(
        "SELECT id, code FROM codes WHERE strategy_id = ? ORDER BY created_at DESC LIMIT 1",
        (strategy_id,)
    )
    
    if not code_rec:
        st.error("No code found for this strategy!")
        return
    
    code_id = code_rec['id']
    
    # Show strategy summary
    with st.expander("Strategy Details"):
        st.json(strategy_data)
    
    # Backtest configuration
    st.subheader("2. Configure Backtest")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Universe
        default_universe = strategy_data.get('universe', ['AAPL'])
        universe_input = st.text_input(
            "Trading Universe (symbols)",
            value=", ".join(default_universe)
        )
        universe = [s.strip().upper() for s in universe_input.split(",")]
        
        # Check available symbols
        available_symbols = stock_mgr.get_available_symbols()
        missing_symbols = [s for s in universe if s not in available_symbols]
        
        if missing_symbols:
            st.warning(f"Missing data for: {', '.join(missing_symbols)}")
            st.info("Download data in the Data page first!")
        
        # Time range
        default_start = strategy_data.get('timeframe', {}).get('start', '2019-01-01')
        default_end = strategy_data.get('timeframe', {}).get('end', '2024-12-31')
        
        start_date = st.date_input(
            "Start Date",
            value=datetime.strptime(default_start, "%Y-%m-%d").date()
        )
        
        end_date = st.date_input(
            "End Date",
            value=datetime.strptime(default_end, "%Y-%m-%d").date()
        )
    
    with col2:
        # Initial capital
        initial_cash = st.number_input(
            "Initial Capital ($)",
            min_value=1000.0,
            value=config.DEFAULT_INITIAL_CASH,
            step=10000.0
        )
        
        # Commission
        commission = st.number_input(
            "Commission per share ($)",
            min_value=0.0,
            value=config.DEFAULT_COMMISSION,
            step=0.001,
            format="%.4f"
        )
        
        # Slippage
        slippage_bps = st.number_input(
            "Slippage (basis points)",
            min_value=0.0,
            value=float(config.DEFAULT_SLIPPAGE_BPS),
            step=1.0
        )
    
    # Benchmarks
    st.subheader("3. Select Benchmarks")
    
    benchmark_options = config.BENCHMARK_SYMBOLS
    selected_benchmarks = st.multiselect(
        "Compare against",
        options=benchmark_options,
        default=["VOO"]
    )
    
    # Run backtest
    st.divider()
    
    if st.button("🚀 Run Backtest", type="primary", disabled=bool(missing_symbols)):
        
        # Create backtest ID
        bt_id = f"bt_{uuid.uuid4().hex[:8]}"
        
        # Save backtest record
        db.execute(
            """INSERT INTO backtests 
               (id, strategy_id, code_id, universe, start, end, initial_cash, benchmarks, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (bt_id, strategy_id, code_id, 
             json.dumps(universe),
             start_date.strftime("%Y-%m-%d"),
             end_date.strftime("%Y-%m-%d"),
             initial_cash,
             json.dumps(selected_benchmarks),
             'running',
             datetime.now().isoformat())
        )
        
        with st.spinner("Running backtest... This may take a moment."):
            try:
                # Run backtest
                results = engine.run_backtest(
                    strategy_code=code_rec['code'],
                    universe=universe,
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    initial_cash=initial_cash,
                    commission=commission,
                    slippage_bps=slippage_bps
                )
                
                if results['success']:
                    # Update backtest status
                    db.execute(
                        "UPDATE backtests SET status = ? WHERE id = ?",
                        ('completed', bt_id)
                    )
                    
                    # Save metrics
                    analyzers = results.get('analyzers', {})
                    returns_data = analyzers.get('returns', {})
                    sharpe_data = analyzers.get('sharpe', {})
                    dd_data = analyzers.get('drawdown', {})
                    
                    db.execute(
                        """INSERT INTO metrics_run 
                           (bt_id, tot_return, cagr, max_dd, sharpe, sortino, calmar, excess_return, benchmarks)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (bt_id,
                         results['total_return'],
                         None,  # Would calculate from returns
                         dd_data.get('max_drawdown_pct', 0),
                         sharpe_data.get('sharpe_ratio', 0),
                         None,  # Sortino not in basic analyzers
                         None,  # Calmar not in basic analyzers
                         None,  # Would compare to benchmark
                         json.dumps({}))
                    )
                    
                    st.success(f"✓ Backtest completed! ID: {bt_id}")
                    
                    # Display results
                    st.subheader("Results Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Starting Value",
                            f"${results['starting_value']:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "Ending Value",
                            f"${results['ending_value']:,.2f}"
                        )
                    
                    with col3:
                        total_return_pct = results['total_return'] * 100
                        st.metric(
                            "Total Return",
                            f"{total_return_pct:.2f}%",
                            delta=f"{total_return_pct:.2f}%"
                        )
                    
                    with col4:
                        trades_data = analyzers.get('trades', {})
                        total_trades = trades_data.get('total_trades', 0)
                        st.metric(
                            "Total Trades",
                            total_trades
                        )
                    
                    # Store in session state for results page
                    st.session_state['last_backtest_id'] = bt_id
                    
                    st.info("View detailed results in the Results page")
                    
                else:
                    # Update backtest status
                    db.execute(
                        "UPDATE backtests SET status = ? WHERE id = ?",
                        ('failed', bt_id)
                    )
                    st.error(f"Backtest failed: {results.get('error', 'Unknown error')}")
            
            except Exception as e:
                db.execute(
                    "UPDATE backtests SET status = ? WHERE id = ?",
                    ('failed', bt_id)
                )
                st.error(f"Backtest error: {str(e)}")
    
    # Show recent backtests
    st.divider()
    st.subheader("Recent Backtests")
    
    recent = db.fetchall(
        """SELECT b.id, s.name, b.status, b.created_at, m.tot_return
           FROM backtests b
           JOIN strategies s ON b.strategy_id = s.id
           LEFT JOIN metrics_run m ON b.id = m.bt_id
           ORDER BY b.created_at DESC
           LIMIT 10"""
    )
    
    if recent:
        for bt in recent:
            status_icon = {
                'completed': '✓',
                'running': '⏳',
                'failed': '✗',
                'pending': '○'
            }.get(bt['status'], '?')
            
            return_str = f"{bt['tot_return']*100:.2f}%" if bt['tot_return'] is not None else "N/A"
            
            st.write(f"{status_icon} **{bt['name']}** - {bt['id']} - Return: {return_str} - {bt['created_at'][:10]}")
    else:
        st.info("No backtests run yet")


if __name__ == "__main__":
    show()
