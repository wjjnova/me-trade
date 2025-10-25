"""
Backtrader execution engine.
Runs strategies with Backtrader, configures cerebro, applies costs.
"""
import backtrader as bt
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import os
from src.data import StockDataManager, IndicatorStorage
from src.db import get_db
from src import config


class EquityCurveAnalyzer(bt.Analyzer):
    """Collect portfolio value over time during a backtest."""

    def __init__(self):
        super().__init__()
        self.records: List[Dict[str, Any]] = []
        self.prev_value: Optional[float] = None
        self.starting_value: Optional[float] = None

    def start(self):
        self.records = []
        self.prev_value = None
        self.starting_value = float(self.strategy.broker.getvalue())

    def next(self):
        try:
            dt = self.strategy.datetime.datetime(0)
        except AttributeError:
            dt = None

        if dt is None:
            try:
                dt = self.strategy.datetime.date(0)
            except AttributeError:
                dt = None

        if dt is None:
            return

        if hasattr(dt, "to_pydatetime"):
            dt = dt.to_pydatetime()

        if hasattr(dt, "replace"):
            dt = dt.replace(tzinfo=None)

        value = float(self.strategy.broker.getvalue())
        cash = float(self.strategy.broker.getcash())
        starting = self.starting_value or value
        pnl = value - starting
        if self.prev_value is None or self.prev_value == 0:
            ret = 0.0
        else:
            ret = (value / self.prev_value) - 1.0

        self.records.append({
            "timestamp": dt.isoformat() if hasattr(dt, "isoformat") else str(dt),
            "value": value,
            "cash": cash,
            "pnl": pnl,
            "return_pct": ret,
        })

        self.prev_value = value

    def get_analysis(self):
        return self.records


class BacktestEngine:
    """Execute backtests using Backtrader."""
    
    def __init__(self):
        self.stock_manager = StockDataManager()
        self.indicator_storage = IndicatorStorage()
        self.db = get_db()
    
    def run_backtest(
        self,
        strategy_code: str,
        universe: list,
        start: str,
        end: str,
        initial_cash: float = 100000.0,
        commission: float = 0.005,
        slippage_bps: float = 5.0,
        backtest_id: Optional[str] = None,
        capture_equity: bool = True
    ) -> Dict[str, Any]:
        """Run a backtest with given strategy code.
        
        Args:
            strategy_code: Python code defining Backtrader strategy
            universe: List of symbols to trade
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            initial_cash: Initial capital
            commission: Commission per share
            slippage_bps: Slippage in basis points
            
        Returns:
            Dictionary with results
        """
        # Create Cerebro engine
        cerebro = bt.Cerebro()
        
        # Set initial cash
        cerebro.broker.setcash(initial_cash)
        
        # Set commission
        cerebro.broker.setcommission(commission=commission)
        
        # Add slippage (using FixedPerc slippage)
        slippage_pct = slippage_bps / 10000.0
        cerebro.broker.set_slippage_perc(slippage_pct)
        
        # Load and add data feeds for each symbol
        data_feeds_loaded = 0
        for symbol in universe:
            # Get OHLCV data with indicators
            df = self.indicator_storage.get_indicators_with_ohlcv(symbol, start, end)
            
            if df.empty:
                print(f"Warning: No data for {symbol}, skipping")
                continue
            
            # Convert DataFrame to Backtrader data feed
            data = self._create_data_feed(df, symbol)
            if data is not None:
                cerebro.adddata(data, name=symbol)
                data_feeds_loaded += 1
        
        if data_feeds_loaded == 0:
            return {
                "success": False,
                "error": "No data feeds could be loaded"
            }
        
        # Compile and add strategy
        try:
            strategy_class = self._compile_strategy(strategy_code)
            cerebro.addstrategy(strategy_class)
        except Exception as e:
            return {
                "success": False,
                "error": f"Strategy compilation failed: {str(e)}"
            }
        
        # Add analyzers
        if capture_equity:
            cerebro.addanalyzer(EquityCurveAnalyzer, _name='equity_curve')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # Run backtest
        try:
            starting_value = cerebro.broker.getvalue()
            results = cerebro.run()
            ending_value = cerebro.broker.getvalue()
            
            # Extract strategy and analyzers
            strat = results[0]
            
            equity_records: List[Dict[str, Any]] = []
            if capture_equity:
                equity_records = strat.analyzers.equity_curve.get_analysis()
                if backtest_id and equity_records:
                    self._store_equity_curve(backtest_id, equity_records)

            trade_log: List[Dict[str, Any]] = []
            if hasattr(strat, 'trade_log'):
                trade_log = list(strat.trade_log)
            if backtest_id:
                self._update_backtest_artifacts(backtest_id, trade_log)

            return {
                "success": True,
                "starting_value": starting_value,
                "ending_value": ending_value,
                "total_return": (ending_value - starting_value) / starting_value,
                "analyzers": {
                    "returns": self._extract_returns(strat.analyzers.returns),
                    "sharpe": self._extract_sharpe(strat.analyzers.sharpe),
                    "drawdown": self._extract_drawdown(strat.analyzers.drawdown),
                    "trades": self._extract_trades(strat.analyzers.trades)
                },
                "equity_curve": equity_records,
                "trade_log": trade_log,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Backtest execution failed: {str(e)}"
            }

    def _store_equity_curve(self, bt_id: str, equity_records: List[Dict[str, Any]]):
        """Persist equity curve samples for a completed backtest."""
        conn = self.db.connect()
        cursor = conn.cursor()
        rows = [
            (
                bt_id,
                record.get("timestamp"),
                record.get("value"),
                record.get("cash"),
                record.get("pnl"),
                record.get("return_pct"),
            )
            for record in equity_records
            if record.get("timestamp") is not None
        ]

        if not rows:
            return

        cursor.executemany(
            """INSERT OR REPLACE INTO equity_curves
                   (bt_id, timestamp, value, cash, pnl, return_pct)
                   VALUES (?, ?, ?, ?, ?, ?)""",
            rows
        )
        conn.commit()

    def _update_backtest_artifacts(self, bt_id: str, trade_log: List[Dict[str, Any]]):
        """Update backtest artifacts with captured trade log."""
        conn = self.db.connect()
        cursor = conn.cursor()

        existing = cursor.execute(
            "SELECT artifacts FROM backtests WHERE id = ?",
            (bt_id,),
        ).fetchone()

        artifacts: Dict[str, Any] = {}
        if existing:
            raw = existing[0] if isinstance(existing, tuple) else existing[0]
            if isinstance(existing, dict):
                raw = existing.get('artifacts')
            if raw:
                try:
                    artifacts = json.loads(raw)
                except Exception:
                    artifacts = {}

        artifacts['trade_log'] = trade_log

        cursor.execute(
            "UPDATE backtests SET artifacts = ? WHERE id = ?",
            (json.dumps(artifacts), bt_id),
        )
        conn.commit()
    
    def _create_data_feed(self, df: pd.DataFrame, name: str) -> Optional[bt.feeds.PandasData]:
        """Create Backtrader data feed from DataFrame with indicators.
        
        Args:
            df: DataFrame with OHLCV + indicator data
            name: Symbol name
            
        Returns:
            Backtrader data feed or None
        """
        try:
            # Ensure date is datetime and set as index
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            # Sort by date
            df.sort_index(inplace=True)
            
            # Define custom data feed class that includes indicators
            class IndicatorDataFeed(bt.feeds.PandasData):
                # Add indicator lines
                lines = ('sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'rsi_14',
                        'macd', 'macd_signal', 'macd_histogram',
                        'bb_upper', 'bb_middle', 'bb_lower',)
                
                params = (
                    ('sma_20', -1),
                    ('sma_50', -1),
                    ('sma_200', -1),
                    ('ema_12', -1),
                    ('ema_26', -1),
                    ('rsi_14', -1),
                    ('macd', -1),
                    ('macd_signal', -1),
                    ('macd_histogram', -1),
                    ('bb_upper', -1),
                    ('bb_middle', -1),
                    ('bb_lower', -1),
                )
            
            # Create data feed with indicators
            data = IndicatorDataFeed(
                dataname=df,
                datetime=None,  # Use index
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=-1,
                sma_20='sma_20' if 'sma_20' in df.columns else -1,
                sma_50='sma_50' if 'sma_50' in df.columns else -1,
                sma_200='sma_200' if 'sma_200' in df.columns else -1,
                ema_12='ema_12' if 'ema_12' in df.columns else -1,
                ema_26='ema_26' if 'ema_26' in df.columns else -1,
                rsi_14='rsi_14' if 'rsi_14' in df.columns else -1,
                macd='macd' if 'macd' in df.columns else -1,
                macd_signal='macd_signal' if 'macd_signal' in df.columns else -1,
                macd_histogram='macd_histogram' if 'macd_histogram' in df.columns else -1,
                bb_upper='bb_upper' if 'bb_upper' in df.columns else -1,
                bb_middle='bb_middle' if 'bb_middle' in df.columns else -1,
                bb_lower='bb_lower' if 'bb_lower' in df.columns else -1,
            )
            
            return data
        
        except Exception as e:
            print(f"Error creating data feed for {name}: {e}")
            return None
    
    def _compile_strategy(self, code: str):
        """Compile strategy code into executable class.
        
        Args:
            code: Python code string
            
        Returns:
            Strategy class
        """
        # Create namespace for exec
        namespace = {'bt': bt}
        
        # Execute code to define strategy class
        exec(code, namespace)
        
        # Find and return the strategy class
        for name, obj in namespace.items():
            if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj != bt.Strategy:
                return obj
        
        raise ValueError("No valid Backtrader strategy class found in code")
    
    def _extract_returns(self, analyzer) -> dict:
        """Extract returns analysis.
        
        Args:
            analyzer: Returns analyzer
            
        Returns:
            Dictionary with returns metrics
        """
        try:
            analysis = analyzer.get_analysis()
            return {
                "total_return": analysis.get('rtot', 0.0),
                "avg_return": analysis.get('ravg', 0.0)
            }
        except:
            return {}
    
    def _extract_sharpe(self, analyzer) -> dict:
        """Extract Sharpe ratio.
        
        Args:
            analyzer: Sharpe analyzer
            
        Returns:
            Dictionary with Sharpe ratio
        """
        try:
            analysis = analyzer.get_analysis()
            return {
                "sharpe_ratio": analysis.get('sharperatio', 0.0)
            }
        except:
            return {}
    
    def _extract_drawdown(self, analyzer) -> dict:
        """Extract drawdown metrics.
        
        Args:
            analyzer: DrawDown analyzer
            
        Returns:
            Dictionary with drawdown metrics
        """
        try:
            analysis = analyzer.get_analysis()
            return {
                "max_drawdown": analysis.get('max', {}).get('drawdown', 0.0),
                "max_drawdown_pct": analysis.get('max', {}).get('drawdown', 0.0) / 100.0
            }
        except:
            return {}
    
    def _extract_trades(self, analyzer) -> dict:
        """Extract trade statistics.
        
        Args:
            analyzer: TradeAnalyzer
            
        Returns:
            Dictionary with trade stats
        """
        try:
            analysis = analyzer.get_analysis()
            return {
                "total_trades": analysis.get('total', {}).get('total', 0),
                "won_trades": analysis.get('won', {}).get('total', 0),
                "lost_trades": analysis.get('lost', {}).get('total', 0)
            }
        except:
            return {}
    
    def save_equity_curve(self, cerebro: bt.Cerebro, filepath: str):
        """Save equity curve to CSV.
        
        Args:
            cerebro: Cerebro instance after run
            filepath: Path to save CSV
        """
        # This would require tracking portfolio value over time
        # For now, placeholder
        pass
