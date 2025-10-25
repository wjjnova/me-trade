"""
Database schema initialization for Me-Trade.
Creates and manages all SQLite tables.
"""
import sqlite3
from pathlib import Path
from typing import Optional
import config


class Database:
    """SQLite database manager for Me-Trade."""
    
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
        
        # Strategies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version INTEGER NOT NULL,
                json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
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
        
        conn.commit()
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


# Global database instance
_db = None

def get_db() -> Database:
    """Get or create global database instance."""
    global _db
    if _db is None:
        _db = Database()
        _db.initialize_schema()
    return _db
