"""
Natural language to structured strategy parser.
Supports both rule-based parsing and LLM-based parsing via OpenAI and Anthropic.
"""
import re
import os
import json
from typing import Dict, Any, Tuple, Optional
from src.models import Strategy


class NLParser:
    """Parse natural language descriptions into structured strategies."""
    
    def __init__(self, use_llm: bool = True, llm_config: Optional[Dict[str, str]] = None):
        """Initialize parser.
        
        Args:
            use_llm: Whether to use LLM for parsing
            llm_config: Dict with 'provider', 'model', 'api_key' keys
        """
        self.llm_config = llm_config
        if llm_config:
            self.use_llm = use_llm
        else:
            # Fallback to env variable for backward compatibility
            self.use_llm = use_llm and os.getenv("OPENAI_API_KEY")
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
        
        # Filter out common words and indicator names
        common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH'}
        indicator_names = {'SMA', 'EMA', 'RSI', 'MACD', 'BB', 'ATR', 'ADX', 'CCI', 'ROC', 'OBV', 'VWAP'}
        excluded = common_words | indicator_names
        symbols = [s for s in matches if s not in excluded]
        
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
    
    def parse_with_llm(self, text: str) -> Tuple[str, Dict[str, Any], str]:
        """Parse using LLM to generate all three strategy formats.
        
        This method calls OpenAI or Anthropic API to convert natural language into:
        1. Human-readable strategy description
        2. Structured JSON strategy definition
        3. Backtrader Python code
        
        Args:
            text: Natural language strategy description
            
        Returns:
            Tuple of (human_readable, strategy_dict, backtrader_code)
        """
        if not self.use_llm:
            # Fall back to rule-based parsing
            return self._fallback_parsing(text)
        
        # Determine which LLM provider to use
        if self.llm_config:
            provider = self.llm_config.get('provider', 'openai')
            if provider == 'anthropic':
                return self._parse_with_anthropic(text)
            else:
                return self._parse_with_openai(text)
        else:
            # Backward compatibility: use OpenAI from env
            return self._parse_with_openai(text)
    
    def _fallback_parsing(self, text: str) -> Tuple[str, Dict[str, Any], str]:
        """Fallback to rule-based parsing."""
        strategy_dict = self.parse(text)
        from src.strategy import StrategyCompiler
        compiler = StrategyCompiler()
        backtrader_code = compiler.compile(strategy_dict)
        human_readable = self._generate_human_readable(strategy_dict)
        return human_readable, strategy_dict, backtrader_code
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for LLM parsing."""
        return """You are an expert trading strategy converter. Convert natural language trading strategies into three formats:

1. HUMAN_READABLE: A clear, structured description of the strategy in plain English
2. JSON: A structured JSON strategy definition following this schema:
{
  "name": "Strategy Name",
  "universe": ["SYMBOL1", "SYMBOL2"],
  "timeframe": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "interval": "1d"
  },
  "entry": [
    {
      "type": "indicator",
      "ind": "SMA|EMA|RSI|MACD|BBANDS",
      "period": number,
      "op": ">|<|>=|<=|==",
      "rhs": number or {"ind": "...", "period": number}
    }
  ],
  "exit": [
    {
      "type": "trailing_stop|take_profit|stop_loss",
      "percent": 0.08
    }
  ],
  "position": {
    "sizing": "percent_cash|fixed",
    "value": 0.25,
    "max_positions": 4
  },
  "costs": {
    "commission_per_share": 0.005,
    "slippage_bps": 5
  }
}

3. BACKTRADER_CODE: Complete Backtrader strategy class in Python that uses pre-calculated indicators from data feed (e.g., self.data.sma_20, self.data.rsi_14)

Return your response in this exact JSON format:
{
  "human_readable": "...",
  "json_strategy": {...},
  "backtrader_code": "..."
}"""
    
    def _parse_with_openai(self, text: str) -> Tuple[str, Dict[str, Any], str]:
        """Parse using OpenAI API."""
        try:
            import openai
            
            # Get API key and model
            if self.llm_config:
                api_key = self.llm_config.get('api_key')
                model = self.llm_config.get('model', 'gpt-4')
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                model = "gpt-4"
            
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"Convert this trading strategy:\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return (
                result["human_readable"],
                result["json_strategy"],
                result["backtrader_code"]
            )
            
        except Exception as e:
            print(f"OpenAI parsing failed: {e}, falling back to rule-based parsing")
            return self._fallback_parsing(text)
    
    def _parse_with_anthropic(self, text: str) -> Tuple[str, Dict[str, Any], str]:
        """Parse using Anthropic Claude API."""
        try:
            import anthropic
            
            # Get API key and model
            api_key = self.llm_config.get('api_key')
            model = self.llm_config.get('model', 'claude-3-5-sonnet-20241022')
            
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                system=self._get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": f"Convert this trading strategy:\n\n{text}"
                    }
                ]
            )
            
            # Extract text from response
            result_text = response.content[0].text
            result = json.loads(result_text)
            
            return (
                result["human_readable"],
                result["json_strategy"],
                result["backtrader_code"]
            )
            
        except Exception as e:
            print(f"Anthropic parsing failed: {e}, falling back to rule-based parsing")
            return self._fallback_parsing(text)
    
    def _generate_human_readable(self, strategy_dict: Dict[str, Any]) -> str:
        """Generate human-readable description from strategy dictionary.
        
        Args:
            strategy_dict: Structured strategy dictionary
            
        Returns:
            Human-readable strategy description
        """
        lines = []
        lines.append(f"Strategy: {strategy_dict.get('name', 'Unnamed Strategy')}")
        lines.append(f"\nTrading Universe: {', '.join(strategy_dict.get('universe', []))}")
        
        timeframe = strategy_dict.get('timeframe', {})
        lines.append(f"Timeframe: {timeframe.get('start')} to {timeframe.get('end')} ({timeframe.get('interval')})")
        
        lines.append("\nEntry Conditions:")
        for i, condition in enumerate(strategy_dict.get('entry', []), 1):
            if condition['type'] == 'indicator':
                ind_desc = f"{condition['ind']}({condition.get('period', '')})"
                rhs = condition.get('rhs', '')
                if isinstance(rhs, dict):
                    rhs_desc = f"{rhs['ind']}({rhs.get('period', '')})"
                else:
                    rhs_desc = str(rhs)
                lines.append(f"  {i}. {ind_desc} {condition.get('op', '')} {rhs_desc}")
        
        lines.append("\nExit Conditions:")
        for i, condition in enumerate(strategy_dict.get('exit', []), 1):
            exit_type = condition.get('type', '').replace('_', ' ').title()
            percent = condition.get('percent', 0) * 100
            lines.append(f"  {i}. {exit_type}: {percent:.1f}%")
        
        position = strategy_dict.get('position', {})
        lines.append(f"\nPosition Sizing: {position.get('sizing', 'percent_cash')} at {position.get('value', 0.25)*100:.0f}%")
        lines.append(f"Max Positions: {position.get('max_positions', 4)}")
        
        costs = strategy_dict.get('costs', {})
        lines.append(f"\nCosts:")
        lines.append(f"  Commission: ${costs.get('commission_per_share', 0.005):.4f} per share")
        lines.append(f"  Slippage: {costs.get('slippage_bps', 5)} basis points")
        
        return '\n'.join(lines)
