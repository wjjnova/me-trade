"""
Technical indicators calculator for stock data.
Calculates common indicators (SMA, EMA, RSI, MACD, Bollinger Bands) from OHLCV data.
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime
from src.db import get_db


class IndicatorCalculator:
    """Calculate technical indicators from OHLCV data."""
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
        """Calculate Simple Moving Average.
        
        Args:
            data: DataFrame with OHLCV data
            period: Lookback period for SMA
            column: Column to calculate SMA on (default: 'close')
        
        Returns:
            Series with SMA values
        """
        return data[column].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
        """Calculate Exponential Moving Average.
        
        Args:
            data: DataFrame with OHLCV data
            period: Lookback period for EMA
            column: Column to calculate EMA on (default: 'close')
        
        Returns:
            Series with EMA values
        """
        return data[column].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
        """Calculate Relative Strength Index.
        
        Args:
            data: DataFrame with OHLCV data
            period: Lookback period for RSI
            column: Column to calculate RSI on (default: 'close')
        
        Returns:
            Series with RSI values
        """
        delta = data[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, 
                      signal: int = 9, column: str = 'close') -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: DataFrame with OHLCV data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            column: Column to calculate MACD on (default: 'close')
        
        Returns:
            Dict with 'macd', 'signal', and 'histogram' Series
        """
        ema_fast = data[column].ewm(span=fast, adjust=False).mean()
        ema_slow = data[column].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, 
                                 std_dev: int = 2, column: str = 'close') -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands.
        
        Args:
            data: DataFrame with OHLCV data
            period: Lookback period for moving average
            std_dev: Number of standard deviations for bands
            column: Column to calculate bands on (default: 'close')
        
        Returns:
            Dict with 'middle', 'upper', and 'lower' Series
        """
        middle = data[column].rolling(window=period).mean()
        std = data[column].rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'middle': middle,
            'upper': upper,
            'lower': lower
        }
    
    @staticmethod
    def calculate_all(data: pd.DataFrame, 
                     indicators: Optional[List[str]] = None) -> pd.DataFrame:
        """Calculate multiple indicators and add them to the DataFrame.
        
        Args:
            data: DataFrame with OHLCV data (must have 'close' column)
            indicators: List of indicator names to calculate. 
                       Options: 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
                               'rsi', 'macd', 'bbands'
                       If None, calculates common defaults.
        
        Returns:
            DataFrame with original data plus indicator columns
        """
        result = data.copy()
        
        if indicators is None:
            indicators = ['sma_20', 'sma_50', 'rsi', 'macd', 'bbands']
        
        for indicator in indicators:
            if indicator.startswith('sma_'):
                period = int(indicator.split('_')[1])
                result[f'SMA_{period}'] = IndicatorCalculator.calculate_sma(data, period)
            
            elif indicator.startswith('ema_'):
                period = int(indicator.split('_')[1])
                result[f'EMA_{period}'] = IndicatorCalculator.calculate_ema(data, period)
            
            elif indicator == 'rsi':
                result['RSI'] = IndicatorCalculator.calculate_rsi(data)
            
            elif indicator == 'macd':
                macd_data = IndicatorCalculator.calculate_macd(data)
                result['MACD'] = macd_data['macd']
                result['MACD_Signal'] = macd_data['signal']
                result['MACD_Histogram'] = macd_data['histogram']
            
            elif indicator == 'bbands':
                bb_data = IndicatorCalculator.calculate_bollinger_bands(data)
                result['BB_Middle'] = bb_data['middle']
                result['BB_Upper'] = bb_data['upper']
                result['BB_Lower'] = bb_data['lower']
        
        return result


class IndicatorStorage:
    """Store and retrieve technical indicators from database."""
    
    def __init__(self):
        self.db = get_db()
    
    def save_indicators(self, symbol: str, data: pd.DataFrame, interval: str = "1d"):
        """Calculate and save indicators to database.
        
        Args:
            symbol: Stock ticker symbol
            data: DataFrame with OHLCV data (must have 'date' and 'close' columns)
            interval: Data interval
        """
        # Calculate all standard indicators
        df_with_ind = IndicatorCalculator.calculate_all(
            data, 
            indicators=['sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'rsi', 'macd', 'bbands']
        )
        
        # Prepare data for insertion
        conn = self.db.connect()
        cursor = conn.cursor()
        calculated_at = datetime.now().isoformat()
        
        # Use INSERT OR REPLACE for upsert behavior
        query = """
            INSERT OR REPLACE INTO technical_indicators 
            (symbol, date, interval, sma_20, sma_50, sma_200, ema_12, ema_26, 
             rsi_14, macd, macd_signal, macd_histogram, bb_upper, bb_middle, bb_lower, calculated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        rows_inserted = 0
        for _, row in df_with_ind.iterrows():
            # Convert date to string if it's datetime
            date_str = row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else str(row['date'])
            
            cursor.execute(query, (
                symbol,
                date_str,
                interval,
                float(row['SMA_20']) if pd.notna(row['SMA_20']) else None,
                float(row['SMA_50']) if pd.notna(row['SMA_50']) else None,
                float(row['SMA_200']) if pd.notna(row['SMA_200']) else None,
                float(row['EMA_12']) if pd.notna(row['EMA_12']) else None,
                float(row['EMA_26']) if pd.notna(row['EMA_26']) else None,
                float(row['RSI']) if pd.notna(row['RSI']) else None,
                float(row['MACD']) if pd.notna(row['MACD']) else None,
                float(row['MACD_Signal']) if pd.notna(row['MACD_Signal']) else None,
                float(row['MACD_Histogram']) if pd.notna(row['MACD_Histogram']) else None,
                float(row['BB_Upper']) if pd.notna(row['BB_Upper']) else None,
                float(row['BB_Middle']) if pd.notna(row['BB_Middle']) else None,
                float(row['BB_Lower']) if pd.notna(row['BB_Lower']) else None,
                calculated_at
            ))
            rows_inserted += 1
        
        conn.commit()
        return rows_inserted
    
    def get_indicators(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Retrieve stored indicators from database.
        
        Args:
            symbol: Stock ticker symbol
            start: Optional start date filter
            end: Optional end date filter
            interval: Data interval
            
        Returns:
            DataFrame with indicator data
        """
        query = """
            SELECT symbol, date, interval, 
                   sma_20, sma_50, sma_200, ema_12, ema_26, rsi_14,
                   macd, macd_signal, macd_histogram,
                   bb_upper, bb_middle, bb_lower, calculated_at
            FROM technical_indicators
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
    
    def get_indicators_with_ohlcv(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Retrieve both OHLCV and indicator data joined.
        
        Args:
            symbol: Stock ticker symbol
            start: Optional start date filter
            end: Optional end date filter
            interval: Data interval
            
        Returns:
            DataFrame with OHLCV + indicator data
        """
        query = """
            SELECT 
                e.symbol, e.date, e.interval,
                e.open, e.high, e.low, e.close, e.volume,
                i.sma_20, i.sma_50, i.sma_200, i.ema_12, i.ema_26, i.rsi_14,
                i.macd, i.macd_signal, i.macd_histogram,
                i.bb_upper, i.bb_middle, i.bb_lower
            FROM equities_ohlcv e
            LEFT JOIN technical_indicators i 
                ON e.symbol = i.symbol AND e.date = i.date AND e.interval = i.interval
            WHERE e.symbol = ? AND e.interval = ?
        """
        params = [symbol, interval]
        
        if start:
            query += " AND e.date >= ?"
            params.append(start)
        
        if end:
            query += " AND e.date <= ?"
            params.append(end)
        
        query += " ORDER BY e.date"
        
        rows = self.db.fetchall(query, tuple(params))
        df = pd.DataFrame(rows)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def has_indicators(self, symbol: str, interval: str = "1d") -> bool:
        """Check if indicators exist for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            interval: Data interval
            
        Returns:
            True if indicators exist
        """
        query = """
            SELECT COUNT(*) as count 
            FROM technical_indicators 
            WHERE symbol = ? AND interval = ?
        """
        result = self.db.fetchone(query, (symbol, interval))
        return result['count'] > 0 if result else False
