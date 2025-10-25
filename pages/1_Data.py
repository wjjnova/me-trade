"""
Data management page for downloading and viewing stock/option data.
"""
import math
from typing import Any

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from src import config
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.download_sp500_data import download_sp500_data

from src.data import IndicatorStorage, OptionsDataManager, StockDataManager
from src.ui import t, use_language_selector


DEFAULT_INTERVAL = "1d"
FAVORITE_DEFAULTS = [
    "TSLA",
    "MSFT",
    "PATH",
    "GOOGL",
    "NVDA",
    "AMZN",
    "VOO",
    "AAPL",
    "BABA",
    "META",
]

OPTION_IMPORT_DIR = Path("data/option")


def _ensure_favorites() -> list[str]:
    """Ensure favorite symbols exist in session state and stay normalized."""
    favorites = st.session_state.get("favorite_symbols")
    if favorites is None:
        favorites = FAVORITE_DEFAULTS.copy()
    normalized = []
    seen = set()
    for symbol in favorites:
        clean = symbol.strip().upper()
        if clean and clean not in seen:
            normalized.append(clean)
            seen.add(clean)
    st.session_state["favorite_symbols"] = normalized
    return normalized


def _merge_favorites_with_options(options: list[str]) -> list[str]:
    """Return a list with favorites first, followed by remaining unique options."""
    favorites = _ensure_favorites()
    merged: list[str] = []
    seen = set()

    for symbol in favorites:
        if symbol not in seen:
            merged.append(symbol)
            seen.add(symbol)

    for symbol in options:
        upper = symbol.strip().upper()
        if upper not in seen:
            merged.append(upper)
            seen.add(upper)

    return merged


def _render_favorite_manager() -> None:
    """Render UI for managing favorite symbols."""
    favorites = _ensure_favorites()

    expander_label = t("data.favorites.header")
    if favorites:
        expander_label = f"{expander_label} ({len(favorites)})"

    with st.expander(expander_label, expanded=False):
        st.caption(t("data.favorites.help"))

        if favorites:
            st.write(t("data.favorites.list", symbols=", ".join(favorites)))
        else:
            st.write(t("data.favorites.list_empty"))

        col_add, col_remove = st.columns([2, 2])

        with col_add:
            add_input = st.text_input(
                t("data.favorites.add_label"),
                key="favorites_add_input",
                placeholder=t("data.favorites.add_placeholder"),
            )
            if st.button(t("data.favorites.add_button"), key="favorites_add_button"):
                symbol = add_input.strip().upper()
                if not symbol:
                    st.warning(t("data.favorites.add_invalid"))
                elif symbol in favorites:
                    st.info(t("data.favorites.add_exists", symbol=symbol))
                else:
                    favorites.append(symbol)
                    st.session_state["favorite_symbols"] = favorites
                    st.session_state["favorites_add_input"] = ""
                    st.success(t("data.favorites.add_success", symbol=symbol))
                    st.experimental_rerun()

        with col_remove:
            if favorites:
                remove_symbol = st.selectbox(
                    t("data.favorites.remove_label"),
                    options=favorites,
                    key="favorites_remove_select",
                )
                if st.button(t("data.favorites.remove_button"), key="favorites_remove_button"):
                    updated = [sym for sym in favorites if sym != remove_symbol]
                    st.session_state["favorite_symbols"] = updated
                    st.success(t("data.favorites.remove_success", symbol=remove_symbol))
                    st.experimental_rerun()
            else:
                st.caption(t("data.favorites.remove_empty"))


def show():
    """Display the data management page."""
    use_language_selector()

    st.title(t("data.title"))
    st.write(t("data.subtitle"))
    
    # Initialize managers
    stock_mgr = StockDataManager()
    options_mgr = OptionsDataManager()

    def _sync_cached_selection() -> None:
        symbol = st.session_state.get("cached_symbol_select")
        if symbol:
            st.session_state["viewer_symbol"] = symbol
    
    # Tabs for different data types
    tab1, tab2, tab3 = st.tabs(
        [
            t("data.tabs.stocks"),
            t("data.tabs.options"),
            t("data.tabs.indicators"),
        ]
    )
    
    # === STOCKS TAB ===
    with tab1:
        _render_favorite_manager()
        st.divider()
        st.header(t("data.stocks.header"))

        history_start = datetime(2019, 1, 1)
        history_start_str = history_start.strftime("%Y-%m-%d")
        history_end_str = datetime.now().strftime("%Y-%m-%d")
        st.caption(
            t(
                "data.stocks.fixed_window_note",
                start=history_start_str,
                end=history_end_str,
            )
        )

        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(t("data.stocks.download_title"))
            
            # Symbol selection
            default_symbols = config.DEFAULT_SYMBOLS
            symbols_input = st.text_area(
                t("data.stocks.symbols_label"),
                value=", ".join(default_symbols),
                help=t("data.stocks.symbols_help")
            )
            
            # Parse symbols
            symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

            if symbols:
                cached_max_dates = []
                for sym in symbols:
                    coverage = stock_mgr.get_date_range(sym, DEFAULT_INTERVAL)
                    if coverage and coverage.get("max_date"):
                        cached_max_dates.append(coverage["max_date"])

                if cached_max_dates:
                    st.caption(
                        t(
                            "data.stocks.last_cached_info",
                            date=max(cached_max_dates),
                            count=len(cached_max_dates),
                            total=len(symbols),
                        )
                    )
                else:
                    st.caption(t("data.stocks.last_cached_missing"))

            latest_col, full_col = st.columns(2)

            with latest_col:
                latest_clicked = st.button(
                    t("data.stocks.download_latest_button"),
                    type="primary",
                    use_container_width=True,
                )

            with full_col:
                full_clicked = st.button(
                    t("data.stocks.download_full_button"),
                    use_container_width=True,
                )

            if latest_clicked:
                if not symbols:
                    st.warning(t("data.stocks.no_symbols"))
                else:
                    with st.spinner(t("data.stocks.spinner")):
                        latest_results = stock_mgr.download_latest(
                            symbols=symbols,
                            interval=DEFAULT_INTERVAL,
                            default_start=history_start_str,
                        )

                        if latest_results["success"]:
                            st.success(
                                t(
                                    "data.stocks.download_success",
                                    rows=latest_results.get("total_rows", 0),
                                    symbol_count=len(latest_results["success"]),
                                )
                            )
                            for item in latest_results["success"]:
                                st.write(
                                    t(
                                        "data.common.success_item",
                                        symbol=item["symbol"],
                                        rows=item["rows"],
                                    )
                                )

                        if latest_results.get("skipped"):
                            st.info(
                                t(
                                    "data.stocks.download_latest_skipped",
                                    count=len(latest_results["skipped"]),
                                    symbols=", ".join(latest_results["skipped"]),
                                )
                            )

                        if latest_results["failed"]:
                            st.warning(t("data.common.download_failed"))
                            for item in latest_results["failed"]:
                                st.write(
                                    t(
                                        "data.common.error_item",
                                        symbol=item["symbol"],
                                        error=item["error"],
                                    )
                                )

                        if (
                            latest_results["total_rows"] == 0
                            and not latest_results["success"]
                            and not latest_results["failed"]
                        ):
                            latest_cached = []
                            for sym in symbols:
                                coverage = stock_mgr.get_date_range(sym, DEFAULT_INTERVAL)
                                if coverage and coverage.get("max_date"):
                                    latest_cached.append(coverage["max_date"])

                            if latest_cached:
                                st.info(
                                    t(
                                        "data.stocks.download_latest_up_to_date_with_date",
                                        date=max(latest_cached),
                                    )
                                )
                            else:
                                st.info(t("data.stocks.download_latest_up_to_date"))

            if full_clicked:
                if not symbols:
                    st.warning(t("data.stocks.no_symbols"))
                else:
                    with st.spinner(t("data.stocks.spinner")):
                        end_date = datetime.now().strftime("%Y-%m-%d")
                        results = stock_mgr.download_stocks(
                            symbols=symbols,
                            start=history_start_str,
                            end=end_date,
                            interval=DEFAULT_INTERVAL,
                        )

                        if results["success"]:
                            st.success(
                                t(
                                    "data.stocks.download_success",
                                    rows=results.get("total_rows", 0),
                                    symbol_count=len(results["success"]),
                                )
                            )
                            for item in results["success"]:
                                st.write(
                                    t(
                                        "data.common.success_item",
                                        symbol=item["symbol"],
                                        rows=item["rows"],
                                    )
                                )

                        if results["failed"]:
                            st.warning(t("data.common.download_failed"))
                            for item in results["failed"]:
                                st.write(
                                    t(
                                        "data.common.error_item",
                                        symbol=item["symbol"],
                                        error=item["error"],
                                    )
                                )
            st.divider()
            st.subheader(t("data.stocks.bulk_title"))
            st.caption(t("data.stocks.bulk_description"))

            if st.button(t("data.stocks.bulk_button")):
                with st.spinner(t("data.stocks.bulk_spinner")):
                    try:
                        bundle = download_sp500_data()
                        bundle_results = bundle["results"]
                        symbols = bundle["symbols"]

                        st.success(
                            t(
                                "data.stocks.bulk_success",
                                count=len(bundle_results["success"]),
                                total=len(symbols),
                                rows=bundle_results.get("total_rows", 0),
                            )
                        )

                        if symbols:
                            st.caption(
                                t(
                                    "data.stocks.bulk_symbol_total",
                                    total=len(symbols),
                                )
                            )
                            st.caption(
                                t(
                                    "data.stocks.bulk_preview",
                                    preview=", ".join(symbols[:5]),
                                )
                            )

                        if bundle_results["failed"]:
                            st.warning(
                                t(
                                    "data.stocks.bulk_failed_summary",
                                    count=len(bundle_results["failed"]),
                                )
                            )
                            for item in bundle_results["failed"]:
                                st.write(
                                    t(
                                        "data.common.error_item",
                                        symbol=item["symbol"],
                                        error=item["error"],
                                    )
                                )

                        st.info(t("data.stocks.bulk_symbol_total", total=len(symbols)))
                    except Exception as exc:
                        message = str(exc)
                        lower_message = message.lower()
                        if "lxml" in lower_message:
                            st.error(t("data.stocks.bulk_error_lxml"))
                        elif "certificate verify failed" in lower_message:
                            st.error(t("data.stocks.bulk_error_ssl"))
                        else:
                            st.error(t("data.stocks.bulk_error", error=message))
        
        with col2:
            st.subheader(t("data.stocks.cached_title"))

            cached_symbols = stock_mgr.get_available_symbols()
            if cached_symbols:
                cached_selector_options = _merge_favorites_with_options(cached_symbols)

                if (
                    "cached_symbol_select" not in st.session_state
                    or st.session_state["cached_symbol_select"] not in cached_selector_options
                ):
                    st.session_state["cached_symbol_select"] = cached_selector_options[0]

                cached_page_size = st.selectbox(
                    t("data.stocks.cached_page_size"),
                    options=[10, 25, 50, 100],
                    index=1,
                    key="cached_page_size",
                )

                st.selectbox(
                    t("data.stocks.cached_selector_label"),
                    options=cached_selector_options,
                    key="cached_symbol_select",
                    on_change=_sync_cached_selection,
                )

                rows = []
                for symbol in cached_symbols:
                    date_range = stock_mgr.get_date_range(symbol, DEFAULT_INTERVAL)
                    if date_range:
                        rows.append(
                            {
                                "symbol": symbol,
                                "rows": date_range["count"],
                                "start": date_range["min_date"],
                                "end": date_range["max_date"],
                            }
                        )

                if not rows:
                    st.info(t("data.stocks.cached_none"))
                else:
                    rows.sort(key=lambda item: item["symbol"])
                    total = len(rows)
                    total_pages = max(1, math.ceil(total / cached_page_size))

                    current_page = st.session_state.get("cached_page", 1)
                    if current_page > total_pages:
                        current_page = total_pages
                    if current_page < 1:
                        current_page = 1
                    st.session_state["cached_page"] = current_page

                    page = st.number_input(
                        t("data.stocks.cached_page"),
                        min_value=1,
                        max_value=total_pages,
                        key="cached_page",
                        format="%d",
                    )
                    start_idx = (page - 1) * cached_page_size
                    end_idx = start_idx + cached_page_size
                    page_rows = rows[start_idx:end_idx]

                    display_df = pd.DataFrame(page_rows)
                    display_df = display_df.rename(
                        columns={
                            "symbol": t("data.stocks.cached_col_symbol"),
                            "rows": t("data.stocks.cached_col_rows"),
                            "start": t("data.stocks.cached_col_start"),
                            "end": t("data.stocks.cached_col_end"),
                        }
                    )
                    st.caption(
                        t(
                            "data.stocks.cached_stats",
                            page=page,
                            pages=total_pages,
                            total=total,
                        )
                    )

                    def _sync_viewer_from_cached(event: Any | None = None) -> None:
                        selection = None
                        if event is not None:
                            if isinstance(event, dict):
                                selection = event.get("selection")
                            else:
                                selection = getattr(event, "selection", None)

                        if not selection:
                            state_value = st.session_state.get("cached_overview_table")
                            if isinstance(state_value, dict):
                                selection = state_value.get("selection")

                        if not selection:
                            return

                        selected_rows = selection.get("rows")
                        if not selected_rows:
                            return

                        row_entry = selected_rows[0]
                        if isinstance(row_entry, dict):
                            row_index = row_entry.get("index")
                        else:
                            row_index = row_entry

                        if not isinstance(row_index, int):
                            return
                        if row_index < 0 or row_index >= len(page_rows):
                            return

                        selected_symbol = page_rows[row_index]["symbol"]
                        st.session_state["cached_symbol_select"] = selected_symbol
                        st.session_state["viewer_symbol"] = selected_symbol
                        st.session_state["viewer_page"] = 1

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        key="cached_overview_table",
                        selection_mode="single-row",
                        on_select=_sync_viewer_from_cached,
                    )
            else:
                st.info(t("data.stocks.cached_none"))
        
        st.divider()
        st.subheader(t("data.stocks.viewer_title"))

        available_symbols = stock_mgr.get_available_symbols()
        viewer_options = _merge_favorites_with_options(available_symbols)

        if not viewer_options:
            st.info(t("data.stocks.viewer_empty"))
        else:
            if (
                "viewer_symbol" not in st.session_state
                or st.session_state["viewer_symbol"] not in viewer_options
            ):
                st.session_state["viewer_symbol"] = viewer_options[0]

            viewer_symbol = st.selectbox(
                t("data.stocks.viewer_select_label"),
                options=viewer_options,
                key="viewer_symbol",
            )

            if viewer_symbol not in available_symbols:
                st.info(t("data.stocks.viewer_no_rows"))
            else:
                page_size = st.selectbox(
                    t("data.stocks.viewer_page_size"),
                    options=[25, 50, 100, 250],
                    index=2,
                    key="viewer_page_size",
                )

                total_rows = stock_mgr.get_row_count(viewer_symbol, interval=DEFAULT_INTERVAL)

                if total_rows == 0:
                    st.info(t("data.stocks.viewer_no_rows"))
                else:
                    total_pages = max(1, math.ceil(total_rows / page_size))
                    current_page = st.session_state.get("viewer_page", 1)
                    if current_page > total_pages:
                        current_page = total_pages
                    if current_page < 1:
                        current_page = 1
                    st.session_state["viewer_page"] = current_page

                    page = st.number_input(
                        t("data.stocks.viewer_page"),
                        min_value=1,
                        max_value=total_pages,
                        key="viewer_page",
                        format="%d",
                    )
                    offset = (page - 1) * page_size
                    data_df = stock_mgr.get_paginated_data(
                        viewer_symbol,
                        interval=DEFAULT_INTERVAL,
                        limit=page_size,
                        offset=offset,
                    )

                    if not data_df.empty:
                        display_df = data_df.copy()
                        display_df['date'] = display_df['date'].dt.strftime("%Y-%m-%d")
                        st.caption(
                            t(
                                "data.stocks.viewer_stats",
                                page=page,
                                pages=total_pages,
                                total=total_rows,
                            )
                        )
                        st.dataframe(display_df, use_container_width=True)

                    delete_section_key = f"delete_symbol_confirm_{viewer_symbol}"
                    st.markdown("---")
                    st.subheader(t("data.stocks.delete_symbol_section_title", symbol=viewer_symbol))
                    confirm_delete = st.checkbox(
                        t("data.stocks.delete_symbol_confirm", symbol=viewer_symbol),
                        key=delete_section_key,
                    )
                    if st.button(
                        t("data.stocks.delete_symbol_button"),
                        type="secondary",
                        disabled=not confirm_delete,
                    ):
                        try:
                            delete_result = stock_mgr.delete_symbol(viewer_symbol)
                            st.success(
                                t(
                                    "data.stocks.delete_symbol_success",
                                    symbol=viewer_symbol,
                                    equity_rows=delete_result["equity_rows"],
                                    indicator_rows=delete_result["indicator_rows"],
                                )
                            )
                            st.session_state.pop(delete_section_key, None)
                            st.session_state.pop("cached_symbol_select", None)
                            st.session_state.pop("viewer_symbol", None)
                            st.session_state.pop("cached_page", None)
                            st.session_state.pop("viewer_page", None)
                            st.experimental_rerun()
                        except Exception as exc:  # noqa: BLE001 - surface error to UI
                            st.error(
                                t(
                                    "data.stocks.delete_symbol_failure",
                                    symbol=viewer_symbol,
                                    error=str(exc),
                                )
                            )

        st.divider()
        st.subheader(t("data.stocks.delete_all_title"))
        st.warning(t("data.stocks.delete_all_warning"))
        confirm_delete_all = st.checkbox(t("data.stocks.delete_all_confirm"), key="delete_all_confirm")
        if st.button(
            t("data.stocks.delete_all_button"),
            type="secondary",
            disabled=not confirm_delete_all,
        ):
            try:
                delete_all_result = stock_mgr.delete_all()
                st.success(
                    t(
                        "data.stocks.delete_all_success",
                        equity_rows=delete_all_result["equity_rows"],
                        indicator_rows=delete_all_result["indicator_rows"],
                    )
                )
                st.session_state.pop("delete_all_confirm", None)
                st.session_state.pop("cached_symbol_select", None)
                st.session_state.pop("viewer_symbol", None)
                st.session_state.pop("cached_page", None)
                st.session_state.pop("viewer_page", None)
                st.experimental_rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))

        # CSV Upload
        st.divider()
        st.subheader(t("data.upload.title"))
        
        uploaded_file = st.file_uploader(
            t("data.upload.file_label"),
            type=["csv"],
            help=t("data.upload.help")
        )
        
        if uploaded_file:
            col_symbol, col_upload = st.columns([1, 1])
            with col_symbol:
                upload_symbol = st.text_input(t("data.upload.symbol_label"), value="CUSTOM")
            
            with col_upload:
                if st.button(t("data.upload.process_button")):
                    # Save file temporarily
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    result = stock_mgr.upload_csv(tmp_path, upload_symbol.upper())
                    os.unlink(tmp_path)
                    
                    if result.get("success"):
                        st.success(
                            t(
                                "data.upload.success",
                                rows=result["rows"],
                                symbol=result["symbol"],
                            )
                        )
                    else:
                        st.error(t("data.upload.error", error=result.get("error")))
    
    # === OPTIONS TAB ===
    with tab2:
        st.header(t("data.options.header"))

        # Import historical data from local CSV exports
        with st.expander(t("data.options.import_title"), expanded=False):
            st.caption(
                t(
                    "data.options.import_help",
                    path=str(OPTION_IMPORT_DIR.resolve()),
                )
            )
            
            # File type selector
            file_type = st.radio(
                "Select Data Type:",
                options=["option_chain", "volatility"],
                format_func=lambda x: "Options Chain Data" if x == "option_chain" else "Volatility Data",
                horizontal=True,
                key="options_file_type"
            )
            
            st.caption(
                "📁 **Options Chain CSV**: date, act_symbol, expiration, strike, call_put, bid, ask, vol, delta, gamma, theta, vega, rho"
                if file_type == "option_chain"
                else "📁 **Volatility CSV**: date, act_symbol, hv_current, hv_week_ago, hv_month_ago, hv_year_high, hv_year_high_date, hv_year_low, hv_year_low_date, iv_current, iv_week_ago, iv_month_ago, iv_year_high, iv_year_high_date, iv_year_low, iv_year_low_date"
            )
            
            if st.button(t("data.options.import_button"), key="options_import_button"):
                with st.spinner(t("data.options.import_spinner")):
                    if file_type == "option_chain":
                        import_results = options_mgr.import_from_directory(OPTION_IMPORT_DIR)
                    else:
                        import_results = options_mgr.import_volatility_from_directory(OPTION_IMPORT_DIR)

                files_processed = import_results.get("files", 0)
                rows_imported = import_results.get("rows", 0)
                errors = import_results.get("errors", [])

                if files_processed == 0 and rows_imported == 0 and not errors:
                    st.info(t("data.options.import_no_files"))
                else:
                    if rows_imported:
                        st.success(
                            t(
                                "data.options.import_success",
                                files=files_processed,
                                rows=rows_imported,
                            )
                        )
                    if errors:
                        st.warning(t("data.options.import_error_summary", count=len(errors)))
                        for item in errors:
                            st.write(
                                t(
                                    "data.options.import_error_item",
                                    file=item.get("file", "?"),
                                    error=item.get("error", "unknown"),
                                )
                            )

        st.caption(t("data.options.import_hint"))
        
        # View cached options
        st.divider()
        st.subheader(t("data.options.view_title"))
        option_symbols = options_mgr.get_available_symbols()

        if not option_symbols:
            st.info(t("data.options.no_cached_data"))
        else:
            if (
                "options_symbol" not in st.session_state
                or st.session_state["options_symbol"] not in option_symbols
            ):
                st.session_state["options_symbol"] = option_symbols[0]

            selected_symbol = st.selectbox(
                t("data.options.select_symbol"),
                options=option_symbols,
                key="options_symbol",
            )

            trade_dates = options_mgr.get_available_trade_dates(selected_symbol)
            if not trade_dates:
                st.info(t("data.options.no_trade_dates"))
            else:
                trade_date_index = st.session_state.get("options_trade_index", 0)
                trade_date_index = max(0, min(trade_date_index, len(trade_dates) - 1))

                col_trade_prev, col_trade_label, col_trade_next, col_trade_latest = st.columns([1, 3, 1, 1])
                with col_trade_prev:
                    if st.button(
                        t("data.options.trade_date_prev"),
                        key="options_trade_prev",
                        disabled=trade_date_index >= len(trade_dates) - 1,
                    ):
                        trade_date_index = min(trade_date_index + 1, len(trade_dates) - 1)
                with col_trade_next:
                    if st.button(
                        t("data.options.trade_date_next"),
                        key="options_trade_next",
                        disabled=trade_date_index <= 0,
                    ):
                        trade_date_index = max(trade_date_index - 1, 0)
                with col_trade_latest:
                    if st.button(
                        t("data.options.trade_date_latest"),
                        key="options_trade_latest",
                        disabled=trade_date_index == 0,
                    ):
                        trade_date_index = 0

                selected_trade_date = trade_dates[trade_date_index]
                with col_trade_label:
                    st.caption(f"{t('data.options.trade_date_view')}: {selected_trade_date}")

                st.session_state["options_trade_index"] = trade_date_index

                expirations = options_mgr.get_available_expirations(
                    selected_symbol, selected_trade_date
                )

                if not expirations:
                    st.info(t("data.options.no_expirations"))
                else:
                    expiration_index = st.session_state.get("options_exp_index", 0)
                    expiration_index = max(0, min(expiration_index, len(expirations) - 1))

                    col_exp_prev, col_exp_label, col_exp_next, col_exp_latest = st.columns([1, 3, 1, 1])
                    with col_exp_prev:
                        if st.button(
                            t("data.options.expiration_prev"),
                            key="options_exp_prev",
                            disabled=expiration_index >= len(expirations) - 1,
                        ):
                            expiration_index = min(expiration_index + 1, len(expirations) - 1)
                    with col_exp_next:
                        if st.button(
                            t("data.options.expiration_next"),
                            key="options_exp_next",
                            disabled=expiration_index <= 0,
                        ):
                            expiration_index = max(expiration_index - 1, 0)
                    with col_exp_latest:
                        if st.button(
                            t("data.options.expiration_latest"),
                            key="options_exp_latest",
                            disabled=expiration_index == 0,
                        ):
                            expiration_index = 0

                    selected_expiration = expirations[expiration_index]
                    with col_exp_label:
                        st.caption(f"{t('data.options.expiration_label')}: {selected_expiration}")

                    st.session_state["options_exp_index"] = expiration_index

                    chain_df = options_mgr.get_option_chain(
                        selected_symbol,
                        trade_date=selected_trade_date,
                        expiration=selected_expiration,
                    )

                    if chain_df.empty:
                        st.info(t("data.options.no_data"))
                    else:
                        metric_cols = [
                            "bid",
                            "ask",
                            "last",
                            "mid",
                            "volume",
                            "open_interest",
                            "implied_vol",
                            "delta",
                            "gamma",
                            "theta",
                            "vega",
                            "rho",
                        ]
                        required_cols = ["strike"] + metric_cols
                        for col in required_cols:
                            if col not in chain_df.columns:
                                chain_df[col] = None
                            chain_df[col] = pd.to_numeric(chain_df[col], errors="coerce")

                        chain_df["right"] = chain_df["right"].map(
                            lambda value: value.lower() if isinstance(value, str) else value
                        )
                        chain_df = chain_df.dropna(subset=["strike"]).reset_index(drop=True)

                        side_key = "options_chain_side"
                        side_options = ("call", "put")
                        if side_key not in st.session_state or st.session_state[side_key] not in side_options:
                            st.session_state[side_key] = side_options[0]

                        selected_side = st.radio(
                            t("data.options.greeks_side_label"),
                            options=side_options,
                            format_func=lambda value: t(f"data.options.side.{value}"),
                            horizontal=True,
                            key=side_key,
                        )

                        active_df = chain_df[chain_df["right"] == selected_side].copy()

                        selected_row = None
                        strike_value = None

                        if active_df.empty:
                            st.info(t("data.options.greeks_none"))
                        else:
                            active_df = active_df.sort_values("strike").reset_index(drop=True)

                            underlying_price_value = None
                            if "underlying_price" in chain_df.columns:
                                underlying_series = pd.to_numeric(
                                    chain_df["underlying_price"], errors="coerce"
                                ).dropna()
                                if not underlying_series.empty:
                                    try:
                                        underlying_price_value = float(underlying_series.iloc[0])
                                    except (TypeError, ValueError):
                                        underlying_price_value = None

                            table_columns = ["strike"] + metric_cols
                            display_rows = []
                            if underlying_price_value is not None:
                                underlying_row = {
                                    "option_idx": None,
                                    "context": t("data.options.row_label.underlying"),
                                    "strike": underlying_price_value,
                                }
                                for col in metric_cols:
                                    underlying_row[col] = None
                                display_rows.append(underlying_row)

                            for idx, option_row in active_df.iterrows():
                                row_data = {
                                    "option_idx": idx,
                                    "context": "",
                                    "strike": option_row.get("strike"),
                                }
                                for col in metric_cols:
                                    row_data[col] = option_row.get(col)
                                display_rows.append(row_data)

                            display_df = pd.DataFrame(display_rows)
                            display_df = display_df.where(pd.notnull(display_df), None)

                            table_display_df = display_df.drop(columns=["option_idx"], errors="ignore")

                            column_config = {
                                "context": st.column_config.Column(" "),
                                "strike": st.column_config.NumberColumn(
                                    t("data.options.col.strike"), format="%.2f"
                                ),
                                "bid": st.column_config.NumberColumn(
                                    t("data.options.metric.bid"), format="%.2f"
                                ),
                                "ask": st.column_config.NumberColumn(
                                    t("data.options.metric.ask"), format="%.2f"
                                ),
                                "last": st.column_config.NumberColumn(
                                    t("data.options.metric.last"), format="%.2f"
                                ),
                                "mid": st.column_config.NumberColumn(
                                    t("data.options.metric.mid"), format="%.2f"
                                ),
                                "volume": st.column_config.NumberColumn(
                                    t("data.options.metric.volume"), format="%.0f"
                                ),
                                "open_interest": st.column_config.NumberColumn(
                                    t("data.options.metric.open_interest"), format="%.0f"
                                ),
                                "implied_vol": st.column_config.NumberColumn(
                                    t("data.options.metric.implied_vol"), format="%.2f"
                                ),
                                "delta": st.column_config.NumberColumn(
                                    t("data.options.metric.delta"), format="%.4f"
                                ),
                                "gamma": st.column_config.NumberColumn(
                                    t("data.options.metric.gamma"), format="%.4f"
                                ),
                                "theta": st.column_config.NumberColumn(
                                    t("data.options.metric.theta"), format="%.4f"
                                ),
                                "vega": st.column_config.NumberColumn(
                                    t("data.options.metric.vega"), format="%.4f"
                                ),
                                "rho": st.column_config.NumberColumn(
                                    t("data.options.metric.rho"), format="%.4f"
                                ),
                            }

                            table_key = (
                                f"options_chain_table_{selected_symbol}_{selected_trade_date}_{selected_expiration}_{selected_side}"
                            )

                            # Add styling for bid/ask columns
                            def highlight_bid_ask(df):
                                """Apply highlighting to bid/ask columns."""
                                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                                if 'bid' in df.columns:
                                    styles['bid'] = 'background-color: #e3f2fd; font-weight: bold'
                                if 'ask' in df.columns:
                                    styles['ask'] = 'background-color: #fff3e0; font-weight: bold'
                                return styles

                            st.dataframe(
                                table_display_df,
                                use_container_width=True,
                                hide_index=True,
                                column_config=column_config,
                                selection_mode="single-row",
                                key=table_key,
                                height=360,
                            )
                            
                            # Display volatility data for the symbol and trade date
                            volatility_df = options_mgr.get_volatility_data(selected_symbol, selected_trade_date)
                            if not volatility_df.empty:
                                with st.expander("📊 Volatility Metrics (HV/IV)", expanded=False):
                                    vol_row = volatility_df.iloc[0]
                                    
                                    col_hv, col_iv = st.columns(2)
                                    
                                    with col_hv:
                                        st.subheader("Historical Volatility (HV)")
                                        hv_col1, hv_col2, hv_col3 = st.columns(3)
                                        with hv_col1:
                                            st.metric("Current", f"{vol_row.get('hv_current', 0)*100:.2f}%" if vol_row.get('hv_current') else "N/A")
                                        with hv_col2:
                                            st.metric("Week Ago", f"{vol_row.get('hv_week_ago', 0)*100:.2f}%" if vol_row.get('hv_week_ago') else "N/A")
                                        with hv_col3:
                                            st.metric("Month Ago", f"{vol_row.get('hv_month_ago', 0)*100:.2f}%" if vol_row.get('hv_month_ago') else "N/A")
                                        
                                        hv_col4, hv_col5 = st.columns(2)
                                        with hv_col4:
                                            high_val = f"{vol_row.get('hv_year_high', 0)*100:.2f}%" if vol_row.get('hv_year_high') else "N/A"
                                            high_date = vol_row.get('hv_year_high_date', 'N/A')
                                            st.metric("Year High", high_val, delta=high_date, delta_color="off")
                                        with hv_col5:
                                            low_val = f"{vol_row.get('hv_year_low', 0)*100:.2f}%" if vol_row.get('hv_year_low') else "N/A"
                                            low_date = vol_row.get('hv_year_low_date', 'N/A')
                                            st.metric("Year Low", low_val, delta=low_date, delta_color="off")
                                    
                                    with col_iv:
                                        st.subheader("Implied Volatility (IV)")
                                        iv_col1, iv_col2, iv_col3 = st.columns(3)
                                        with iv_col1:
                                            st.metric("Current", f"{vol_row.get('iv_current', 0)*100:.2f}%" if vol_row.get('iv_current') else "N/A")
                                        with iv_col2:
                                            st.metric("Week Ago", f"{vol_row.get('iv_week_ago', 0)*100:.2f}%" if vol_row.get('iv_week_ago') else "N/A")
                                        with iv_col3:
                                            st.metric("Month Ago", f"{vol_row.get('iv_month_ago', 0)*100:.2f}%" if vol_row.get('iv_month_ago') else "N/A")
                                        
                                        iv_col4, iv_col5 = st.columns(2)
                                        with iv_col4:
                                            high_val = f"{vol_row.get('iv_year_high', 0)*100:.2f}%" if vol_row.get('iv_year_high') else "N/A"
                                            high_date = vol_row.get('iv_year_high_date', 'N/A')
                                            st.metric("Year High", high_val, delta=high_date, delta_color="off")
                                        with iv_col5:
                                            low_val = f"{vol_row.get('iv_year_low', 0)*100:.2f}%" if vol_row.get('iv_year_low') else "N/A"
                                            low_date = vol_row.get('iv_year_low_date', 'N/A')
                                            st.metric("Year Low", low_val, delta=low_date, delta_color="off")

                            selection_state = st.session_state.get(table_key)
                            default_index = 1 if underlying_price_value is not None and len(table_display_df) > 1 else 0
                            selected_display_index = default_index
                            if selection_state:
                                selected_rows = selection_state.get("selection", {}).get("rows")
                                if selected_rows:
                                    candidate = selected_rows[0]
                                    if isinstance(candidate, dict):
                                        candidate = candidate.get("index", default_index)
                                    if isinstance(candidate, int) and 0 <= candidate < len(table_display_df):
                                        selected_display_index = candidate

                            if not table_display_df.empty and 0 <= selected_display_index < len(display_df):
                                option_idx_value = display_df.iloc[selected_display_index].get("option_idx")
                                if option_idx_value is None and not active_df.empty:
                                    option_idx_value = 0
                                if option_idx_value is not None:
                                    try:
                                        option_idx_int = int(option_idx_value)
                                    except (TypeError, ValueError):
                                        option_idx_int = None
                                    if option_idx_int is not None and 0 <= option_idx_int < len(active_df):
                                        selected_row = active_df.iloc[option_idx_int]
                                        try:
                                            strike_value = float(selected_row.get("strike"))
                                        except (TypeError, ValueError):
                                            strike_value = None

                            if selected_row is not None:
                                detail_rows = []
                                for metric in metric_cols:
                                    detail_rows.append(
                                        {
                                            "Metric": t(f"data.options.metric.{metric}"),
                                            "Value": selected_row.get(metric),
                                        }
                                    )

                                detail_df = pd.DataFrame(detail_rows)

                                def _format_metric_value(val):
                                    if val is None or pd.isna(val):
                                        return ""
                                    try:
                                        return round(float(val), 4)
                                    except (TypeError, ValueError):
                                        return val

                                detail_df["Value"] = detail_df["Value"].apply(_format_metric_value)

                                st.markdown(
                                    t(
                                        "data.options.greeks_title",
                                        side=t(f"data.options.side.{selected_side}"),
                                        strike=f"{strike_value:.2f}" if strike_value is not None else "?",
                                    )
                                )
                                st.dataframe(detail_df, hide_index=True, use_container_width=True)
                            else:
                                st.info(t("data.options.greeks_none"))
                                if strike_value is not None:
                                    price_fields = [
                                        ("bid", t("data.options.metric.bid")),
                                        ("ask", t("data.options.metric.ask")),
                                        ("mid", t("data.options.metric.mid")),
                                        ("last", t("data.options.metric.last")),
                                    ]
                                    greek_fields = [
                                        ("delta", t("data.options.metric.delta")),
                                        ("gamma", t("data.options.metric.gamma")),
                                        ("theta", t("data.options.metric.theta")),
                                        ("vega", t("data.options.metric.vega")),
                                        ("rho", t("data.options.metric.rho")),
                                    ]

                                    timeline_trade = options_mgr.get_time_series_by_trade_date(
                                        selected_symbol,
                                        strike_value,
                                        selected_side,
                                        selected_expiration,
                                    )

                                    if timeline_trade.empty:
                                        st.info(t("data.options.timeline_no_data"))
                                    else:
                                        timeline_trade["trade_date"] = pd.to_datetime(
                                            timeline_trade["trade_date"], errors="coerce"
                                        )

                                        fig_price = go.Figure()
                                        for field, label in price_fields:
                                            if field in timeline_trade.columns and timeline_trade[field].notna().any():
                                                fig_price.add_trace(
                                                    go.Scatter(
                                                        x=timeline_trade["trade_date"],
                                                        y=timeline_trade[field],
                                                        mode="lines+markers",
                                                        name=label,
                                                    )
                                                )

                                        fig_price.update_layout(
                                            title=t(
                                                "data.options.timeline_trade_title",
                                                side=t(f"data.options.side.{selected_side}"),
                                                strike=f"{strike_value:.2f}",
                                                expiration=selected_expiration,
                                            ),
                                            hovermode="x unified",
                                        )
                                        fig_price.update_xaxes(
                                            title=t("data.options.timeline_axis_trade_date")
                                        )
                                        fig_price.update_yaxes(title=t("data.options.metric.price"))
                                        st.plotly_chart(fig_price, use_container_width=True)

                                        fig_greeks = go.Figure()
                                        for field, label in greek_fields:
                                            if field in timeline_trade.columns and timeline_trade[field].notna().any():
                                                fig_greeks.add_trace(
                                                    go.Scatter(
                                                        x=timeline_trade["trade_date"],
                                                        y=timeline_trade[field],
                                                        mode="lines+markers",
                                                        name=label,
                                                    )
                                                )

                                        if fig_greeks.data:
                                            fig_greeks.update_layout(
                                                title=t(
                                                    "data.options.timeline_trade_greeks",
                                                    side=t(f"data.options.side.{selected_side}"),
                                                    strike=f"{strike_value:.2f}",
                                                    expiration=selected_expiration,
                                                ),
                                                hovermode="x unified",
                                            )
                                            fig_greeks.update_xaxes(
                                                title=t("data.options.timeline_axis_trade_date")
                                            )
                                            fig_greeks.update_yaxes(title=t("data.options.metric.generic"))
                                            st.plotly_chart(fig_greeks, use_container_width=True)

                                    timeline_exp = options_mgr.get_time_series_by_expiration(
                                        selected_symbol,
                                        strike_value,
                                        selected_side,
                                        selected_trade_date,
                                    ) if strike_value is not None else pd.DataFrame()

                                    if timeline_exp.empty:
                                        st.info(t("data.options.timeline_expiration_no_data"))
                                    else:
                                        timeline_exp["expiration"] = pd.to_datetime(
                                            timeline_exp["expiration"], errors="coerce"
                                        )

                                        fig_exp_price = go.Figure()
                                        for field, label in price_fields:
                                            if field in timeline_exp.columns and timeline_exp[field].notna().any():
                                                fig_exp_price.add_trace(
                                                    go.Scatter(
                                                        x=timeline_exp["expiration"],
                                                        y=timeline_exp[field],
                                                        mode="lines+markers",
                                                        name=label,
                                                    )
                                                )

                                        fig_exp_price.update_layout(
                                            title=t(
                                                "data.options.timeline_expiration_title",
                                                side=t(f"data.options.side.{selected_side}"),
                                                strike=f"{strike_value:.2f}",
                                                trade_date=selected_trade_date,
                                            ),
                                            hovermode="x unified",
                                        )
                                        fig_exp_price.update_xaxes(
                                            title=t("data.options.timeline_axis_expiration")
                                        )
                                        fig_exp_price.update_yaxes(title=t("data.options.metric.price"))
                                        st.plotly_chart(fig_exp_price, use_container_width=True)

                                        fig_exp_greeks = go.Figure()
                                        for field, label in greek_fields:
                                            if field in timeline_exp.columns and timeline_exp[field].notna().any():
                                                fig_exp_greeks.add_trace(
                                                    go.Scatter(
                                                        x=timeline_exp["expiration"],
                                                        y=timeline_exp[field],
                                                        mode="lines+markers",
                                                        name=label,
                                                    )
                                                )

                                        if fig_exp_greeks.data:
                                            fig_exp_greeks.update_layout(
                                                title=t(
                                                    "data.options.timeline_expiration_greeks",
                                                    side=t(f"data.options.side.{selected_side}"),
                                                    strike=f"{strike_value:.2f}",
                                                    trade_date=selected_trade_date,
                                                ),
                                                hovermode="x unified",
                                            )
                                            fig_exp_greeks.update_xaxes(
                                                title=t("data.options.timeline_axis_expiration")
                                            )
                                            fig_exp_greeks.update_yaxes(title=t("data.options.metric.generic"))
                                            st.plotly_chart(fig_exp_greeks, use_container_width=True)

        st.divider()
        st.subheader(t("data.options.delete_title"))

        delete_symbols = options_mgr.get_available_symbols()
        if not delete_symbols:
            st.info(t("data.options.no_cached_data"))
        else:
            col_del_symbol, col_del_all = st.columns([2, 1])

            with col_del_symbol:
                delete_symbol = st.selectbox(
                    t("data.options.delete_symbol_label"),
                    options=delete_symbols,
                    key="options_delete_symbol",
                )
                confirm_symbol_delete = st.checkbox(
                    t("data.options.delete_symbol_confirm", symbol=delete_symbol),
                    key="options_delete_symbol_confirm",
                )
                if st.button(
                    t("data.options.delete_symbol_button"),
                    key="options_delete_symbol_button",
                    disabled=not confirm_symbol_delete,
                ):
                    removed = options_mgr.delete_symbol(delete_symbol)
                    st.session_state.pop("options_symbol", None)
                    st.session_state.pop("options_trade_date", None)
                    st.session_state.pop("options_expiration", None)
                    st.session_state.pop("options_trade_index", None)
                    st.session_state.pop("options_exp_index", None)
                    st.session_state.pop("options_chain_side", None)
                    st.session_state.pop("options_table_context", None)
                    st.session_state.pop("options_table_page", None)
                    st.session_state.pop("options_table_page_size", None)
                    st.session_state.pop("options_delete_symbol_confirm", None)
                    st.success(
                        t(
                            "data.options.delete_symbol_success",
                            symbol=delete_symbol,
                            rows=removed or 0,
                        )
                    )
                    st.experimental_rerun()

            with col_del_all:
                confirm_delete_all = st.checkbox(
                    t("data.options.delete_all_confirm"),
                    key="options_delete_all_confirm",
                )
                if st.button(
                    t("data.options.delete_all_button"),
                    key="options_delete_all_button",
                    type="secondary",
                    disabled=not confirm_delete_all,
                ):
                    removed_all = options_mgr.delete_all()
                    st.session_state.pop("options_symbol", None)
                    st.session_state.pop("options_trade_date", None)
                    st.session_state.pop("options_expiration", None)
                    st.session_state.pop("options_trade_index", None)
                    st.session_state.pop("options_exp_index", None)
                    st.session_state.pop("options_chain_side", None)
                    st.session_state.pop("options_table_context", None)
                    st.session_state.pop("options_table_page", None)
                    st.session_state.pop("options_table_page_size", None)
                    st.session_state.pop("options_delete_symbol_confirm", None)
                    st.session_state.pop("options_delete_all_confirm", None)
                    st.success(
                        t("data.options.delete_all_success", rows=removed_all or 0)
                    )
                    st.experimental_rerun()
    
    # === VIEW INDICATORS TAB ===
    with tab3:
        st.header(t("data.indicators.header"))
        
        # Symbol selection
        cached_symbols = stock_mgr.get_available_symbols()
        indicator_options = _merge_favorites_with_options(cached_symbols)

        if not indicator_options:
            st.warning(t("data.indicators.no_data"))
        else:
            indicator_storage = IndicatorStorage()
            col1, col2 = st.columns([1, 3])

            with col1:
                if (
                    "indicators_symbol" not in st.session_state
                    or st.session_state["indicators_symbol"] not in indicator_options
                ):
                    st.session_state["indicators_symbol"] = indicator_options[0]

                selected_symbol = st.selectbox(
                    t("data.indicators.select_symbol"),
                    options=indicator_options,
                    key="indicators_symbol",
                )

                st.subheader(t("data.indicators.date_range"))
                preset_definitions = [
                    ("custom", None),
                    ("last_week", pd.DateOffset(weeks=1)),
                    ("last_month", pd.DateOffset(months=1)),
                    ("last_three_months", pd.DateOffset(months=3)),
                    ("last_year", pd.DateOffset(years=1)),
                    ("last_two_years", pd.DateOffset(years=2)),
                    ("last_three_years", pd.DateOffset(years=3)),
                    ("last_five_years", pd.DateOffset(years=5)),
                ]

                preset_labels = {
                    key: t(f"data.indicators.date_preset.{key}")
                    for key, _ in preset_definitions
                }
                preset_options = [preset_labels[key] for key, _ in preset_definitions]
                label_to_key = {label: key for key, label in preset_labels.items()}
                preset_lookup = dict(preset_definitions)

                selected_preset_label = st.selectbox(
                    t("data.indicators.date_preset.label"),
                    options=preset_options,
                    key="indicators_date_preset",
                )

                selected_preset_key = label_to_key[selected_preset_label]
                prior_preset = st.session_state.get("indicators_date_preset_applied")

                if selected_preset_key != "custom" and selected_preset_key != prior_preset:
                    offset = preset_lookup[selected_preset_key]
                    today = datetime.now().date()
                    start_date = (pd.Timestamp(today) - offset).date()
                    st.session_state["indicators_view_start"] = start_date
                    st.session_state["indicators_view_end"] = today
                st.session_state["indicators_date_preset_applied"] = selected_preset_key

                view_start = st.date_input(
                    t("data.indicators.from"),
                    value=st.session_state.get(
                        "indicators_view_start",
                        (datetime.now() - timedelta(days=180)).date(),
                    ),
                    key="indicators_view_start",
                )
                view_end = st.date_input(
                    t("data.indicators.to"),
                    value=st.session_state.get("indicators_view_end", datetime.now().date()),
                    key="indicators_view_end",
                )

                st.subheader(t("data.indicators.section_title"))
                show_sma_20 = st.checkbox(t("data.indicators.checkbox.sma20"), value=True)
                show_sma_50 = st.checkbox(t("data.indicators.checkbox.sma50"), value=True)
                show_sma_200 = st.checkbox(t("data.indicators.checkbox.sma200"), value=False)
                show_ema_12 = st.checkbox(t("data.indicators.checkbox.ema12"), value=False)
                show_rsi = st.checkbox(t("data.indicators.checkbox.rsi"), value=True)
                show_macd = st.checkbox(t("data.indicators.checkbox.macd"), value=False)
                show_bbands = st.checkbox(t("data.indicators.checkbox.bbands"), value=False)

                has_stored = indicator_storage.has_indicators(selected_symbol)
                if has_stored:
                    st.info(t("data.indicators.stored_available"))
                else:
                    st.warning(t("data.indicators.stored_missing"))

                if has_stored:
                    refresh_indicators = st.button(
                        t("data.indicators.refresh_button"),
                        help=t("data.indicators.refresh_help"),
                        key="indicators_refresh_button",
                    )
                else:
                    refresh_indicators = st.button(
                        t("data.indicators.refresh_button"),
                        help=t("data.indicators.refresh_help"),
                        key="indicators_refresh_button",
                        disabled=True,
                    )

            with col2:
                if refresh_indicators:
                    with st.spinner(t("data.indicators.refresh_spinner")):
                        raw_df = stock_mgr.get_cached_data(
                            selected_symbol,
                            start=view_start.strftime("%Y-%m-%d"),
                            end=view_end.strftime("%Y-%m-%d"),
                        )
                        if raw_df.empty:
                            st.warning(t("data.indicators.refresh_no_source", symbol=selected_symbol))
                        else:
                            indicator_storage.save_indicators(selected_symbol, raw_df)
                            st.success(t("data.indicators.refresh_success"))

                start_str = view_start.strftime("%Y-%m-%d")
                end_str = view_end.strftime("%Y-%m-%d")

                with st.spinner(t("data.indicators.loading_spinner")):
                    df_with_indicators = indicator_storage.get_indicators_with_ohlcv(
                        selected_symbol,
                        start=start_str,
                        end=end_str,
                    )

                if df_with_indicators.empty:
                    st.warning(t("data.indicators.load_no_data", symbol=selected_symbol))
                else:
                    if 'sma_20' in df_with_indicators.columns:
                        df_with_indicators.rename(
                            columns={
                                'sma_20': 'SMA_20',
                                'sma_50': 'SMA_50',
                                'sma_200': 'SMA_200',
                                'ema_12': 'EMA_12',
                                'ema_26': 'EMA_26',
                                'rsi_14': 'RSI',
                                'macd': 'MACD',
                                'macd_signal': 'MACD_Signal',
                                'macd_histogram': 'MACD_Histogram',
                                'bb_upper': 'BB_Upper',
                                'bb_middle': 'BB_Middle',
                                'bb_lower': 'BB_Lower',
                            },
                            inplace=True,
                        )

                    st.subheader(t("data.indicators.chart_title", symbol=selected_symbol))

                    num_subplots = 1
                    if show_rsi:
                        num_subplots += 1
                    if show_macd:
                        num_subplots += 1

                    row_heights = [0.6] + [0.2] * (num_subplots - 1)
                    subplot_titles = [t("data.indicators.subplot.price")]
                    if show_rsi:
                        subplot_titles.append(t("data.indicators.subplot.rsi"))
                    if show_macd:
                        subplot_titles.append(t("data.indicators.subplot.macd"))

                    fig = make_subplots(
                        rows=num_subplots,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=row_heights,
                        subplot_titles=subplot_titles,
                    )

                    fig.add_trace(
                        go.Candlestick(
                            x=df_with_indicators['date'],
                            open=df_with_indicators['open'],
                            high=df_with_indicators['high'],
                            low=df_with_indicators['low'],
                            close=df_with_indicators['close'],
                            name=t("data.indicators.legend.candles"),
                            increasing_line_color="#2ca02c",
                            decreasing_line_color="#d62728",
                            increasing_fillcolor="rgba(44,160,44,0.5)",
                            decreasing_fillcolor="rgba(214,39,40,0.5)",
                            showlegend=True,
                        ),
                        row=1,
                        col=1,
                    )

                    if show_sma_20 and 'SMA_20' in df_with_indicators.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['SMA_20'],
                                name=t("data.indicators.checkbox.sma20"),
                                line=dict(color='orange', width=1),
                            ),
                            row=1,
                            col=1,
                        )

                    if show_sma_50 and 'SMA_50' in df_with_indicators.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['SMA_50'],
                                name=t("data.indicators.checkbox.sma50"),
                                line=dict(color='green', width=1),
                            ),
                            row=1,
                            col=1,
                        )

                    if show_sma_200 and 'SMA_200' in df_with_indicators.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['SMA_200'],
                                name=t("data.indicators.checkbox.sma200"),
                                line=dict(color='red', width=1),
                            ),
                            row=1,
                            col=1,
                        )

                    if show_ema_12 and 'EMA_12' in df_with_indicators.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['EMA_12'],
                                name=t("data.indicators.legend.ema12"),
                                line=dict(color='purple', width=1, dash='dash'),
                            ),
                            row=1,
                            col=1,
                        )

                    if show_bbands and {'BB_Upper', 'BB_Middle', 'BB_Lower'}.issubset(df_with_indicators.columns):
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['BB_Upper'],
                                name=t("data.indicators.legend.bb_upper"),
                                line=dict(color='gray', width=1, dash='dot'),
                                showlegend=True,
                            ),
                            row=1,
                            col=1,
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['BB_Middle'],
                                name=t("data.indicators.legend.bb_middle"),
                                line=dict(color='gray', width=1),
                                showlegend=False,
                            ),
                            row=1,
                            col=1,
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['BB_Lower'],
                                name=t("data.indicators.legend.bb_lower"),
                                line=dict(color='gray', width=1, dash='dot'),
                                fill='tonexty',
                                fillcolor='rgba(128,128,128,0.1)',
                                showlegend=False,
                            ),
                            row=1,
                            col=1,
                        )

                    current_row = 2
                    if show_rsi and 'RSI' in df_with_indicators.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['RSI'],
                                name=t("data.indicators.checkbox.rsi"),
                                line=dict(color='purple', width=2),
                            ),
                            row=current_row,
                            col=1,
                        )
                        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
                        fig.update_yaxes(title_text=t("data.indicators.subplot.rsi"), row=current_row, col=1)
                        current_row += 1

                    if show_macd and {'MACD', 'MACD_Signal', 'MACD_Histogram'}.issubset(df_with_indicators.columns):
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['MACD'],
                                name=t("data.indicators.checkbox.macd"),
                                line=dict(color='blue', width=2),
                            ),
                            row=current_row,
                            col=1,
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['MACD_Signal'],
                                name=t("data.indicators.legend.macd_signal"),
                                line=dict(color='orange', width=2),
                            ),
                            row=current_row,
                            col=1,
                        )
                        fig.add_trace(
                            go.Bar(
                                x=df_with_indicators['date'],
                                y=df_with_indicators['MACD_Histogram'],
                                name=t("data.indicators.legend.macd_histogram"),
                                marker_color='gray',
                                opacity=0.5,
                            ),
                            row=current_row,
                            col=1,
                        )
                        fig.update_yaxes(title_text=t("data.indicators.subplot.macd"), row=current_row, col=1)

                    fig.update_layout(
                        height=200 + 300 * num_subplots,
                        showlegend=True,
                        hovermode='x unified',
                        xaxis_rangeslider_visible=False,
                    )
                    fig.update_xaxes(title_text=t("data.indicators.xaxis.date"), row=num_subplots, col=1)
                    fig.update_yaxes(title_text=t("data.indicators.yaxis.price"), row=1, col=1)

                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader(t("data.indicators.table_title"))

                    display_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
                    indicator_cols = [
                        col
                        for col in df_with_indicators.columns
                        if col not in ['symbol', 'interval', 'adj_close', 'source', 'asof']
                        and col not in display_cols
                    ]
                    display_cols.extend(indicator_cols)

                    display_df = df_with_indicators[display_cols].copy()
                    display_df = display_df.round(2)

                    table_page_size = st.selectbox(
                        t("data.indicators.table_page_size"),
                        options=[25, 50, 100, 250],
                        index=1,
                        key="indicators_table_page_size",
                    )

                    total_rows = len(display_df)
                    total_pages = max(1, math.ceil(total_rows / table_page_size))

                    if "indicators_table_page" not in st.session_state:
                        st.session_state["indicators_table_page"] = 1
                    if st.session_state["indicators_table_page"] > total_pages:
                        st.session_state["indicators_table_page"] = total_pages
                    if st.session_state["indicators_table_page"] < 1:
                        st.session_state["indicators_table_page"] = 1

                    table_page = int(
                        st.number_input(
                        t("data.indicators.table_page"),
                        min_value=1,
                        max_value=total_pages,
                        key="indicators_table_page",
                            format="%d",
                        )
                    )
                    table_start = (table_page - 1) * table_page_size
                    table_end = table_start + table_page_size
                    table_slice = display_df.iloc[table_start:table_end]

                    st.caption(
                        t(
                            "data.indicators.table_stats",
                            page=table_page,
                            pages=total_pages,
                            total=total_rows,
                        )
                    )
                    st.dataframe(table_slice, use_container_width=True)

                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label=t("data.indicators.download_button"),
                        data=csv,
                        file_name=f"{selected_symbol}_with_indicators_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )


if __name__ == "__main__":
    show()
