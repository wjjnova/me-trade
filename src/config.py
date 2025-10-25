# Me Trade Configuration
import os
from pathlib import Path


# Resolve project root one level above the src package
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DB_PATH = str(BASE_DIR / "data" / "metrade.db")

# File storage
FILES_DIR = str(BASE_DIR / "files")

# Default symbols for initial download
DEFAULT_SYMBOLS = [
    "MSFT", "PATH", "GOOGL", "TSLA", "COST", 
    "NVDA", "META", "NFLX", "AMZN", "VOO", "AAPL", "BABA"
]

# Benchmark symbols
BENCHMARK_SYMBOLS = ["VOO", "SPY", "QQQ"]

# Backtest defaults
DEFAULT_INITIAL_CASH = 100000.0
DEFAULT_COMMISSION = 0.005  # per share
DEFAULT_SLIPPAGE_BPS = 5  # basis points

# Execution limits
MAX_BACKTEST_RUNTIME = 300  # seconds (5 minutes)
