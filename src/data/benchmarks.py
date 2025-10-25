"""
Benchmark data manager for downloading market indices.
Downloads VOO, SPY, QQQ for performance comparison.
"""
from typing import List
from .stocks import StockDataManager


class BenchmarkManager:
    """Manager for benchmark index data."""
    
    def __init__(self):
        self.stock_manager = StockDataManager()
        self.default_benchmarks = ["VOO", "SPY", "QQQ"]
    
    def download_benchmarks(
        self,
        start: str,
        end: str,
        benchmarks: List[str] = None,
        interval: str = "1d"
    ) -> dict:
        """Download benchmark data.
        
        Args:
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            benchmarks: List of benchmark symbols (defaults to VOO, SPY, QQQ)
            interval: Data interval
            
        Returns:
            Dictionary with download results
        """
        if benchmarks is None:
            benchmarks = self.default_benchmarks
        
        return self.stock_manager.download_stocks(
            symbols=benchmarks,
            start=start,
            end=end,
            interval=interval
        )
    
    def get_benchmark_data(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "1d"
    ):
        """Get cached benchmark data.
        
        Args:
            symbol: Benchmark symbol
            start: Start date
            end: End date
            interval: Data interval
            
        Returns:
            DataFrame with benchmark data
        """
        return self.stock_manager.get_cached_data(
            symbol=symbol,
            start=start,
            end=end,
            interval=interval
        )
