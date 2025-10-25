"""
Pydantic models for strategy validation.
Matches the JSON schema from the specification.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class Timeframe(BaseModel):
    """Timeframe configuration."""
    start: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    interval: Literal["1d", "1h", "15m", "5m"] = "1d"


class IndicatorCondition(BaseModel):
    """Indicator-based condition for entry/exit."""
    type: Literal["indicator"] = "indicator"
    ind: str  # SMA, EMA, RSI, MACD, BBANDS, etc.
    period: Optional[int] = None
    op: Optional[str] = None  # >, <, >=, <=, ==
    rhs: Optional[Any] = None  # number or another indicator dict


class StopCondition(BaseModel):
    """Stop loss or take profit condition."""
    type: Literal["trailing_stop", "stop_loss", "take_profit"]
    percent: float


class PositionSizing(BaseModel):
    """Position sizing configuration."""
    sizing: Literal["percent_cash", "fixed"]
    value: float
    max_positions: Optional[int] = None


class TradingCosts(BaseModel):
    """Commission and slippage costs."""
    commission_per_share: float = 0.005
    slippage_bps: float = 5.0


class Strategy(BaseModel):
    """Complete trading strategy definition."""
    name: str
    universe: List[str]
    timeframe: Timeframe
    entry: List[Dict[str, Any]]  # Mix of indicator conditions
    exit: List[Dict[str, Any]]   # Mix of stop conditions
    position: PositionSizing
    costs: TradingCosts
    options: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "SMA Cross with RSI Filter",
                "universe": ["AAPL", "MSFT"],
                "timeframe": {
                    "start": "2019-01-01",
                    "end": "2024-12-31",
                    "interval": "1d"
                },
                "entry": [
                    {
                        "type": "indicator",
                        "ind": "SMA",
                        "period": 50,
                        "op": ">",
                        "rhs": {"ind": "SMA", "period": 200}
                    },
                    {
                        "type": "indicator",
                        "ind": "RSI",
                        "period": 14,
                        "op": "<",
                        "rhs": 60
                    }
                ],
                "exit": [
                    {"type": "trailing_stop", "percent": 0.08},
                    {"type": "take_profit", "percent": 0.2}
                ],
                "position": {
                    "sizing": "percent_cash",
                    "value": 0.25,
                    "max_positions": 4
                },
                "costs": {
                    "commission_per_share": 0.005,
                    "slippage_bps": 5
                }
            }
        }


class BacktestRequest(BaseModel):
    """Request to run a backtest."""
    strategy_id: str
    code_id: Optional[str] = None
    universe: List[str]
    start: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    initial_cash: float = 100000.0
    benchmarks: Optional[List[str]] = ["VOO"]


class PerformanceMetrics(BaseModel):
    """Performance metrics from backtest."""
    tot_return: Optional[float] = None
    cagr: Optional[float] = None
    max_dd: Optional[float] = None
    sharpe: Optional[float] = None
    sortino: Optional[float] = None
    calmar: Optional[float] = None
    excess_return: Optional[float] = None


class BenchmarkPerformance(BaseModel):
    """Benchmark performance metrics."""
    tot_return: Optional[float] = None
    cagr: Optional[float] = None


class BacktestResult(BaseModel):
    """Result of a backtest run."""
    id: str
    strategy_id: str
    code_id: str
    status: Literal["pending", "running", "completed", "failed"]
    performance: Optional[PerformanceMetrics] = None
    benchmarks: Optional[Dict[str, BenchmarkPerformance]] = None
    artifacts: Optional[Dict[str, str]] = None
    created_at: str
    error: Optional[str] = None


class StrategyRecord(BaseModel):
    """Stored strategy record."""
    id: str
    name: str
    version: int
    strategy: Strategy
    created_at: str


class CodeRecord(BaseModel):
    """Generated code record."""
    id: str
    strategy_id: str
    language: str
    code: str
    created_at: str
