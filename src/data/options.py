"""
Options data sourcing using yfinance and local CSV imports.
Downloads and caches option chain data to SQLite.
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd
import yfinance as yf

from src.db import get_db


class OptionsDataManager:
    """Manager for downloading and caching options chain data."""

    DB_COLUMNS: Sequence[str] = (
        "symbol",
        "trade_date",
        "expiration",
        "right",
        "strike",
        "bid",
        "ask",
        "last",
        "mid",
        "volume",
        "open_interest",
        "implied_vol",
        "delta",
        "gamma",
        "theta",
        "vega",
        "rho",
        "underlying_price",
        "source",
        "asof",
    )
    
    def __init__(self):
        self.db = get_db()

    def import_from_directory(self, directory: Path) -> Dict[str, Any]:
        """Import historical option data from CSV files in a directory.

        Files must contain columns matching the Dolt option chain export
        (date, act_symbol, expiration, strike, call_put, bid, ask, vol,
        delta, gamma, theta, vega, rho).

        Args:
            directory: Folder containing CSV files to import.

        Returns:
            Summary dict with row counts and errors.
        """

        directory = Path(directory)
        results: Dict[str, Any] = {"files": 0, "rows": 0, "errors": []}

        if not directory.exists():
            return results

        csv_files = sorted(p for p in directory.glob("*.csv") if p.is_file())
        if not csv_files:
            return results

        for csv_file in csv_files:
            try:
                inserted = self._import_single_csv(csv_file)
                results["files"] += 1
                results["rows"] += inserted
            except Exception as exc:  # noqa: BLE001 - surface errors to UI
                results.setdefault("errors", []).append(
                    {"file": str(csv_file), "error": str(exc)}
                )

        return results

    def _import_single_csv(self, csv_path: Path) -> int:
        """Import a single CSV file of option data."""

        rows_inserted = 0
        for chunk in pd.read_csv(csv_path, chunksize=10_000):
            prepared = self._prepare_local_chunk(chunk)
            if prepared.empty:
                continue
            rows_inserted += self._insert_options_data(prepared)
        return rows_inserted

    def _prepare_local_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Dolt CSV option data to match database schema."""

        if df.empty:
            return df

        column_mapping = {
            "date": "trade_date",
            "act_symbol": "symbol",
            "call_put": "right",
            "vol": "volume",
        }

        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        # Ensure mandatory columns exist
        required_columns = {"trade_date", "symbol", "expiration", "right", "strike"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"Missing required columns in import: {sorted(missing)}")

        df["symbol"] = df["symbol"].map(lambda x: x.upper() if isinstance(x, str) else x)
        df["right"] = df["right"].map(lambda x: x.lower() if isinstance(x, str) else x)

        for date_col in ["trade_date", "expiration"]:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_columns = [
            "strike",
            "bid",
            "ask",
            "last",
            "volume",
            "open_interest",
            "implied_vol",
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "mid" not in df.columns and {"bid", "ask"}.issubset(df.columns):
            df["mid"] = (df["bid"] + df["ask"]) / 2

        for optional in ["last", "mid", "open_interest", "implied_vol", "underlying_price"]:
            if optional not in df.columns:
                df[optional] = None

        df["source"] = "local_csv"
        df["asof"] = datetime.now().isoformat()

        return self._finalize_for_insert(df)

    def _finalize_for_insert(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure dataframe aligns with database column ordering and types."""

        df = df.copy()

        # Normalize symbol/right casing
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].map(lambda x: x.upper() if isinstance(x, str) else x)
        if "right" in df.columns:
            df["right"] = df["right"].map(lambda x: x.lower() if isinstance(x, str) else x)

        for date_col in ["trade_date", "expiration"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")

        if "asof" not in df.columns:
            df["asof"] = datetime.now().isoformat()

        for column in self.DB_COLUMNS:
            if column not in df.columns:
                df[column] = None

        df = df[list(self.DB_COLUMNS)]
        df = df.replace({pd.NA: None, "NaT": None})
        df = df.where(pd.notnull(df), None)
        return df
    
    def download_options(self, symbols: List[str]) -> dict:
        """Download current option chains for symbols.
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {
            "success": [],
            "failed": [],
            "total_rows": 0
        }
        
        trade_date = datetime.now().strftime('%Y-%m-%d')
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get underlying price
                info = ticker.info
                underlying_price = info.get('regularMarketPrice') or info.get('currentPrice')
                
                # Get all expiration dates
                expirations = ticker.options
                
                if not expirations:
                    results["failed"].append({
                        "symbol": symbol,
                        "error": "No options available"
                    })
                    continue
                
                total_inserted = 0
                
                # Download options for each expiration
                for expiration in expirations:
                    opt = ticker.option_chain(expiration)
                    
                    # Process calls
                    if not opt.calls.empty:
                        calls_df = self._prepare_options_data(
                            opt.calls, symbol, trade_date, expiration, 
                            'call', underlying_price
                        )
                        total_inserted += self._insert_options_data(calls_df)
                    
                    # Process puts
                    if not opt.puts.empty:
                        puts_df = self._prepare_options_data(
                            opt.puts, symbol, trade_date, expiration,
                            'put', underlying_price
                        )
                        total_inserted += self._insert_options_data(puts_df)
                
                results["success"].append({
                    "symbol": symbol,
                    "expirations": len(expirations),
                    "rows": total_inserted
                })
                results["total_rows"] += total_inserted
                
            except Exception as e:
                results["failed"].append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return results
    
    def _prepare_options_data(
        self,
        df: pd.DataFrame,
        symbol: str,
        trade_date: str,
        expiration: str,
        right: str,
        underlying_price: Optional[float]
    ) -> pd.DataFrame:
        """Prepare options data for database insertion.
        
        Args:
            df: Options DataFrame from yfinance
            symbol: Stock symbol
            trade_date: Trade date
            expiration: Expiration date
            right: 'call' or 'put'
            underlying_price: Current underlying price
            
        Returns:
            Prepared DataFrame
        """
        df = df.copy()
        df['symbol'] = symbol
        df['trade_date'] = trade_date
        df['expiration'] = expiration
        df['right'] = right
        df['underlying_price'] = underlying_price
        df['source'] = 'yfinance'
        df['asof'] = datetime.now().isoformat()

        column_mapping = {
            'strike': 'strike',
            'lastPrice': 'last',
            'bid': 'bid',
            'ask': 'ask',
            'volume': 'volume',
            'openInterest': 'open_interest',
            'impliedVolatility': 'implied_vol',
            'delta': 'delta',
            'gamma': 'gamma',
            'theta': 'theta',
            'vega': 'vega',
            'rho': 'rho',
        }

        df.rename(columns=column_mapping, inplace=True)

        if {'bid', 'ask'}.issubset(df.columns):
            df['mid'] = (df['bid'] + df['ask']) / 2

        for metric in ['delta', 'gamma', 'theta', 'vega', 'rho']:
            if metric not in df.columns:
                df[metric] = None

        return self._finalize_for_insert(df)
    
    def _insert_options_data(self, df: pd.DataFrame) -> int:
        """Insert options data into database.
        
        Args:
            df: DataFrame with options data
            
        Returns:
            Number of rows inserted
        """
        if df.empty:
            return 0

        df = self._finalize_for_insert(df)

        conn = self.db.connect()
        cursor = conn.cursor()

        placeholders = ", ".join(["?"] * len(self.DB_COLUMNS))
        columns_sql = ", ".join(self.DB_COLUMNS)
        query = f"""
            INSERT OR REPLACE INTO options_chain ({columns_sql})
            VALUES ({placeholders})
        """

        records = [tuple(row) for row in df.itertuples(index=False, name=None)]
        cursor.executemany(query, records)
        conn.commit()
        return len(records)
    
    def get_option_chain(
        self,
        symbol: str,
        trade_date: Optional[str] = None,
        expiration: Optional[str] = None,
        right: Optional[str] = None
    ) -> pd.DataFrame:
        """Retrieve cached option chain data.
        
        Args:
            symbol: Stock symbol
            trade_date: Optional trade date filter
            expiration: Optional expiration date filter
            right: Optional right filter ('call' or 'put')
            
        Returns:
            DataFrame with option chain data
        """
        query = "SELECT * FROM options_chain WHERE symbol = ?"
        params = [symbol]
        
        if trade_date:
            query += " AND trade_date = ?"
            params.append(trade_date)
        
        if expiration:
            query += " AND expiration = ?"
            params.append(expiration)
        
        if right:
            query += " AND right = ?"
            params.append(right)
        
        query += " ORDER BY expiration, strike"
        
        rows = self.db.fetchall(query, tuple(params))
        return pd.DataFrame(rows)

    def get_available_symbols(self) -> List[str]:
        """Return distinct symbols with cached option data."""

        rows = self.db.fetchall(
            "SELECT DISTINCT symbol FROM options_chain ORDER BY symbol"
        )
        return [row["symbol"] for row in rows if row.get("symbol")]

    def get_available_trade_dates(self, symbol: str) -> List[str]:
        """Return sorted trade dates for a symbol (latest first)."""

        rows = self.db.fetchall(
            "SELECT DISTINCT trade_date FROM options_chain WHERE symbol = ? ORDER BY trade_date DESC",
            (symbol,),
        )
        return [row["trade_date"] for row in rows if row.get("trade_date")]

    def get_time_series_by_trade_date(
        self,
        symbol: str,
        strike: float,
        right: str,
        expiration: str,
    ) -> pd.DataFrame:
        """Return historical values for a contract across trade dates."""

        query = """
            SELECT trade_date, bid, ask, last, mid, volume, open_interest,
                   implied_vol, delta, gamma, theta, vega, rho
            FROM options_chain
            WHERE symbol = ? AND strike = ? AND right = ? AND expiration = ?
            ORDER BY trade_date
        """
        rows = self.db.fetchall(query, (symbol, strike, right, expiration))
        return pd.DataFrame(rows)

    def get_time_series_by_expiration(
        self,
        symbol: str,
        strike: float,
        right: str,
        trade_date: str,
    ) -> pd.DataFrame:
        """Return historical values for a contract across expirations."""

        query = """
            SELECT expiration, bid, ask, last, mid, volume, open_interest,
                   implied_vol, delta, gamma, theta, vega, rho
            FROM options_chain
            WHERE symbol = ? AND strike = ? AND right = ? AND trade_date = ?
            ORDER BY expiration
        """
        rows = self.db.fetchall(query, (symbol, strike, right, trade_date))
        return pd.DataFrame(rows)

    def delete_symbol(self, symbol: str) -> int:
        """Delete all option rows for a specific symbol."""

        cursor = self.db.execute(
            "DELETE FROM options_chain WHERE symbol = ?",
            (symbol.upper(),),
        )
        return cursor.rowcount if cursor else 0

    def delete_all(self) -> int:
        """Delete all option data."""

        cursor = self.db.execute("DELETE FROM options_chain")
        return cursor.rowcount if cursor else 0
    
    def get_available_expirations(
        self,
        symbol: str,
        trade_date: Optional[str] = None
    ) -> List[str]:
        """Get available expiration dates for a symbol.
        
        Args:
            symbol: Stock symbol
            trade_date: Optional trade date filter
            
        Returns:
            List of expiration dates
        """
        query = "SELECT DISTINCT expiration FROM options_chain WHERE symbol = ?"
        params = [symbol]
        
        if trade_date:
            query += " AND trade_date = ?"
            params.append(trade_date)
        
        query += " ORDER BY expiration"
        
        rows = self.db.fetchall(query, tuple(params))
        return [row['expiration'] for row in rows]

    # ===== Volatility Data Methods =====
    
    def import_volatility_from_directory(self, directory: Path) -> Dict[str, Any]:
        """Import historical volatility data from CSV files in a directory.

        Files must contain columns: date, act_symbol, hv_current, hv_week_ago,
        hv_month_ago, hv_year_high, hv_year_high_date, hv_year_low, hv_year_low_date,
        iv_current, iv_week_ago, iv_month_ago, iv_year_high, iv_year_high_date,
        iv_year_low, iv_year_low_date.

        Args:
            directory: Folder containing volatility CSV files to import.

        Returns:
            Summary dict with row counts and errors.
        """
        directory = Path(directory)
        results: Dict[str, Any] = {"files": 0, "rows": 0, "errors": []}

        if not directory.exists():
            return results

        csv_files = sorted(p for p in directory.glob("*.csv") if p.is_file())
        if not csv_files:
            return results

        for csv_file in csv_files:
            try:
                inserted = self._import_single_volatility_csv(csv_file)
                results["files"] += 1
                results["rows"] += inserted
            except Exception as exc:  # noqa: BLE001 - surface errors to UI
                results.setdefault("errors", []).append(
                    {"file": str(csv_file), "error": str(exc)}
                )

        return results

    def _import_single_volatility_csv(self, csv_path: Path) -> int:
        """Import a single CSV file of volatility data."""
        rows_inserted = 0
        for chunk in pd.read_csv(csv_path, chunksize=10_000):
            prepared = self._prepare_volatility_chunk(chunk)
            if prepared.empty:
                continue
            rows_inserted += self._insert_volatility_data(prepared)
        return rows_inserted

    def _prepare_volatility_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize volatility CSV data to match database schema."""
        if df.empty:
            return df

        # Map act_symbol to symbol
        if "act_symbol" in df.columns:
            df = df.rename(columns={"act_symbol": "symbol"})

        # Ensure mandatory columns exist
        required_columns = {"date", "symbol"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise ValueError(f"Missing required columns in volatility import: {sorted(missing)}")

        df["symbol"] = df["symbol"].map(lambda x: x.upper() if isinstance(x, str) else x)

        # Format date
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        # Numeric columns
        numeric_columns = [
            "hv_current", "hv_week_ago", "hv_month_ago", "hv_year_high", "hv_year_low",
            "iv_current", "iv_week_ago", "iv_month_ago", "iv_year_high", "iv_year_low"
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Date columns for year high/low
        date_columns = ["hv_year_high_date", "hv_year_low_date", "iv_year_high_date", "iv_year_low_date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

        df["source"] = "local_csv"
        df["asof"] = datetime.now().isoformat()

        # Ensure all expected columns exist
        expected_columns = [
            "date", "symbol", "hv_current", "hv_week_ago", "hv_month_ago", "hv_year_high",
            "hv_year_high_date", "hv_year_low", "hv_year_low_date", "iv_current", "iv_week_ago",
            "iv_month_ago", "iv_year_high", "iv_year_high_date", "iv_year_low", "iv_year_low_date",
            "source", "asof"
        ]

        for col in expected_columns:
            if col not in df.columns:
                df[col] = None

        df = df[expected_columns]
        df = df.replace({pd.NA: None, "NaT": None})
        df = df.where(pd.notnull(df), None)
        return df

    def _insert_volatility_data(self, df: pd.DataFrame) -> int:
        """Insert volatility data into database."""
        if df.empty:
            return 0

        placeholders = ",".join(["?"] * len(df.columns))
        insert_query = f"""
            INSERT OR REPLACE INTO options_volatility ({','.join(df.columns)})
            VALUES ({placeholders})
        """

        rows_data = [tuple(row) for row in df.itertuples(index=False, name=None)]
        self.db.executemany(insert_query, rows_data)
        return len(rows_data)

    def get_volatility_data(self, symbol: str, date: Optional[str] = None) -> pd.DataFrame:
        """Get volatility data for a symbol.
        
        Args:
            symbol: Stock symbol
            date: Optional specific date (if None, returns latest)
            
        Returns:
            DataFrame with volatility metrics
        """
        if date:
            query = "SELECT * FROM options_volatility WHERE symbol = ? AND date = ?"
            params = (symbol.upper(), date)
        else:
            query = """
                SELECT * FROM options_volatility 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT 1
            """
            params = (symbol.upper(),)

        rows = self.db.fetchall(query, params)
        return pd.DataFrame(rows)

    def get_available_volatility_dates(self, symbol: str) -> List[str]:
        """Get available dates for volatility data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of dates
        """
        query = """
            SELECT DISTINCT date 
            FROM options_volatility 
            WHERE symbol = ? 
            ORDER BY date DESC
        """
        rows = self.db.fetchall(query, (symbol.upper(),))
        return [row['date'] for row in rows]
