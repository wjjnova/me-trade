"""
Backtrader execution engine.
Runs strategies with Backtrader, configures cerebro, applies costs.
"""
import backtrader as bt
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os
from src.data import StockDataManager
from src.db import get_db
import config


class BacktestEngine:
    """Execute backtests using Backtrader."""
    
    def __init__(self):
        self.stock_manager = StockDataManager()
        self.db = get_db()
    
    def run_backtest(
        self,
        strategy_code: str,
        universe: list,
        start: str,
        end: str,
        initial_cash: float = 100000.0,
        commission: float = 0.005,
        slippage_bps: float = 5.0
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
            df = self.stock_manager.get_cached_data(symbol, start, end)
            
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
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Backtest execution failed: {str(e)}"
            }
    
    def _create_data_feed(self, df: pd.DataFrame, name: str) -> Optional[bt.feeds.PandasData]:
        """Create Backtrader data feed from DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
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
            
            # Create data feed
            data = bt.feeds.PandasData(
                dataname=df,
                datetime=None,  # Use index
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=-1
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
