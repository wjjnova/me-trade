"""
Database schema initialization for Me Trade.
Creates and manages all SQLite tables.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from src import config
from src.models import Strategy as StrategyModel
from src.strategy import StrategyCompiler


class Database:
    """SQLite database manager for Me Trade."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. Defaults to config.DB_PATH.
        """
        self.db_path = db_path or config.DB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection with WAL mode."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize_schema(self):
        """Create all tables and indexes if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Equities OHLCV table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equities_ohlcv (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                interval TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adj_close REAL,
                volume INTEGER,
                source TEXT,
                asof TEXT,
                PRIMARY KEY (symbol, date, interval)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_equities_symbol_date 
            ON equities_ohlcv(symbol, date)
        """)
        
        # Options chain table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options_chain (
                symbol TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                expiration TEXT NOT NULL,
                right TEXT NOT NULL,
                strike REAL NOT NULL,
                bid REAL,
                ask REAL,
                last REAL,
                mid REAL,
                volume INTEGER,
                open_interest INTEGER,
                implied_vol REAL,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                rho REAL,
                underlying_price REAL,
                source TEXT,
                asof TEXT,
                PRIMARY KEY (symbol, trade_date, expiration, right, strike)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_options_symbol_trade 
            ON options_chain(symbol, trade_date)
        """)

        # Ensure greek columns exist for legacy databases
        existing_columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(options_chain)")
        }
        for column, col_type in [
            ("delta", "REAL"),
            ("gamma", "REAL"),
            ("theta", "REAL"),
            ("vega", "REAL"),
            ("rho", "REAL"),
        ]:
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE options_chain ADD COLUMN {column} {col_type}")
        
        # Options volatility table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options_volatility (
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                hv_current REAL,
                hv_week_ago REAL,
                hv_month_ago REAL,
                hv_year_high REAL,
                hv_year_high_date TEXT,
                hv_year_low REAL,
                hv_year_low_date TEXT,
                iv_current REAL,
                iv_week_ago REAL,
                iv_month_ago REAL,
                iv_year_high REAL,
                iv_year_high_date TEXT,
                iv_year_low REAL,
                iv_year_low_date TEXT,
                source TEXT,
                asof TEXT,
                PRIMARY KEY (symbol, date)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_volatility_symbol_date 
            ON options_volatility(symbol, date)
        """)
        
        # Technical indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technical_indicators (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                interval TEXT NOT NULL,
                sma_20 REAL,
                sma_50 REAL,
                sma_200 REAL,
                ema_12 REAL,
                ema_26 REAL,
                rsi_14 REAL,
                macd REAL,
                macd_signal REAL,
                macd_histogram REAL,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                calculated_at TEXT NOT NULL,
                PRIMARY KEY (symbol, date, interval)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_indicators_symbol_date 
            ON technical_indicators(symbol, date)
        """)
        
        # Strategies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version INTEGER NOT NULL,
                json TEXT NOT NULL,
                human_readable TEXT,
                json_definition TEXT,
                backtrader_code TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Add new columns to existing strategies table for legacy support
        existing_strategy_columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(strategies)")
        }
        for column in ["human_readable", "json_definition", "backtrader_code"]:
            if column not in existing_strategy_columns:
                cursor.execute(f"ALTER TABLE strategies ADD COLUMN {column} TEXT")
        
        # Generated code table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(strategy_id) REFERENCES strategies(id)
            )
        """)
        
        # Backtests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL,
                code_id TEXT NOT NULL,
                universe TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                initial_cash REAL NOT NULL,
                benchmarks TEXT,
                status TEXT NOT NULL,
                artifacts TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(strategy_id) REFERENCES strategies(id),
                FOREIGN KEY(code_id) REFERENCES codes(id)
            )
        """)
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics_run (
                bt_id TEXT PRIMARY KEY,
                tot_return REAL,
                cagr REAL,
                max_dd REAL,
                sharpe REAL,
                sortino REAL,
                calmar REAL,
                excess_return REAL,
                benchmarks TEXT,
                FOREIGN KEY(bt_id) REFERENCES backtests(id)
            )
        """)

        # LLM configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                api_key TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_llm_configs_active 
            ON llm_configs(is_active)
        """)
        
        # Equity curve table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_curves (
                bt_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                cash REAL,
                pnl REAL,
                return_pct REAL,
                PRIMARY KEY (bt_id, timestamp),
                FOREIGN KEY(bt_id) REFERENCES backtests(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_equity_curves_bt_id
            ON equity_curves(bt_id)
        """)
        
        conn.commit()
        self._seed_default_strategies(conn)
        print(f"Database initialized at {self.db_path}")
    
    def execute(self, query: str, params: tuple = ()):
        """Execute a query and return cursor.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Cursor with results
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def fetchall(self, query: str, params: tuple = ()) -> list:
        """Execute query and fetch all results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of row dictionaries
        """
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[dict]:
        """Execute query and fetch one result.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Row dictionary or None
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def _seed_default_strategies(self, conn: sqlite3.Connection):
        """Populate database with built-in strategy templates."""
        defaults = [
            {
                "id": "builtin_sma_golden_cross",
                "name": "SMA Golden Cross",
                "version": 2,
                "strategy": {
                    "name": "SMA Golden Cross",
                    "universe": ["AAPL", "MSFT", "GOOGL"],
                    "timeframe": {
                        "start": "2018-01-01",
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
                            "rhs": 65
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
                        "slippage_bps": 5.0
                    }
                }
            },
            {
                "id": "builtin_rsi_mean_reversion",
                "name": "RSI Mean Reversion",
                "version": 2,
                "strategy": {
                    "name": "RSI Mean Reversion",
                    "universe": ["SPY"],
                    "timeframe": {
                        "start": "2017-01-01",
                        "end": "2024-12-31",
                        "interval": "1d"
                    },
                    "entry": [
                        {
                            "type": "indicator",
                            "ind": "RSI",
                            "period": 14,
                            "op": "<",
                            "rhs": 30
                        },
                        {
                            "type": "indicator",
                            "ind": "SMA",
                            "period": 20,
                            "op": "<",
                            "rhs": {"ind": "SMA", "period": 50}
                        }
                    ],
                    "exit": [
                        {"type": "take_profit", "percent": 0.12},
                        {"type": "stop_loss", "percent": 0.06}
                    ],
                    "position": {
                        "sizing": "percent_cash",
                        "value": 0.5,
                        "max_positions": 2
                    },
                    "costs": {
                        "commission_per_share": 0.001,
                        "slippage_bps": 3.0
                    }
                }
            },
            {
                "id": "builtin_ema_macd_trend",
                "name": "EMA MACD Trend",
                "version": 2,
                "strategy": {
                    "name": "EMA MACD Trend",
                    "universe": ["QQQ", "NVDA"],
                    "timeframe": {
                        "start": "2019-01-01",
                        "end": "2024-12-31",
                        "interval": "1d"
                    },
                    "entry": [
                        {
                            "type": "indicator",
                            "ind": "EMA",
                            "period": 12,
                            "op": ">",
                            "rhs": {"ind": "EMA", "period": 26}
                        },
                        {
                            "type": "indicator",
                            "ind": "MACD",
                            "op": ">",
                            "rhs": 0
                        }
                    ],
                    "exit": [
                        {"type": "trailing_stop", "percent": 0.1},
                        {"type": "stop_loss", "percent": 0.07}
                    ],
                    "position": {
                        "sizing": "percent_cash",
                        "value": 0.33,
                        "max_positions": 3
                    },
                    "costs": {
                        "commission_per_share": 0.0025,
                        "slippage_bps": 4.0
                    }
                }
            }
        ]

        compiler = StrategyCompiler()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        changes = False

        for default in defaults:
            strategy_payload = default["strategy"]
            try:
                StrategyModel(**strategy_payload)
            except Exception as exc:
                print(f"Skipping default strategy '{default['name']}' due to validation error: {exc}")
                continue

            strategy_id = default["id"]
            version = default.get("version", 1)
            existing_row = cursor.execute(
                "SELECT version FROM strategies WHERE id = ?",
                (strategy_id,)
            ).fetchone()

            existing_version = None
            if existing_row is not None:
                if isinstance(existing_row, sqlite3.Row):
                    existing_version = existing_row["version"]
                else:
                    existing_version = existing_row[0]

            if existing_version is None or existing_version < version:
                cursor.execute(
                    """INSERT OR REPLACE INTO strategies (id, name, version, json, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                    (
                        strategy_id,
                        default["name"],
                        version,
                        json.dumps(strategy_payload),
                        now
                    )
                )
                changes = True

            code_id = f"{strategy_id}_code"
            code_exists = cursor.execute(
                "SELECT id FROM codes WHERE id = ?",
                (code_id,)
            ).fetchone()

            needs_code_refresh = (
                existing_version is None or existing_version < version or code_exists is None
            )

            if needs_code_refresh:
                code_text = compiler.compile(strategy_payload)
                cursor.execute(
                    """INSERT OR REPLACE INTO codes (id, strategy_id, language, code, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                    (
                        code_id,
                        strategy_id,
                        'python',
                        code_text,
                        now
                    )
                )
                changes = True

        if changes:
            conn.commit()


# Global database instance
_db = None

def get_db() -> Database:
    """Get or create global database instance."""
    global _db
    if _db is None:
        _db = Database()
        _db.initialize_schema()
    return _db
