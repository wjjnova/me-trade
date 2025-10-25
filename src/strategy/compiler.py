"""
Strategy code compiler.
Converts structured JSON strategy into executable Backtrader Python code.
"""
from typing import Dict, Any
import textwrap


class StrategyCompiler:
    """Compile structured strategies into Backtrader Python code."""
    
    def compile(self, strategy_dict: Dict[str, Any]) -> str:
        """Compile strategy dictionary to Backtrader code.
        
        Args:
            strategy_dict: Structured strategy from parser or user
            
        Returns:
            Python code string
        """
        entry_conditions = strategy_dict.get('entry', [])
        exit_conditions = strategy_dict.get('exit', [])
        position_config = strategy_dict.get('position', {})
        
        # Generate indicator initializations
        indicators_code = self._generate_indicators(entry_conditions)
        
        # Generate entry logic
        entry_code = self._generate_entry_logic(entry_conditions)
        
        # Generate exit logic
        exit_code = self._generate_exit_logic(exit_conditions)
        
        # Generate position sizing
        sizing_code = self._generate_position_sizing(position_config)
        
        # Build complete strategy class
        code = f'''
import backtrader as bt

class GeneratedStrategy(bt.Strategy):
    """Auto-generated strategy from structured definition."""
    
    params = (
        ('printlog', False),
    )
    
    def __init__(self):
        """Initialize indicators and tracking variables."""
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
        # Initialize indicators
{textwrap.indent(indicators_code, '        ')}
    
    def notify_order(self, order):
        """Track order status."""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                if self.params.printlog:
                    self.log(f'BUY EXECUTED, Price: {{order.executed.price:.2f}}, Cost: {{order.executed.value:.2f}}, Comm: {{order.executed.comm:.2f}}')
            elif order.issell():
                if self.params.printlog:
                    self.log(f'SELL EXECUTED, Price: {{order.executed.price:.2f}}, Cost: {{order.executed.value:.2f}}, Comm: {{order.executed.comm:.2f}}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.params.printlog:
                self.log('Order Canceled/Margin/Rejected')
        
        self.order = None
    
    def next(self):
        """Execute strategy logic on each bar."""
        if self.order:
            return
        
        # Entry logic
        if not self.position:
{textwrap.indent(entry_code, '            ')}
        
        # Exit logic
        else:
{textwrap.indent(exit_code, '            ')}
    
    def log(self, txt, dt=None):
        """Logging function."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{{dt.isoformat()}} {{txt}}')
'''
        
        return code.strip()
    
    def _generate_indicators(self, entry_conditions: list) -> str:
        """Generate indicator initialization code.
        
        Args:
            entry_conditions: List of entry condition dictionaries
            
        Returns:
            Code string for __init__ method
        """
        indicators = set()
        code_lines = []
        
        for condition in entry_conditions:
            if condition.get('type') == 'indicator':
                ind_name = condition.get('ind')
                period = condition.get('period', 14)
                
                if ind_name == 'SMA':
                    var_name = f"sma_{period}"
                    if var_name not in indicators:
                        code_lines.append(f"self.{var_name} = bt.indicators.SimpleMovingAverage(self.data.close, period={period})")
                        indicators.add(var_name)
                
                elif ind_name == 'EMA':
                    var_name = f"ema_{period}"
                    if var_name not in indicators:
                        code_lines.append(f"self.{var_name} = bt.indicators.ExponentialMovingAverage(self.data.close, period={period})")
                        indicators.add(var_name)
                
                elif ind_name == 'RSI':
                    var_name = f"rsi_{period}"
                    if var_name not in indicators:
                        code_lines.append(f"self.{var_name} = bt.indicators.RSI(self.data.close, period={period})")
                        indicators.add(var_name)
                
                elif ind_name == 'MACD':
                    if 'macd' not in indicators:
                        code_lines.append(f"self.macd = bt.indicators.MACD(self.data.close)")
                        indicators.add('macd')
                
                elif ind_name == 'BBANDS':
                    if 'bbands' not in indicators:
                        code_lines.append(f"self.bbands = bt.indicators.BollingerBands(self.data.close)")
                        indicators.add('bbands')
                
                # Handle RHS if it's also an indicator
                rhs = condition.get('rhs')
                if isinstance(rhs, dict) and rhs.get('ind'):
                    rhs_ind = rhs.get('ind')
                    rhs_period = rhs.get('period', 14)
                    
                    if rhs_ind == 'SMA':
                        var_name = f"sma_{rhs_period}"
                        if var_name not in indicators:
                            code_lines.append(f"self.{var_name} = bt.indicators.SimpleMovingAverage(self.data.close, period={rhs_period})")
                            indicators.add(var_name)
        
        return '\n'.join(code_lines) if code_lines else "pass"
    
    def _generate_entry_logic(self, entry_conditions: list) -> str:
        """Generate entry logic code.
        
        Args:
            entry_conditions: List of entry condition dictionaries
            
        Returns:
            Code string for buy logic
        """
        if not entry_conditions:
            return "pass"
        
        condition_parts = []
        
        for condition in entry_conditions:
            if condition.get('type') == 'indicator':
                ind_name = condition.get('ind')
                period = condition.get('period', 14)
                op = condition.get('op', '>')
                rhs = condition.get('rhs')
                
                # Build LHS
                if ind_name == 'SMA':
                    lhs = f"self.sma_{period}[0]"
                elif ind_name == 'EMA':
                    lhs = f"self.ema_{period}[0]"
                elif ind_name == 'RSI':
                    lhs = f"self.rsi_{period}[0]"
                elif ind_name == 'MACD':
                    lhs = "self.macd.macd[0]"
                else:
                    continue
                
                # Build RHS
                if isinstance(rhs, dict) and rhs.get('ind'):
                    rhs_ind = rhs.get('ind')
                    rhs_period = rhs.get('period', 14)
                    if rhs_ind == 'SMA':
                        rhs_str = f"self.sma_{rhs_period}[0]"
                    elif rhs_ind == 'EMA':
                        rhs_str = f"self.ema_{rhs_period}[0]"
                    else:
                        rhs_str = str(rhs)
                else:
                    rhs_str = str(rhs)
                
                condition_parts.append(f"{lhs} {op} {rhs_str}")
        
        if condition_parts:
            conditions_str = " and ".join(condition_parts)
            return f"if {conditions_str}:\n    self.buy()"
        else:
            return "pass"
    
    def _generate_exit_logic(self, exit_conditions: list) -> str:
        """Generate exit logic code.
        
        Args:
            exit_conditions: List of exit condition dictionaries
            
        Returns:
            Code string for sell logic
        """
        if not exit_conditions:
            return "pass"
        
        code_lines = []
        
        for condition in exit_conditions:
            cond_type = condition.get('type')
            percent = condition.get('percent', 0.1)
            
            if cond_type == 'trailing_stop':
                code_lines.append(f"# Trailing stop: {percent*100:.1f}%")
                code_lines.append(f"if self.data.close[0] < self.buy_price * (1 - {percent}):")
                code_lines.append(f"    self.sell()")
            
            elif cond_type == 'stop_loss':
                code_lines.append(f"# Stop loss: {percent*100:.1f}%")
                code_lines.append(f"if self.data.close[0] < self.buy_price * (1 - {percent}):")
                code_lines.append(f"    self.sell()")
            
            elif cond_type == 'take_profit':
                code_lines.append(f"# Take profit: {percent*100:.1f}%")
                code_lines.append(f"if self.data.close[0] > self.buy_price * (1 + {percent}):")
                code_lines.append(f"    self.sell()")
        
        return '\n'.join(code_lines) if code_lines else "pass"
    
    def _generate_position_sizing(self, position_config: dict) -> str:
        """Generate position sizing code.
        
        Args:
            position_config: Position configuration dictionary
            
        Returns:
            Code string for position sizing
        """
        sizing = position_config.get('sizing', 'percent_cash')
        value = position_config.get('value', 0.25)
        
        if sizing == 'percent_cash':
            return f"# Position size: {value*100:.1f}% of cash"
        elif sizing == 'fixed':
            return f"# Position size: {value} shares"
        
        return ""
