"""Results visualization page."""
import json

import pandas as pd
import streamlit as st

from src.data import StockDataManager
from src.db import get_db
from src.ui import t, use_language_selector
from src.visualization import ChartGenerator


def show() -> None:
    """Display the results page."""
    use_language_selector()

    st.title(t("results.title"))
    st.write(t("results.subtitle"))

    db = get_db()
    chart_gen = ChartGenerator()
    stock_mgr = StockDataManager()

    backtests = db.fetchall(
        """SELECT b.id, s.name as strategy_name, b.status, b.created_at, b.start, b.end,
                  b.universe, b.benchmarks
           FROM backtests b
           JOIN strategies s ON b.strategy_id = s.id
           WHERE b.status = 'completed'
           ORDER BY b.created_at DESC"""
    )

    if not backtests:
        st.info(t("results.info.no_completed"))
        return

    st.subheader(t("results.section.select"))
    
    # Delete actions
    col_select, col_delete_one, col_delete_all = st.columns([3, 1, 1])
    
    with col_delete_all:
        if st.button("🗑️ Delete All", type="secondary", use_container_width=True, help="Delete all backtest results"):
            if st.session_state.get("confirm_delete_all"):
                # Perform deletion
                db.execute("DELETE FROM equity_curves")
                db.execute("DELETE FROM metrics_run")
                db.execute("DELETE FROM backtests WHERE status = 'completed'")
                st.success("✅ All backtest results deleted!")
                st.session_state.pop("confirm_delete_all", None)
                st.rerun()
            else:
                st.session_state["confirm_delete_all"] = True
                st.warning("⚠️ Click 'Delete All' again to confirm deletion of all results!")

    default_index = 0
    last_bt = st.session_state.get("last_backtest_id")
    if last_bt:
        for idx, bt in enumerate(backtests):
            if bt["id"] == last_bt:
                default_index = idx
                break

    backtest_options = {
        f"{bt['strategy_name']} - {bt['created_at'][:10]} ({bt['id']})": bt["id"]
        for bt in backtests
    }

    with col_select:
        selected = st.selectbox(
            t("results.form.choose_backtest"),
            options=list(backtest_options.keys()),
            index=default_index,
            label_visibility="collapsed"
        )

    bt_id = backtest_options[selected]
    
    with col_delete_one:
        if st.button("🗑️ Delete This", type="secondary", use_container_width=True, help="Delete selected backtest result"):
            if st.session_state.get(f"confirm_delete_{bt_id}"):
                # Perform deletion
                db.execute("DELETE FROM equity_curves WHERE bt_id = ?", (bt_id,))
                db.execute("DELETE FROM metrics_run WHERE bt_id = ?", (bt_id,))
                db.execute("DELETE FROM backtests WHERE id = ?", (bt_id,))
                st.success(f"✅ Backtest {bt_id} deleted!")
                st.session_state.pop(f"confirm_delete_{bt_id}", None)
                st.session_state.pop("last_backtest_id", None)
                st.rerun()
            else:
                st.session_state[f"confirm_delete_{bt_id}"] = True
                st.warning(f"⚠️ Click 'Delete This' again to confirm deletion of backtest {bt_id}!")

    backtest = db.fetchone(
        """SELECT b.*, s.name as strategy_name, s.json as strategy_json
           FROM backtests b
           JOIN strategies s ON b.strategy_id = s.id
           WHERE b.id = ?""",
        (bt_id,),
    )

    metrics = db.fetchone(
        "SELECT * FROM metrics_run WHERE bt_id = ?",
        (bt_id,),
    )

    if not metrics:
        st.warning(t("results.warning.no_metrics"))
        return

    st.subheader(t("results.section.summary"))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_return = metrics.get("tot_return", 0)
        st.metric(
            t("results.metric.total_return"),
            f"{total_return * 100:.2f}%",
            delta=f"{total_return * 100:.2f}%",
        )

    with col2:
        sharpe = metrics.get("sharpe", 0)
        st.metric(
            t("results.metric.sharpe"),
            f"{sharpe:.3f}",
        )

    with col3:
        max_dd = metrics.get("max_dd", 0)
        st.metric(
            t("results.metric.max_dd"),
            f"{max_dd * 100:.2f}%",
            delta=f"{max_dd * 100:.2f}%",
            delta_color="inverse",
        )

    with col4:
        excess_return = metrics.get("excess_return")
        if excess_return is not None:
            st.metric(
                t("results.metric.excess_return"),
                f"{excess_return * 100:.2f}%",
                delta=f"{excess_return * 100:.2f}%",
            )
        else:
            cagr = metrics.get("cagr")
            st.metric(
                t("results.metric.cagr"),
                f"{cagr * 100:.2f}%" if cagr else "N/A",
            )

    artifacts_raw = backtest.get("artifacts")
    try:
        artifacts = json.loads(artifacts_raw) if artifacts_raw else {}
    except (TypeError, json.JSONDecodeError):
        artifacts = {}

    trade_log = artifacts.get("trade_log") or []

    equity_tab, metrics_tab, trades_tab, benchmark_tab, details_tab = st.tabs(
        [
            t("results.tabs.equity"),
            t("results.tabs.metrics"),
            t("results.tabs.trades"),
            t("results.tabs.benchmark"),
            t("results.tabs.details"),
        ]
    )

    with equity_tab:
        st.subheader(t("results.tabs.equity_header"))

        equity_rows = db.fetchall(
            """SELECT timestamp, value, cash, pnl, return_pct
                   FROM equity_curves
                   WHERE bt_id = ?
                   ORDER BY timestamp""",
            (bt_id,),
        )

        if equity_rows:
            equity_df = pd.DataFrame(equity_rows)
            equity_df["date"] = pd.to_datetime(equity_df["timestamp"])
            equity_df.sort_values("date", inplace=True)
            equity_df["return_pct"] = equity_df["return_pct"].fillna(0.0)
            equity_df["pnl"] = equity_df["pnl"].fillna(0.0)

            st.plotly_chart(
                chart_gen.equity_trend_chart(
                    equity_df,
                    title=t("results.chart.equity_trend"),
                ),
                use_container_width=True,
            )

            st.plotly_chart(
                chart_gen.daily_returns_bar_chart(
                    equity_df,
                    title=t("results.chart.daily_returns"),
                ),
                use_container_width=True,
            )

            total_gain_days = int((equity_df["return_pct"] > 0).sum())
            total_loss_days = int((equity_df["return_pct"] < 0).sum())
            st.caption(
                t(
                    "results.caption.sessions",
                    gains=total_gain_days,
                    losses=total_loss_days,
                )
            )

            def _format_gain_loss(df: pd.DataFrame) -> pd.DataFrame:
                formatted = df.copy()
                formatted["date"] = formatted["date"].apply(
                    lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else "—"
                )
                formatted["return_pct"] = formatted["return_pct"] * 100
                formatted = formatted[["date", "return_pct", "value", "pnl"]]

                date_col = t("results.gain_loss.date")
                return_col = t("results.gain_loss.return")
                value_col = t("results.gain_loss.value")
                pnl_col = t("results.gain_loss.pnl")

                formatted.rename(
                    columns={
                        "date": date_col,
                        "return_pct": return_col,
                        "value": value_col,
                        "pnl": pnl_col,
                    },
                    inplace=True,
                )

                formatted[return_col] = formatted[return_col].map(lambda x: f"{x:.2f}%")
                formatted[value_col] = formatted[value_col].map(lambda x: f"${x:,.2f}")
                formatted[pnl_col] = formatted[pnl_col].map(lambda x: f"${x:,.2f}")
                return formatted

            gain_col, loss_col = st.columns(2)

            top_gains = equity_df.sort_values("return_pct", ascending=False).head(5)
            if not top_gains.empty:
                gain_col.markdown(t("results.section.top_gains"))
                gain_col.dataframe(_format_gain_loss(top_gains), use_container_width=True)
            else:
                gain_col.info(t("results.info.no_gain_sessions"))

            top_losses = equity_df.sort_values("return_pct").head(5)
            if not top_losses.empty:
                loss_col.markdown(t("results.section.top_losses"))
                loss_col.dataframe(_format_gain_loss(top_losses), use_container_width=True)
            else:
                loss_col.info(t("results.info.no_loss_sessions"))

        else:
            st.info(t("results.info.no_equity"))

    with metrics_tab:
        st.subheader(t("results.tabs.metrics_header"))

        label_map = {
            "tot_return": t("results.metric.total_return"),
            "cagr": t("results.metric.cagr"),
            "max_dd": t("results.metric.max_dd"),
            "sharpe": t("results.metric.sharpe"),
            "sortino": t("results.metric.sortino"),
            "calmar": t("results.metric.calmar"),
            "excess_return": t("results.metric.excess_return"),
        }

        metrics_rows = []
        for key, label in label_map.items():
            if key not in metrics:
                continue
            value = metrics.get(key)
            if value is None:
                display = "N/A"
            elif key in {"tot_return", "cagr", "max_dd", "excess_return"}:
                display = f"{value * 100:.2f}%"
            else:
                display = f"{value:.3f}"
            metrics_rows.append(
                {
                    t("results.table.metric"): label,
                    t("results.table.value"): display,
                }
            )

        df_metrics = pd.DataFrame(metrics_rows)
        st.dataframe(df_metrics, use_container_width=True)

    with trades_tab:
        st.subheader(t("results.tabs.trades_header"))

        if trade_log:
            trade_df = pd.DataFrame(trade_log)
            trade_df = trade_df.dropna(how="all")

            if not trade_df.empty:
                if "timestamp" in trade_df.columns:
                    trade_df["timestamp"] = pd.to_datetime(trade_df["timestamp"], errors="coerce")
                    trade_df.sort_values("timestamp", inplace=True)

                if "alloc_pct" in trade_df.columns:
                    trade_df["alloc_pct"] = pd.to_numeric(trade_df["alloc_pct"], errors="coerce")
                else:
                    trade_df["alloc_pct"] = pd.NA

                if "portfolio_value" in trade_df.columns:
                    trade_df["portfolio_value"] = pd.to_numeric(
                        trade_df["portfolio_value"], errors="coerce"
                    )
                else:
                    trade_df["portfolio_value"] = pd.NA

                sells = trade_df[trade_df.get("action") == "SELL"].copy()
                realized_trades = sells.dropna(subset=["pnl"])

                total_trades = int(len(trade_df))
                realized_pnl = float(realized_trades["pnl"].sum()) if not realized_trades.empty else 0.0
                win_rate = (
                    float((realized_trades["pnl"] > 0).mean()) if not realized_trades.empty else None
                )
                avg_hold = (
                    float(realized_trades["holding_period"].dropna().mean())
                    if not realized_trades.empty
                    and "holding_period" in realized_trades.columns
                    and not realized_trades["holding_period"].dropna().empty
                    else None
                )

                buy_allocations = trade_df[
                    (trade_df.get("action") == "BUY") & trade_df["alloc_pct"].notna()
                ]["alloc_pct"]
                avg_allocation = float(buy_allocations.mean()) if not buy_allocations.empty else None

                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    st.metric(
                        t("results.trades.metric.trades"),
                        total_trades,
                    )

                with metric_col2:
                    st.metric(
                        t("results.trades.metric.realized"),
                        f"${realized_pnl:,.2f}",
                    )

                with metric_col3:
                    win_display = f"{win_rate * 100:.1f}%" if win_rate is not None else "N/A"
                    st.metric(
                        t("results.trades.metric.win_rate"),
                        win_display,
                    )

                with metric_col4:
                    alloc_display = (
                        f"{avg_allocation * 100:.1f}%" if avg_allocation is not None else "N/A"
                    )
                    st.metric(
                        t("results.trades.metric.avg_allocation"),
                        alloc_display,
                    )

                if avg_hold is not None:
                    st.caption(
                        t(
                            "results.trades.caption.avg_hold",
                            bars=f"{avg_hold:.1f}",
                        )
                    )

                formatted = trade_df.copy()
                if "timestamp" in formatted.columns:
                    formatted["timestamp"] = formatted["timestamp"].apply(
                        lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else "—"
                    )

                if "pnl_pct" in formatted.columns:
                    formatted["pnl_pct"] = formatted["pnl_pct"].apply(
                        lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "—"
                    )

                if "alloc_pct" in formatted.columns:
                    formatted["alloc_pct"] = formatted["alloc_pct"].apply(
                        lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "—"
                    )

                money_cols = ["price", "value", "pnl", "commission"]
                for col in money_cols:
                    if col in formatted.columns:
                        formatted[col] = formatted[col].apply(
                            lambda x: f"${x:,.2f}" if pd.notnull(x) else "—"
                        )

                if "size" in formatted.columns:
                    formatted["size"] = formatted["size"].apply(
                        lambda x: int(x) if pd.notnull(x) else "—"
                    )

                if "holding_period" in formatted.columns:
                    formatted["holding_period"] = formatted["holding_period"].apply(
                        lambda x: f"{int(x)}" if pd.notnull(x) else "—"
                    )

                column_map = {
                    "timestamp": t("results.trades.column.timestamp"),
                    "symbol": t("results.trades.column.symbol"),
                    "action": t("results.trades.column.action"),
                    "size": t("results.trades.column.size"),
                    "price": t("results.trades.column.price"),
                    "value": t("results.trades.column.value"),
                    "commission": t("results.trades.column.commission"),
                    "pnl": t("results.trades.column.pnl"),
                    "pnl_pct": t("results.trades.column.pnl_pct"),
                    "alloc_pct": t("results.trades.column.alloc_pct"),
                    "holding_period": t("results.trades.column.holding"),
                    "reason": t("results.trades.column.reason"),
                }

                available_columns = [col for col in column_map.keys() if col in formatted.columns]

                st.dataframe(
                    formatted[available_columns].rename(columns=column_map),
                    use_container_width=True,
                )
            else:
                st.info(t("results.trades.no_data"))
        else:
            st.info(t("results.trades.no_data"))

    with benchmark_tab:
        st.subheader(t("results.tabs.benchmark_header"))

        benchmarks = json.loads(backtest["benchmarks"]) if backtest.get("benchmarks") else []

        if benchmarks:
            st.write(t("results.text.benchmarks", benchmarks=", ".join(benchmarks)))

            start_date = backtest["start"]
            end_date = backtest["end"]

            comparison_data = []
            total_return = metrics.get("tot_return", 0)

            for benchmark in benchmarks:
                bench_data = stock_mgr.get_cached_data(benchmark, start_date, end_date)

                if not bench_data.empty:
                    start_price = bench_data["close"].iloc[0]
                    end_price = bench_data["close"].iloc[-1]
                    bench_return = (end_price - start_price) / start_price

                    comparison_data.append(
                        {
                            t("results.benchmark.symbol"): benchmark,
                            t("results.metric.total_return"): f"{bench_return * 100:.2f}%",
                            t("results.benchmark.outperformance"): f"{(total_return - bench_return) * 100:.2f}%",
                        }
                    )

            if comparison_data:
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)
            else:
                st.warning(t("results.warning.no_benchmark_data"))
        else:
            st.info(t("results.info.no_benchmarks"))

    with details_tab:
        st.subheader(t("results.section.configuration"))

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(t("results.config.backtest_id", value=backtest["id"]))
            st.markdown(t("results.config.strategy", value=backtest["strategy_name"]))
            st.markdown(t("results.config.status", value=backtest["status"]))
            st.markdown(t("results.config.created", value=backtest["created_at"]))

        with col2:
            universe = json.loads(backtest["universe"])
            st.markdown(t("results.config.universe", value=", ".join(universe)))
            st.markdown(t("results.config.start", value=backtest["start"]))
            st.markdown(t("results.config.end", value=backtest["end"]))
            st.markdown(
                t(
                    "results.config.initial_cash",
                    value=f"${backtest.get('initial_cash', 0):,.2f}",
                )
            )

        st.divider()
        st.subheader(t("results.section.strategy_definition"))

        strategy_json = json.loads(backtest["strategy_json"])
        st.json(strategy_json)

        st.divider()
        st.subheader(t("results.section.export"))

        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            if st.button(t("results.button.export_json")):
                export_data = {
                    "backtest": dict(backtest),
                    "metrics": dict(metrics) if metrics else {},
                    "strategy": strategy_json,
                }
                st.download_button(
                    t("results.button.download_json"),
                    data=json.dumps(export_data, indent=2),
                    file_name=f"backtest_{bt_id}.json",
                    mime="application/json",
                )

        with exp_col2:
            if st.button(t("results.button.export_metrics")):
                df_metrics_export = pd.DataFrame([metrics]) if metrics else pd.DataFrame()
                st.download_button(
                    t("results.button.download_csv"),
                    data=df_metrics_export.to_csv(index=False),
                    file_name=f"metrics_{bt_id}.csv",
                    mime="text/csv",
                )

        with exp_col3:
            st.info(t("results.info.export_html"))


if __name__ == "__main__":
    show()
