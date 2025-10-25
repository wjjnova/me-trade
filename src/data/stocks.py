"""
Stock data sourcing using yfinance.
Downloads and caches OHLCV data to SQLite.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from src.db import get_db


class StockDataManager:
    """Manager for downloading and caching stock OHLCV data."""
    
    def __init__(self):
        self.db = get_db()
    
    def download_stocks(
        self,
        symbols: List[str],
        start: str,
        end: str,
        interval: str = "1d"
    ) -> dict:
        """Download stock data using yfinance and cache to database.
        
        Args:
            symbols: List of stock ticker symbols
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            interval: Data interval (1d, 1h, 15m, 5m)
            
        Returns:
            Dictionary with success/failure counts and messages
        """
        results = {
            "success": [],
            "failed": [],
            "total_rows": 0
        }
        
        for symbol in symbols:
            try:
                # Download data from yfinance
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start, end=end, interval=interval)
                
                if df.empty:
                    results["failed"].append({
                        "symbol": symbol,
                        "error": "No data returned"
                    })
                    continue
                
                # Prepare data for insertion
                df.reset_index(inplace=True)
                df['symbol'] = symbol
                df['interval'] = interval
                df['source'] = 'yfinance'
                df['asof'] = datetime.now().isoformat()
                
                # Rename columns to match schema
                df.rename(columns={
                    'Date': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                }, inplace=True)
                
                # Convert date to string
                df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                
                # Add adj_close if not present (use close)
                if 'adj_close' not in df.columns:
                    df['adj_close'] = df['close']
                
                # Select only needed columns
                columns = [
                    'symbol', 'date', 'interval', 'open', 'high', 
                    'low', 'close', 'adj_close', 'volume', 'source', 'asof'
                ]
                df = df[columns]
                
                # Insert into database (replace on conflict)
                inserted = self._insert_equity_data(df)
                
                # Calculate and store indicators
                try:
                    from .indicators import IndicatorStorage
                    indicator_storage = IndicatorStorage()
                    
                    # Re-fetch data with proper format for indicator calculation
                    df_for_indicators = self.get_cached_data(symbol, interval=interval)
                    if not df_for_indicators.empty:
                        indicators_inserted = indicator_storage.save_indicators(symbol, df_for_indicators, interval)
                except Exception as ind_error:
                    # Don't fail the whole download if indicators fail
                    print(f"Warning: Failed to calculate indicators for {symbol}: {ind_error}")
                
                results["success"].append({
                    "symbol": symbol,
                    "rows": inserted
                })
                results["total_rows"] += inserted
                
            except Exception as e:
                results["failed"].append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return results
    
    def _insert_equity_data(self, df: pd.DataFrame) -> int:
        """Insert equity data into database.
        
        Args:
            df: DataFrame with equity data
            
        Returns:
            Number of rows inserted
        """
        conn = self.db.connect()
        
        # Use INSERT OR REPLACE for upsert behavior
        query = """
            INSERT OR REPLACE INTO equities_ohlcv 
            (symbol, date, interval, open, high, low, close, adj_close, volume, source, asof)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = conn.cursor()
        rows_inserted = 0
        
        for _, row in df.iterrows():
            cursor.execute(query, (
                row['symbol'],
                row['date'],
                row['interval'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['adj_close'],
                row['volume'],
                row['source'],
                row['asof']
            ))
            rows_inserted += 1
        
        conn.commit()
        return rows_inserted
    
    def get_cached_data(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Retrieve cached stock data from database.
        
        Args:
            symbol: Stock ticker symbol
            start: Optional start date filter
            end: Optional end date filter
            interval: Data interval
            
        Returns:
            DataFrame with cached data
        """
        query = """
            SELECT symbol, date, open, high, low, close, adj_close, volume
            FROM equities_ohlcv
            WHERE symbol = ? AND interval = ?
        """
        params = [symbol, interval]
        
        if start:
            query += " AND date >= ?"
            params.append(start)
        
        if end:
            query += " AND date <= ?"
            params.append(end)
        
        query += " ORDER BY date"
        
        rows = self.db.fetchall(query, tuple(params))
        df = pd.DataFrame(rows)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_available_symbols(self) -> List[str]:
        """Get list of symbols with cached data.
        
        Returns:
            List of unique symbols
        """
        query = "SELECT DISTINCT symbol FROM equities_ohlcv ORDER BY symbol"
        rows = self.db.fetchall(query)
        return [row['symbol'] for row in rows]
    
    def get_row_count(self, symbol: str, interval: str = "1d") -> int:
        """Return number of cached rows for a symbol/interval."""
        result = self.db.fetchone(
            "SELECT COUNT(*) AS count FROM equities_ohlcv WHERE symbol = ? AND interval = ?",
            (symbol, interval),
        )
        return result["count"] if result else 0

    def get_date_range(self, symbol: str, interval: str = "1d") -> Optional[dict]:
        """Get date range for cached symbol data.
        
        Args:
            symbol: Stock ticker symbol
            interval: Data interval
            
        Returns:
            Dictionary with min and max dates, or None if no data
        """
        query = """
            SELECT MIN(date) as min_date, MAX(date) as max_date, COUNT(*) as count
            FROM equities_ohlcv
            WHERE symbol = ? AND interval = ?
        """
        result = self.db.fetchone(query, (symbol, interval))
        
        if result and result['count'] > 0:
            return {
                "min_date": result['min_date'],
                "max_date": result['max_date'],
                "count": result['count']
            }
        return None

    def get_paginated_data(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 100,
        offset: int = 0,
        descending: bool = True,
    ) -> pd.DataFrame:
        """Retrieve cached data with pagination support."""

        order = "DESC" if descending else "ASC"
        query = (
            "SELECT date, open, high, low, close, adj_close, volume "
            "FROM equities_ohlcv WHERE symbol = ? AND interval = ? "
            f"ORDER BY date {order} LIMIT ? OFFSET ?"
        )
        rows = self.db.fetchall(query, (symbol, interval, limit, offset))
        df = pd.DataFrame(rows)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])

        return df

    def delete_symbol(self, symbol: str) -> dict:
        """Delete all cached data and indicators for a symbol."""

        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM equities_ohlcv WHERE symbol = ?", (symbol,))
        equity_rows = cursor.rowcount or 0

        cursor.execute("DELETE FROM technical_indicators WHERE symbol = ?", (symbol,))
        indicator_rows = cursor.rowcount or 0

        conn.commit()

        return {
            "equity_rows": equity_rows,
            "indicator_rows": indicator_rows,
        }

    def delete_all(self) -> dict:
        """Purge all equity data and related indicators."""

        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM equities_ohlcv")
        equity_rows = cursor.rowcount or 0

        cursor.execute("DELETE FROM technical_indicators")
        indicator_rows = cursor.rowcount or 0

        conn.commit()

        return {
            "equity_rows": equity_rows,
            "indicator_rows": indicator_rows,
        }

    def download_latest(
        self,
        symbols: List[str],
        interval: str = "1d",
        default_start: str = "2019-01-01",
    ) -> dict:
        """Download only the latest data since the last cached date for each symbol."""

        end_date = datetime.now().strftime("%Y-%m-%d")
        results = {
            "success": [],
            "failed": [],
            "total_rows": 0,
            "skipped": [],
        }

        try:
            default_start_dt = datetime.strptime(default_start, "%Y-%m-%d")
        except ValueError:
            default_start_dt = datetime(2019, 1, 1)

        for symbol in symbols:
            start_dt = default_start_dt
            range_info = self.get_date_range(symbol, interval)

            if range_info and range_info.get("max_date"):
                try:
                    last_date = datetime.strptime(range_info["max_date"], "%Y-%m-%d")
                    start_dt = last_date + timedelta(days=1)
                except ValueError:
                    start_dt = default_start_dt

            start_str = start_dt.strftime("%Y-%m-%d")

            if start_str > end_date:
                results["skipped"].append(symbol)
                continue

            partial = self.download_stocks([symbol], start=start_str, end=end_date, interval=interval)

            results["success"].extend(partial.get("success", []))
            results["failed"].extend(partial.get("failed", []))
            results["total_rows"] += partial.get("total_rows", 0)

        return results
    
    def upload_csv(
        self,
        csv_path: str,
        symbol: str,
        interval: str = "1d"
    ) -> dict:
        """Upload custom CSV data to database.
        
        Expected CSV columns: date, open, high, low, close, volume
        Optional: adj_close
        
        Args:
            csv_path: Path to CSV file
            symbol: Stock ticker symbol
            interval: Data interval
            
        Returns:
            Dictionary with upload results
        """
        try:
            df = pd.read_csv(csv_path)
            
            # Validate required columns
            required = ['date', 'open', 'high', 'low', 'close', 'volume']
            missing = [col for col in required if col not in df.columns]
            if missing:
                return {
                    "success": False,
                    "error": f"Missing required columns: {missing}"
                }
            
            # Add metadata
            df['symbol'] = symbol
            df['interval'] = interval
            df['source'] = 'csv_upload'
            df['asof'] = datetime.now().isoformat()
            
            # Add adj_close if missing
            if 'adj_close' not in df.columns:
                df['adj_close'] = df['close']
            
            # Ensure date is string format
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # Insert data
            inserted = self._insert_equity_data(df)
            
            return {
                "success": True,
                "symbol": symbol,
                "rows": inserted
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
