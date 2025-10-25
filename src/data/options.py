"""
Options data sourcing using yfinance.
Downloads and caches option chain data to SQLite.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List, Optional
from src.db import get_db


class OptionsDataManager:
    """Manager for downloading and caching options chain data."""
    
    def __init__(self):
        self.db = get_db()
    
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
        
        # Rename columns to match schema
        column_mapping = {
            'strike': 'strike',
            'lastPrice': 'last',
            'bid': 'bid',
            'ask': 'ask',
            'volume': 'volume',
            'openInterest': 'open_interest',
            'impliedVolatility': 'implied_vol'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Calculate mid price
        df['mid'] = (df['bid'] + df['ask']) / 2
        
        # Select only needed columns
        columns = [
            'symbol', 'trade_date', 'expiration', 'right', 'strike',
            'bid', 'ask', 'last', 'mid', 'volume', 'open_interest',
            'implied_vol', 'underlying_price', 'source', 'asof'
        ]
        
        # Only keep columns that exist
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]
        
        return df
    
    def _insert_options_data(self, df: pd.DataFrame) -> int:
        """Insert options data into database.
        
        Args:
            df: DataFrame with options data
            
        Returns:
            Number of rows inserted
        """
        conn = self.db.connect()
        
        query = """
            INSERT OR REPLACE INTO options_chain
            (symbol, trade_date, expiration, right, strike, bid, ask, last, mid,
             volume, open_interest, implied_vol, underlying_price, source, asof)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = conn.cursor()
        rows_inserted = 0
        
        for _, row in df.iterrows():
            cursor.execute(query, (
                row.get('symbol'),
                row.get('trade_date'),
                row.get('expiration'),
                row.get('right'),
                row.get('strike'),
                row.get('bid'),
                row.get('ask'),
                row.get('last'),
                row.get('mid'),
                row.get('volume'),
                row.get('open_interest'),
                row.get('implied_vol'),
                row.get('underlying_price'),
                row.get('source'),
                row.get('asof')
            ))
            rows_inserted += 1
        
        conn.commit()
        return rows_inserted
    
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
