"""
Natural language to structured strategy parser.
MVP uses rule-based parsing with stub for future LLM integration.
"""
import re
from typing import Dict, Any
from src.models import Strategy


class NLParser:
    """Parse natural language descriptions into structured strategies."""
    
    def __init__(self):
        self.indicator_keywords = {
            'sma': 'SMA',
            'simple moving average': 'SMA',
            'ema': 'EMA',
            'exponential moving average': 'EMA',
            'rsi': 'RSI',
            'relative strength index': 'RSI',
            'macd': 'MACD',
            'bollinger': 'BBANDS',
            'bollinger bands': 'BBANDS'
        }
    
    def parse(self, text: str, symbols: list = None) -> Dict[str, Any]:
        """Parse natural language text into structured strategy.
        
        This is a simple rule-based implementation for MVP.
        TODO: Replace with LLM-based parsing for better accuracy.
        
        Args:
            text: Natural language strategy description
            symbols: Optional list of symbols (will try to extract if not provided)
            
        Returns:
            Dictionary representing structured strategy
        """
        text_lower = text.lower()
        
        # Extract symbols if not provided
        if not symbols:
            symbols = self._extract_symbols(text)
        
        # Extract indicators
        indicators = self._extract_indicators(text_lower)
        
        # Extract time periods
        periods = self._extract_periods(text)
        
        # Build entry conditions
        entry_conditions = []
        if 'sma' in indicators or 'simple moving average' in text_lower:
            # Look for crossover patterns
            if 'cross' in text_lower or 'above' in text_lower:
                entry_conditions.append({
                    "type": "indicator",
                    "ind": "SMA",
                    "period": 50,
                    "op": ">",
                    "rhs": {"ind": "SMA", "period": 200}
                })
        
        if 'rsi' in indicators:
            # RSI filter
            entry_conditions.append({
                "type": "indicator",
                "ind": "RSI",
                "period": 14,
                "op": "<",
                "rhs": 70
            })
        
        # Build exit conditions
        exit_conditions = []
        
        # Look for stop loss mentions
        if 'stop' in text_lower or 'loss' in text_lower:
            stop_percent = self._extract_percentage(text, default=0.08)
            exit_conditions.append({
                "type": "trailing_stop",
                "percent": stop_percent
            })
        
        # Look for profit taking
        if 'profit' in text_lower or 'target' in text_lower:
            profit_percent = self._extract_percentage(text, default=0.15)
            exit_conditions.append({
                "type": "take_profit",
                "percent": profit_percent
            })
        
        # Default exits if none found
        if not exit_conditions:
            exit_conditions = [
                {"type": "trailing_stop", "percent": 0.08},
                {"type": "take_profit", "percent": 0.15}
            ]
        
        # Default entry if none found
        if not entry_conditions:
            entry_conditions = [{
                "type": "indicator",
                "ind": "SMA",
                "period": 50,
                "op": ">",
                "rhs": {"ind": "SMA", "period": 200}
            }]
        
        # Extract dates or use defaults
        start_date, end_date = self._extract_dates(text)
        
        # Build strategy structure
        strategy_dict = {
            "name": self._extract_name(text) or "Natural Language Strategy",
            "universe": symbols or ["AAPL"],
            "timeframe": {
                "start": start_date,
                "end": end_date,
                "interval": "1d"
            },
            "entry": entry_conditions,
            "exit": exit_conditions,
            "position": {
                "sizing": "percent_cash",
                "value": 0.25,
                "max_positions": len(symbols) if symbols else 4
            },
            "costs": {
                "commission_per_share": 0.005,
                "slippage_bps": 5
            }
        }
        
        return strategy_dict
    
    def _extract_symbols(self, text: str) -> list:
        """Extract stock symbols from text.
        
        Args:
            text: Input text
            
        Returns:
            List of symbols
        """
        # Look for common ticker patterns
        symbol_pattern = r'\b([A-Z]{1,5})\b'
        matches = re.findall(symbol_pattern, text)
        
        # Filter out common words
        common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH'}
        symbols = [s for s in matches if s not in common_words]
        
        return symbols[:10] if symbols else ["AAPL"]  # Limit to 10 symbols
    
    def _extract_indicators(self, text: str) -> list:
        """Extract indicator names from text.
        
        Args:
            text: Input text (lowercase)
            
        Returns:
            List of indicator names
        """
        found_indicators = []
        for keyword, indicator in self.indicator_keywords.items():
            if keyword in text:
                found_indicators.append(indicator)
        return found_indicators
    
    def _extract_periods(self, text: str) -> list:
        """Extract time periods (days) from text.
        
        Args:
            text: Input text
            
        Returns:
            List of period numbers
        """
        # Look for patterns like "50 day", "200-day", etc.
        period_pattern = r'(\d+)[- ]?day'
        matches = re.findall(period_pattern, text, re.IGNORECASE)
        return [int(m) for m in matches]
    
    def _extract_percentage(self, text: str, default: float = 0.1) -> float:
        """Extract percentage value from text.
        
        Args:
            text: Input text
            default: Default value if no percentage found
            
        Returns:
            Percentage as decimal (e.g., 0.08 for 8%)
        """
        # Look for patterns like "8%", "8 percent", "0.08"
        percent_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*percent',
            r'(0\.\d+)'
        ]
        
        for pattern in percent_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = float(matches[0])
                # Convert to decimal if given as percentage
                if value > 1:
                    value = value / 100
                return value
        
        return default
    
    def _extract_dates(self, text: str) -> tuple:
        """Extract start and end dates from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (start_date, end_date) as strings
        """
        # Look for date patterns
        date_pattern = r'(\d{4}[-/]\d{2}[-/]\d{2})'
        matches = re.findall(date_pattern, text)
        
        if len(matches) >= 2:
            return matches[0].replace('/', '-'), matches[1].replace('/', '-')
        elif len(matches) == 1:
            return matches[0].replace('/', '-'), "2024-12-31"
        else:
            return "2019-01-01", "2024-12-31"
    
    def _extract_name(self, text: str) -> str:
        """Extract or generate strategy name from text.
        
        Args:
            text: Input text
            
        Returns:
            Strategy name
        """
        # Take first sentence or first 50 chars as name
        sentences = text.split('.')
        if sentences:
            name = sentences[0].strip()
            if len(name) > 50:
                name = name[:50] + "..."
            return name
        return "Natural Language Strategy"
    
    def parse_with_llm(self, text: str) -> Dict[str, Any]:
        """Parse using LLM (future implementation).
        
        This is a stub for future LLM integration.
        
        Args:
            text: Natural language strategy description
            
        Returns:
            Structured strategy dictionary
        """
        # TODO: Integrate with OpenAI/Anthropic/other LLM
        # For now, fall back to rule-based parsing
        return self.parse(text)
