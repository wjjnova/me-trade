"""
Results visualization page.
"""
import streamlit as st
import pandas as pd
import json
from src.db import get_db
from src.visualization import ChartGenerator
from src.data import StockDataManager
from src.backtest import MetricsCalculator


def show():
    """Display the results page."""
    st.title("Backtest Results")
    st.write("Analyze backtest performance and metrics")
    
    # Initialize components
    db = get_db()
    chart_gen = ChartGenerator()
    metrics_calc = MetricsCalculator()
    stock_mgr = StockDataManager()
    
    # Get all completed backtests
    backtests = db.fetchall(
        """SELECT b.id, s.name as strategy_name, b.status, b.created_at, b.start, b.end,
                  b.universe, b.benchmarks
           FROM backtests b
           JOIN strategies s ON b.strategy_id = s.id
           WHERE b.status = 'completed'
           ORDER BY b.created_at DESC"""
    )
    
    if not backtests:
        st.info("No completed backtests yet. Run a backtest in the Backtest page!")
        return
    
    # Select backtest
    st.subheader("Select Backtest")
    
    # Check if we have a recent backtest from session state
    default_index = 0
    if 'last_backtest_id' in st.session_state:
        for i, bt in enumerate(backtests):
            if bt['id'] == st.session_state['last_backtest_id']:
                default_index = i
                break
    
    backtest_options = {
        f"{bt['strategy_name']} - {bt['created_at'][:10]} ({bt['id']})": bt['id'] 
        for bt in backtests
    }
    
    selected = st.selectbox(
        "Choose backtest",
        options=list(backtest_options.keys()),
        index=default_index
    )
    
    bt_id = backtest_options[selected]
    
    # Load backtest details
    backtest = db.fetchone(
        """SELECT b.*, s.name as strategy_name, s.json as strategy_json
           FROM backtests b
           JOIN strategies s ON b.strategy_id = s.id
           WHERE b.id = ?""",
        (bt_id,)
    )
    
    # Load metrics
    metrics = db.fetchone(
        "SELECT * FROM metrics_run WHERE bt_id = ?",
        (bt_id,)
    )
    
    if not metrics:
        st.warning("No metrics available for this backtest")
        return
    
    # Display summary metrics
    st.subheader("Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_return = metrics.get('tot_return', 0)
        st.metric(
            "Total Return",
            f"{total_return * 100:.2f}%",
            delta=f"{total_return * 100:.2f}%"
        )
    
    with col2:
        sharpe = metrics.get('sharpe', 0)
        st.metric(
            "Sharpe Ratio",
            f"{sharpe:.3f}"
        )
    
    with col3:
        max_dd = metrics.get('max_dd', 0)
        st.metric(
            "Max Drawdown",
            f"{max_dd * 100:.2f}%",
            delta=f"{max_dd * 100:.2f}%",
            delta_color="inverse"
        )
    
    with col4:
        if metrics.get('excess_return'):
            excess = metrics['excess_return']
            st.metric(
                "Excess Return",
                f"{excess * 100:.2f}%",
                delta=f"{excess * 100:.2f}%"
            )
        else:
            st.metric("CAGR", "N/A")
    
    # Tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Equity Curve", 
        "📊 Metrics", 
        "🎯 Benchmark Comparison",
        "📋 Details"
    ])
    
    # === EQUITY CURVE TAB ===
    with tab1:
        st.subheader("Equity Curve")
        
        # For a real implementation, we would need to store equity curve data
        # For now, show placeholder
        st.info("Equity curve visualization requires storing time-series portfolio values during backtest execution.")
        st.write("This would be implemented by tracking cerebro broker value at each step and saving to a CSV/database.")
        
        # Example of how it would work:
        st.code("""
# During backtest, track portfolio value:
equity_curve = []
for date, value in zip(dates, portfolio_values):
    equity_curve.append({'date': date, 'value': value})

# Save to CSV
pd.DataFrame(equity_curve).to_csv(f'files/{bt_id}_equity.csv')
""", language="python")
    
    # === METRICS TAB ===
    with tab2:
        st.subheader("Performance Metrics")
        
        metrics_data = {
            'Total Return': f"{metrics.get('tot_return', 0) * 100:.2f}%",
            'CAGR': f"{metrics.get('cagr', 0) * 100:.2f}%" if metrics.get('cagr') else "N/A",
            'Max Drawdown': f"{metrics.get('max_dd', 0) * 100:.2f}%",
            'Sharpe Ratio': f"{metrics.get('sharpe', 0):.3f}",
            'Sortino Ratio': f"{metrics.get('sortino', 0):.3f}" if metrics.get('sortino') else "N/A",
            'Calmar Ratio': f"{metrics.get('calmar', 0):.3f}" if metrics.get('calmar') else "N/A",
        }
        
        if metrics.get('excess_return'):
            metrics_data['Excess Return'] = f"{metrics['excess_return'] * 100:.2f}%"
        
        # Display as table
        df_metrics = pd.DataFrame([metrics_data]).T
        df_metrics.columns = ['Value']
        st.dataframe(df_metrics, use_container_width=True)
    
    # === BENCHMARK COMPARISON TAB ===
    with tab3:
        st.subheader("Benchmark Comparison")
        
        benchmarks = json.loads(backtest['benchmarks']) if backtest.get('benchmarks') else []
        
        if benchmarks:
            st.write(f"**Benchmarks:** {', '.join(benchmarks)}")
            
            # For each benchmark, calculate metrics
            start_date = backtest['start']
            end_date = backtest['end']
            
            comparison_data = []
            
            for benchmark in benchmarks:
                bench_data = stock_mgr.get_cached_data(benchmark, start_date, end_date)
                
                if not bench_data.empty:
                    # Calculate benchmark return
                    start_price = bench_data['close'].iloc[0]
                    end_price = bench_data['close'].iloc[-1]
                    bench_return = (end_price - start_price) / start_price
                    
                    comparison_data.append({
                        'Symbol': benchmark,
                        'Total Return': f"{bench_return * 100:.2f}%",
                        'Strategy Outperformance': f"{(total_return - bench_return) * 100:.2f}%"
                    })
            
            if comparison_data:
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)
            else:
                st.warning("Benchmark data not available. Download benchmark data in the Data page.")
        else:
            st.info("No benchmarks selected for this backtest")
    
    # === DETAILS TAB ===
    with tab4:
        st.subheader("Backtest Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Backtest ID:**", backtest['id'])
            st.write("**Strategy:**", backtest['strategy_name'])
            st.write("**Status:**", backtest['status'])
            st.write("**Created:**", backtest['created_at'])
        
        with col2:
            universe = json.loads(backtest['universe'])
            st.write("**Universe:**", ", ".join(universe))
            st.write("**Start Date:**", backtest['start'])
            st.write("**End Date:**", backtest['end'])
            st.write("**Initial Cash:**", f"${backtest.get('initial_cash', 0):,.2f}")
        
        st.divider()
        st.subheader("Strategy Definition")
        
        strategy_json = json.loads(backtest['strategy_json'])
        st.json(strategy_json)
        
        # Export options
        st.divider()
        st.subheader("Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export as JSON"):
                export_data = {
                    'backtest': dict(backtest),
                    'metrics': dict(metrics) if metrics else {},
                    'strategy': strategy_json
                }
                st.download_button(
                    "Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"backtest_{bt_id}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("Export Metrics as CSV"):
                df_metrics = pd.DataFrame([metrics]) if metrics else pd.DataFrame()
                st.download_button(
                    "Download CSV",
                    data=df_metrics.to_csv(index=False),
                    file_name=f"metrics_{bt_id}.csv",
                    mime="text/csv"
                )
        
        with col3:
            st.info("HTML export coming soon")


if __name__ == "__main__":
    show()
