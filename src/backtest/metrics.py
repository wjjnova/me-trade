"""
Performance metrics calculation.
Computes CAGR, Sharpe, Sortino, Calmar, and excess returns.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime


class MetricsCalculator:
    """Calculate performance metrics for backtests and benchmarks."""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_metrics(
        self,
        equity_curve: pd.DataFrame,
        benchmark_curve: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics.
        
        Args:
            equity_curve: DataFrame with dates and portfolio values
            benchmark_curve: Optional benchmark DataFrame for comparison
            
        Returns:
            Dictionary with all metrics
        """
        if equity_curve.empty:
            return {}
        
        # Calculate returns
        returns = equity_curve['value'].pct_change().dropna()
        
        # Calculate metrics
        metrics = {
            'tot_return': self.total_return(equity_curve),
            'cagr': self.cagr(equity_curve),
            'max_dd': self.max_drawdown(equity_curve),
            'sharpe': self.sharpe_ratio(returns),
            'sortino': self.sortino_ratio(returns),
            'calmar': self.calmar_ratio(equity_curve)
        }
        
        # Calculate excess return if benchmark provided
        if benchmark_curve is not None and not benchmark_curve.empty:
            benchmark_return = self.total_return(benchmark_curve)
            metrics['excess_return'] = metrics['tot_return'] - benchmark_return
        
        return metrics
    
    def total_return(self, equity_curve: pd.DataFrame) -> float:
        """Calculate total return.
        
        Args:
            equity_curve: DataFrame with portfolio values
            
        Returns:
            Total return as decimal (e.g., 0.5 for 50%)
        """
        if equity_curve.empty or len(equity_curve) < 2:
            return 0.0
        
        starting_value = equity_curve['value'].iloc[0]
        ending_value = equity_curve['value'].iloc[-1]
        
        if starting_value == 0:
            return 0.0
        
        return (ending_value - starting_value) / starting_value
    
    def cagr(self, equity_curve: pd.DataFrame) -> float:
        """Calculate Compound Annual Growth Rate.
        
        Args:
            equity_curve: DataFrame with dates and portfolio values
            
        Returns:
            CAGR as decimal
        """
        if equity_curve.empty or len(equity_curve) < 2:
            return 0.0
        
        starting_value = equity_curve['value'].iloc[0]
        ending_value = equity_curve['value'].iloc[-1]
        
        # Calculate years
        if 'date' in equity_curve.columns:
            start_date = pd.to_datetime(equity_curve['date'].iloc[0])
            end_date = pd.to_datetime(equity_curve['date'].iloc[-1])
            years = (end_date - start_date).days / 365.25
        else:
            years = len(equity_curve) / 252  # Assume 252 trading days per year
        
        if years <= 0 or starting_value <= 0:
            return 0.0
        
        cagr = (ending_value / starting_value) ** (1 / years) - 1
        return cagr
    
    def max_drawdown(self, equity_curve: pd.DataFrame) -> float:
        """Calculate maximum drawdown.
        
        Args:
            equity_curve: DataFrame with portfolio values
            
        Returns:
            Maximum drawdown as negative decimal (e.g., -0.2 for -20%)
        """
        if equity_curve.empty:
            return 0.0
        
        values = equity_curve['value']
        cummax = values.cummax()
        drawdown = (values - cummax) / cummax
        
        return drawdown.min()
    
    def sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: Optional[float] = None
    ) -> float:
        """Calculate Sharpe ratio.
        
        Args:
            returns: Series of periodic returns
            risk_free_rate: Annual risk-free rate (uses class default if None)
            
        Returns:
            Annualized Sharpe ratio
        """
        if returns.empty or returns.std() == 0:
            return 0.0
        
        rf = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        
        # Convert annual risk-free rate to daily
        daily_rf = (1 + rf) ** (1/252) - 1
        
        # Calculate excess returns
        excess_returns = returns - daily_rf
        
        # Annualize
        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        
        return sharpe
    
    def sortino_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: Optional[float] = None
    ) -> float:
        """Calculate Sortino ratio (using downside deviation).
        
        Args:
            returns: Series of periodic returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Annualized Sortino ratio
        """
        if returns.empty:
            return 0.0
        
        rf = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        daily_rf = (1 + rf) ** (1/252) - 1
        
        # Calculate downside returns (only negative)
        downside_returns = returns[returns < daily_rf]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        # Calculate excess return
        excess_return = returns.mean() - daily_rf
        
        # Downside deviation
        downside_std = downside_returns.std()
        
        # Annualize
        sortino = (excess_return / downside_std) * np.sqrt(252)
        
        return sortino
    
    def calmar_ratio(self, equity_curve: pd.DataFrame) -> float:
        """Calculate Calmar ratio (CAGR / Max Drawdown).
        
        Args:
            equity_curve: DataFrame with dates and portfolio values
            
        Returns:
            Calmar ratio
        """
        cagr_val = self.cagr(equity_curve)
        max_dd = abs(self.max_drawdown(equity_curve))
        
        if max_dd == 0:
            return 0.0
        
        return cagr_val / max_dd
    
    def calculate_benchmark_metrics(
        self,
        benchmark_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate metrics for benchmark.
        
        Args:
            benchmark_data: DataFrame with benchmark OHLCV data
            
        Returns:
            Dictionary with benchmark metrics
        """
        if benchmark_data.empty:
            return {}
        
        # Create equity curve from close prices
        equity_curve = pd.DataFrame({
            'date': benchmark_data['date'],
            'value': benchmark_data['close']
        })
        
        # Normalize to start at same value as typical backtest
        equity_curve['value'] = equity_curve['value'] / equity_curve['value'].iloc[0] * 100000
        
        return {
            'tot_return': self.total_return(equity_curve),
            'cagr': self.cagr(equity_curve),
            'max_dd': self.max_drawdown(equity_curve)
        }
    
    def compare_to_benchmark(
        self,
        strategy_metrics: Dict[str, float],
        benchmark_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Compare strategy metrics to benchmark.
        
        Args:
            strategy_metrics: Strategy performance metrics
            benchmark_metrics: Benchmark performance metrics
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            'strategy': strategy_metrics,
            'benchmark': benchmark_metrics,
            'outperformance': {}
        }
        
        # Calculate differences
        for key in ['tot_return', 'cagr']:
            if key in strategy_metrics and key in benchmark_metrics:
                comparison['outperformance'][key] = (
                    strategy_metrics[key] - benchmark_metrics[key]
                )
        
        return comparison
