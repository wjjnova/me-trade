"""
Basic tests for Me Trade functionality.
Run with: python -m pytest tests/
"""
import pytest
import pandas as pd
from src.data import StockDataManager
from src.strategy import NLParser, StrategyCompiler, CodeValidator
from src.backtest import MetricsCalculator


class TestDataManager:
    """Test data management functionality."""
    
    def test_stock_manager_initialization(self):
        """Test that stock manager initializes."""
        manager = StockDataManager()
        assert manager is not None
        assert manager.db is not None
    
    def test_get_available_symbols(self):
        """Test retrieving available symbols."""
        manager = StockDataManager()
        symbols = manager.get_available_symbols()
        assert isinstance(symbols, list)


class TestNLParser:
    """Test natural language parser."""
    
    def test_parser_initialization(self):
        """Test parser initializes."""
        parser = NLParser()
        assert parser is not None
    
    def test_basic_parse(self):
        """Test basic strategy parsing."""
        parser = NLParser()
        text = "Buy AAPL when SMA 50 crosses above SMA 200"
        result = parser.parse(text)
        
        assert isinstance(result, dict)
        assert 'name' in result
        assert 'universe' in result
        assert 'entry' in result
        assert 'exit' in result


class TestStrategyCompiler:
    """Test strategy compiler."""
    
    def test_compiler_initialization(self):
        """Test compiler initializes."""
        compiler = StrategyCompiler()
        assert compiler is not None
    
    def test_basic_compilation(self):
        """Test basic strategy compilation."""
        compiler = StrategyCompiler()
        
        strategy = {
            "name": "Test Strategy",
            "universe": ["AAPL"],
            "timeframe": {"start": "2020-01-01", "end": "2021-01-01", "interval": "1d"},
            "entry": [{"type": "indicator", "ind": "SMA", "period": 50, "op": ">", "rhs": {"ind": "SMA", "period": 200}}],
            "exit": [{"type": "trailing_stop", "percent": 0.08}],
            "position": {"sizing": "percent_cash", "value": 0.25},
            "costs": {"commission_per_share": 0.005, "slippage_bps": 5}
        }
        
        code = compiler.compile(strategy)
        
        assert isinstance(code, str)
        assert "import backtrader" in code
        assert "GeneratedStrategy" in code
        assert "def __init__" in code
        assert "def next" in code


class TestCodeValidator:
    """Test code validator."""
    
    def test_validator_initialization(self):
        """Test validator initializes."""
        validator = CodeValidator()
        assert validator is not None
    
    def test_valid_code(self):
        """Test validation of safe code."""
        validator = CodeValidator()
        
        safe_code = """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA()
    
    def next(self):
        if not self.position:
            self.buy()
"""
        
        is_valid, violations = validator.validate_backtrader_strategy(safe_code)
        assert is_valid
        assert len(violations) == 0
    
    def test_invalid_code(self):
        """Test validation catches dangerous code."""
        validator = CodeValidator()
        
        dangerous_code = """
import os

class TestStrategy:
    def next(self):
        os.system('ls')
"""
        
        is_valid, violations = validator.validate(dangerous_code)
        assert not is_valid
        assert len(violations) > 0


class TestMetricsCalculator:
    """Test metrics calculator."""
    
    def test_calculator_initialization(self):
        """Test calculator initializes."""
        calc = MetricsCalculator()
        assert calc is not None
    
    def test_total_return_calculation(self):
        """Test total return calculation."""
        calc = MetricsCalculator()
        
        # Create simple equity curve
        equity = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=100),
            'value': [100000 * (1 + i * 0.001) for i in range(100)]
        })
        
        total_return = calc.total_return(equity)
        
        assert isinstance(total_return, float)
        assert total_return > 0  # Should be positive for this test data
    
    def test_max_drawdown_calculation(self):
        """Test max drawdown calculation."""
        calc = MetricsCalculator()
        
        # Create equity curve with drawdown
        values = [100000, 110000, 105000, 95000, 100000, 120000]
        equity = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=len(values)),
            'value': values
        })
        
        max_dd = calc.max_drawdown(equity)
        
        assert isinstance(max_dd, float)
        assert max_dd <= 0  # Drawdown should be negative


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
