"""Backtest execution page."""
import json
import uuid
from datetime import datetime, timedelta

import streamlit as st

from src import config
from src.backtest import BacktestEngine
from src.data import StockDataManager
from src.db import get_db
from src.ui import t, use_language_selector

_STATUS_ICONS = {
    "completed": "✓",
    "running": "⏳",
    "failed": "✗",
    "pending": "○",
}


def show() -> None:
    """Display the backtest page."""
    use_language_selector()

    st.title(t("backtest.title"))
    st.write(t("backtest.subtitle"))

    engine = BacktestEngine()
    db = get_db()
    stock_mgr = StockDataManager()

    strategies = db.fetchall("SELECT id, name FROM strategies ORDER BY created_at DESC")

    if not strategies:
        st.warning(t("backtest.warning.no_strategies"))
        return

    st.subheader(t("backtest.section.select_strategy"))

    strategy_options = {f"{s['name']} ({s['id']})": s['id'] for s in strategies}
    selected_strategy = st.selectbox(
        t("backtest.form.choose_strategy"),
        options=list(strategy_options.keys()),
    )

    strategy_id = strategy_options[selected_strategy]

    strategy_rec = db.fetchone(
        "SELECT json FROM strategies WHERE id = ?",
        (strategy_id,),
    )
    strategy_data = json.loads(strategy_rec["json"])

    code_rec = db.fetchone(
        "SELECT id, code FROM codes WHERE strategy_id = ? ORDER BY created_at DESC LIMIT 1",
        (strategy_id,),
    )

    if not code_rec:
        st.error(t("backtest.error.no_code"))
        return

    code_id = code_rec["id"]

    with st.expander(t("backtest.expander.strategy_details")):
        st.json(strategy_data)

    st.subheader(t("backtest.section.configure"))

    col1, col2 = st.columns(2)

    with col1:
        default_universe = strategy_data.get("universe", ["AAPL"])
        universe_input = st.text_input(
            t("backtest.form.universe"),
            value=", ".join(default_universe),
        )
        universe = [s.strip().upper() for s in universe_input.split(",") if s.strip()]

        available_symbols = stock_mgr.get_available_symbols()
        missing_symbols = [s for s in universe if s not in available_symbols]

        if missing_symbols:
            st.warning(
                t("backtest.warning.missing_data", symbols=", ".join(missing_symbols))
            )
            st.info(t("backtest.info.download_data"))

    timeframe = strategy_data.get("timeframe", {})
    today = datetime.today().date()
    twelve_months_ago = today - timedelta(days=365)

    strategy_start = timeframe.get("start")
    strategy_end = timeframe.get("end")

    if strategy_start:
        try:
            strategy_start_date = datetime.strptime(strategy_start, "%Y-%m-%d").date()
        except ValueError:
            strategy_start_date = None
    else:
        strategy_start_date = None

    if strategy_end:
        try:
            strategy_end_date = datetime.strptime(strategy_end, "%Y-%m-%d").date()
        except ValueError:
            strategy_end_date = None
    else:
        strategy_end_date = None

    default_start = twelve_months_ago
    if strategy_start_date:
        default_start = max(default_start, strategy_start_date)

    default_end = today
    if strategy_end_date:
        default_end = min(default_end, strategy_end_date)

    if default_start > default_end:
        default_start = default_end

    start_date = st.date_input(
        t("common.start_date"),
        value=default_start,
    )

    end_date = st.date_input(
        t("common.end_date"),
        value=default_end,
    )

    with col2:
        initial_cash = st.number_input(
            t("backtest.form.initial_cash"),
            min_value=1000.0,
            value=config.DEFAULT_INITIAL_CASH,
            step=10000.0,
        )

        commission = st.number_input(
            t("backtest.form.commission"),
            min_value=0.0,
            value=config.DEFAULT_COMMISSION,
            step=0.001,
            format="%.4f",
        )

        slippage_bps = st.number_input(
            t("backtest.form.slippage"),
            min_value=0.0,
            value=float(config.DEFAULT_SLIPPAGE_BPS),
            step=1.0,
        )

    st.subheader(t("backtest.section.benchmarks"))

    benchmark_options = config.BENCHMARK_SYMBOLS
    selected_benchmarks = st.multiselect(
        t("backtest.form.compare_against"),
        options=benchmark_options,
        default=["VOO"],
    )

    st.divider()

    if st.button(t("backtest.button.run"), type="primary", disabled=bool(missing_symbols)):
        bt_id = f"bt_{uuid.uuid4().hex[:8]}"

        db.execute(
            """INSERT INTO backtests 
               (id, strategy_id, code_id, universe, start, end, initial_cash, benchmarks, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                bt_id,
                strategy_id,
                code_id,
                json.dumps(universe),
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                initial_cash,
                json.dumps(selected_benchmarks),
                "running",
                datetime.now().isoformat(),
            ),
        )

        with st.spinner(t("backtest.spinner.running")):
            try:
                results = engine.run_backtest(
                    strategy_code=code_rec["code"],
                    universe=universe,
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    initial_cash=initial_cash,
                    commission=commission,
                    slippage_bps=slippage_bps,
                    backtest_id=bt_id,
                )

                if results["success"]:
                    db.execute(
                        "UPDATE backtests SET status = ? WHERE id = ?",
                        ("completed", bt_id),
                    )

                    analyzers = results.get("analyzers", {})
                    sharpe_data = analyzers.get("sharpe", {})
                    dd_data = analyzers.get("drawdown", {})

                    db.execute(
                        """INSERT INTO metrics_run 
                           (bt_id, tot_return, cagr, max_dd, sharpe, sortino, calmar, excess_return, benchmarks)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            bt_id,
                            results["total_return"],
                            None,
                            dd_data.get("max_drawdown_pct", 0),
                            sharpe_data.get("sharpe_ratio", 0),
                            None,
                            None,
                            None,
                            json.dumps({}),
                        ),
                    )

                    st.success(t("backtest.success.completed", bt_id=bt_id))

                    st.subheader(t("backtest.section.results_summary"))

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            t("backtest.metric.starting_value"),
                            f"${results['starting_value']:,.2f}",
                        )

                    with col2:
                        st.metric(
                            t("backtest.metric.ending_value"),
                            f"${results['ending_value']:,.2f}",
                        )

                    with col3:
                        total_return_pct = results["total_return"] * 100
                        st.metric(
                            t("backtest.metric.total_return"),
                            f"{total_return_pct:.2f}%",
                            delta=f"{total_return_pct:.2f}%",
                        )

                    with col4:
                        trades_data = analyzers.get("trades", {})
                        total_trades = trades_data.get("total_trades", 0)
                        st.metric(
                            t("backtest.metric.total_trades"),
                            total_trades,
                        )

                    st.session_state["last_backtest_id"] = bt_id

                    st.info(t("backtest.info.view_results"))

                else:
                    db.execute(
                        "UPDATE backtests SET status = ? WHERE id = ?",
                        ("failed", bt_id),
                    )
                    st.error(
                        t(
                            "backtest.error.failed",
                            message=results.get("error", "Unknown error"),
                        )
                    )

            except Exception as exc:  # noqa: BLE001
                db.execute(
                    "UPDATE backtests SET status = ? WHERE id = ?",
                    ("failed", bt_id),
                )
                st.error(t("backtest.error.exception", message=str(exc)))

    st.divider()
    st.subheader(t("backtest.section.recent"))

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
            status_icon = _STATUS_ICONS.get(bt["status"], "?")
            total_return = bt["tot_return"]
            return_str = f"{total_return*100:.2f}%" if total_return is not None else "N/A"
            st.write(
                t(
                    "backtest.recent.item",
                    status_icon=status_icon,
                    name=bt["name"],
                    bt_id=bt["id"],
                    return_str=return_str,
                    created=bt["created_at"][:10],
                )
            )
    else:
        st.info(t("backtest.info.no_backtests"))


if __name__ == "__main__":
    show()
