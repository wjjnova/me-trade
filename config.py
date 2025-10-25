# Me-Trade Configuration
import os

# Database
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "metrade.db")

# File storage
FILES_DIR = os.path.join(os.path.dirname(__file__), "files")

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
