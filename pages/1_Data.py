"""
Data management page for downloading and viewing stock/option data.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.data import StockDataManager, OptionsDataManager, BenchmarkManager
import config


def show():
    """Display the data management page."""
    st.title("Data Management")
    st.write("Download and manage stock and options data")
    
    # Initialize managers
    stock_mgr = StockDataManager()
    options_mgr = OptionsDataManager()
    benchmark_mgr = BenchmarkManager()
    
    # Tabs for different data types
    tab1, tab2, tab3 = st.tabs(["📈 Stocks", "📊 Options", "🎯 Benchmarks"])
    
    # === STOCKS TAB ===
    with tab1:
        st.header("Stock Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Download Stock Data")
            
            # Symbol selection
            default_symbols = config.DEFAULT_SYMBOLS
            symbols_input = st.text_area(
                "Symbols (comma-separated)",
                value=", ".join(default_symbols),
                help="Enter stock ticker symbols separated by commas"
            )
            
            # Parse symbols
            symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
            
            # Date range
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=5*365)
                )
            with col_end:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now()
                )
            
            # Interval
            interval = st.selectbox(
                "Interval",
                options=["1d", "1h", "15m", "5m"],
                index=0
            )
            
            # Download button
            if st.button("Download Stock Data", type="primary"):
                with st.spinner("Downloading data..."):
                    results = stock_mgr.download_stocks(
                        symbols=symbols,
                        start=start_date.strftime("%Y-%m-%d"),
                        end=end_date.strftime("%Y-%m-%d"),
                        interval=interval
                    )
                    
                    # Show results
                    if results["success"]:
                        st.success(f"✓ Downloaded {results['total_rows']} rows for {len(results['success'])} symbols")
                        for item in results["success"]:
                            st.write(f"- {item['symbol']}: {item['rows']} rows")
                    
                    if results["failed"]:
                        st.warning("Some downloads failed:")
                        for item in results["failed"]:
                            st.write(f"- {item['symbol']}: {item['error']}")
        
        with col2:
            st.subheader("Cached Symbols")
            
            cached_symbols = stock_mgr.get_available_symbols()
            if cached_symbols:
                for symbol in cached_symbols:
                    date_range = stock_mgr.get_date_range(symbol, interval)
                    if date_range:
                        with st.expander(symbol):
                            st.write(f"**Rows:** {date_range['count']}")
                            st.write(f"**From:** {date_range['min_date']}")
                            st.write(f"**To:** {date_range['max_date']}")
            else:
                st.info("No cached data yet")
        
        # CSV Upload
        st.divider()
        st.subheader("Upload Custom Data")
        
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=["csv"],
            help="CSV must have columns: date, open, high, low, close, volume"
        )
        
        if uploaded_file:
            col_symbol, col_upload = st.columns([1, 1])
            with col_symbol:
                upload_symbol = st.text_input("Symbol for uploaded data", value="CUSTOM")
            
            with col_upload:
                if st.button("Process Upload"):
                    # Save file temporarily
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    result = stock_mgr.upload_csv(tmp_path, upload_symbol.upper())
                    os.unlink(tmp_path)
                    
                    if result.get("success"):
                        st.success(f"✓ Uploaded {result['rows']} rows for {result['symbol']}")
                    else:
                        st.error(f"Upload failed: {result.get('error')}")
    
    # === OPTIONS TAB ===
    with tab2:
        st.header("Options Chain Data")
        
        st.subheader("Download Options Chains")
        
        options_symbols_input = st.text_input(
            "Symbols for options",
            value="AAPL, MSFT, TSLA",
            help="Enter symbols to download option chains"
        )
        
        options_symbols = [s.strip().upper() for s in options_symbols_input.split(",") if s.strip()]
        
        if st.button("Download Options Data", type="primary"):
            with st.spinner("Downloading option chains..."):
                results = options_mgr.download_options(options_symbols)
                
                if results["success"]:
                    st.success(f"✓ Downloaded {results['total_rows']} option contracts")
                    for item in results["success"]:
                        st.write(f"- {item['symbol']}: {item['expirations']} expirations, {item['rows']} contracts")
                
                if results["failed"]:
                    st.warning("Some downloads failed:")
                    for item in results["failed"]:
                        st.write(f"- {item['symbol']}: {item['error']}")
        
        # View cached options
        st.divider()
        st.subheader("View Cached Options")
        
        view_symbol = st.selectbox("Select symbol", options=stock_mgr.get_available_symbols())
        
        if view_symbol:
            expirations = options_mgr.get_available_expirations(view_symbol)
            if expirations:
                st.write(f"**Available expirations:** {len(expirations)}")
                selected_exp = st.selectbox("Expiration", options=expirations)
                
                if selected_exp:
                    chain = options_mgr.get_option_chain(view_symbol, expiration=selected_exp)
                    if not chain.empty:
                        st.dataframe(chain[['strike', 'right', 'bid', 'ask', 'volume', 'open_interest']])
            else:
                st.info("No option chain data available for this symbol")
    
    # === BENCHMARKS TAB ===
    with tab3:
        st.header("Benchmark Data")
        
        st.write("Download benchmark indices for comparison")
        
        benchmark_symbols = config.BENCHMARK_SYMBOLS
        st.write(f"**Benchmarks:** {', '.join(benchmark_symbols)}")
        
        col_start, col_end = st.columns(2)
        with col_start:
            bench_start = st.date_input(
                "Benchmark Start Date",
                value=datetime.now() - timedelta(days=5*365),
                key="bench_start"
            )
        with col_end:
            bench_end = st.date_input(
                "Benchmark End Date",
                value=datetime.now(),
                key="bench_end"
            )
        
        if st.button("Download Benchmarks", type="primary"):
            with st.spinner("Downloading benchmark data..."):
                results = benchmark_mgr.download_benchmarks(
                    start=bench_start.strftime("%Y-%m-%d"),
                    end=bench_end.strftime("%Y-%m-%d")
                )
                
                if results["success"]:
                    st.success(f"✓ Downloaded benchmark data")
                    for item in results["success"]:
                        st.write(f"- {item['symbol']}: {item['rows']} rows")
                
                if results["failed"]:
                    st.warning("Some downloads failed:")
                    for item in results["failed"]:
                        st.write(f"- {item['symbol']}: {item['error']}")
        
        # Show cached benchmark data
        st.divider()
        st.subheader("Cached Benchmark Data")
        
        for symbol in benchmark_symbols:
            date_range = stock_mgr.get_date_range(symbol)
            if date_range:
                with st.expander(symbol):
                    st.write(f"**Rows:** {date_range['count']}")
                    st.write(f"**From:** {date_range['min_date']}")
                    st.write(f"**To:** {date_range['max_date']}")


if __name__ == "__main__":
    show()
