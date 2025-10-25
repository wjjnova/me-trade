"""
Strategy code compiler.
Converts structured JSON strategy into executable Backtrader Python code.
"""
from typing import Dict, Any, Tuple
import json
import textwrap


class StrategyCompiler:
    """Compile structured strategies into Backtrader Python code."""
    
    def compile(self, strategy_dict: Dict[str, Any]) -> str:
        """Compile strategy dictionary to Backtrader code using pre-calculated indicators.
        
        Args:
            strategy_dict: Structured strategy from parser or user
            
        Returns:
            Python code string
        """
        entry_conditions = strategy_dict.get('entry', [])
        exit_conditions = strategy_dict.get('exit', [])
        position_config = strategy_dict.get('position', {})
        
        # Note: Indicators are now pre-calculated and available in data feed lines
        # We just need to reference them (e.g., self.data.sma_20)
        
        # Generate entry logic
        entry_code = self._generate_entry_logic(entry_conditions)

        # Generate exit logic
        exit_code = self._generate_exit_logic(exit_conditions)

        # Generate position sizing helper
        sizing_code = self._generate_position_sizing(position_config)

        # Build complete strategy class
        code = f'''
import backtrader as bt

class GeneratedStrategy(bt.Strategy):
    """Auto-generated strategy using pre-calculated indicators from data feed."""

    params = (
        ('printlog', False),
    )

    def __init__(self):
        """Initialize tracking variables. Indicators are pre-calculated in data feed."""
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        self.trade_log = []
        self._pending_signal = None

        # Pre-calculated indicators are available as data feed lines:
        # self.data.sma_20, self.data.sma_50, self.data.rsi_14, etc.

    def _determine_size(self, price: float) -> int:
{textwrap.indent(sizing_code or 'return 0', '        ')}

    def _place_order(self, side: str, reason: str, size: int) -> None:
        if self.order:
            return
        if size is None or size <= 0:
            return

        self._pending_signal = {'side': side, 'reason': reason}

        if side == 'buy':
            order = self.buy(size=size)
        else:
            order = self.sell(size=size)

        if order is not None:
            try:
                order.addinfo(reason=reason)
            except AttributeError:
                pass
            self.order = order

    def notify_order(self, order):
        """Track order status and record trade execution."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            portfolio_value = float(self.broker.getvalue()) if hasattr(self, 'broker') else None
            executed_value = float(order.executed.value) if hasattr(order.executed, 'value') else None

            alloc_pct = None
            if portfolio_value and portfolio_value != 0 and executed_value is not None:
                alloc_pct = abs(executed_value) / portfolio_value

            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            elif order.issell():
                self.buy_price = None

            timestamp = None
            if hasattr(order.data.datetime, 'datetime'):
                try:
                    timestamp = order.data.datetime.datetime(0)
                except Exception:
                    timestamp = None

            if timestamp is None and hasattr(self.datas[0].datetime, 'datetime'):
                try:
                    timestamp = self.datas[0].datetime.datetime(0)
                except Exception:
                    timestamp = None

            if hasattr(timestamp, 'isoformat'):
                timestamp = timestamp.replace(tzinfo=None).isoformat()
            elif timestamp is not None:
                timestamp = str(timestamp)

            symbol = getattr(order.data, '_name', None)
            if not symbol:
                symbol = getattr(getattr(order.data, 'params', None), 'dataname', 'UNKNOWN')

            reason = getattr(getattr(order, 'info', None), 'reason', None)
            if not reason and self._pending_signal and self._pending_signal.get('side') == ('buy' if order.isbuy() else 'sell'):
                reason = self._pending_signal.get('reason')

            record = {
                'timestamp': timestamp,
                'symbol': symbol,
                'action': 'BUY' if order.isbuy() else 'SELL',
                'size': abs(order.executed.size),
                'price': order.executed.price,
                'value': order.executed.value,
                'commission': order.executed.comm,
                'reason': reason,
                'portfolio_value': portfolio_value,
                'alloc_pct': alloc_pct,
                'pnl': None,
                'pnl_pct': None,
                'holding_period': None,
            }
            self.trade_log.append(record)

            if self.params.printlog:
                action = 'BUY' if order.isbuy() else 'SELL'
                self.log(f'{action} EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.params.printlog:
                self.log('Order Canceled/Margin/Rejected')

        self.order = None
        self._pending_signal = None

    def notify_trade(self, trade):
        """Update trade log with realized PnL when a trade closes."""
        if not trade.isclosed:
            return

        symbol = getattr(trade.data, '_name', None)
        if not symbol:
            symbol = getattr(getattr(trade.data, 'params', None), 'dataname', 'UNKNOWN')

        pnl = trade.pnlcomm
        sell_record = None
        entry_price = None
        entry_size = None

        for record in reversed(self.trade_log):
            if record['symbol'] != symbol:
                continue

            if sell_record is None and record['action'] == 'SELL' and record.get('pnl') is None:
                sell_record = record
                continue

            if record['action'] == 'BUY':
                entry_price = record.get('price')
                entry_size = record.get('size')
                break

        if sell_record is None:
            return

        sell_record['pnl'] = pnl
        if isinstance(entry_price, (int, float)) and isinstance(entry_size, (int, float)) and entry_price and entry_size:
            try:
                sell_record['pnl_pct'] = pnl / (entry_price * entry_size)
            except ZeroDivisionError:
                sell_record['pnl_pct'] = None
        else:
            sell_record['pnl_pct'] = None

        sell_record['holding_period'] = getattr(trade, 'barlen', None)

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
                        code_lines.append(f"self.{var_name} = bt.indicators.SimpleMovingAverage(data.close, period={period})")
                        indicators.add(var_name)
                
                elif ind_name == 'EMA':
                    var_name = f"ema_{period}"
                    if var_name not in indicators:
                        code_lines.append(f"self.{var_name} = bt.indicators.ExponentialMovingAverage(data.close, period={period})")
                        indicators.add(var_name)
                
                elif ind_name == 'RSI':
                    var_name = f"rsi_{period}"
                    if var_name not in indicators:
                        code_lines.append(f"self.{var_name} = bt.indicators.RSI(data.close, period={period})")
                        indicators.add(var_name)
                
                elif ind_name == 'MACD':
                    if 'macd' not in indicators:
                        code_lines.append(f"self.macd = bt.indicators.MACD(data.close)")
                        indicators.add('macd')
                
                elif ind_name == 'BBANDS':
                    if 'bbands' not in indicators:
                        code_lines.append(f"self.bbands = bt.indicators.BollingerBands(data.close)")
                        indicators.add('bbands')
                
                # Handle RHS if it's also an indicator
                rhs = condition.get('rhs')
                if isinstance(rhs, dict) and rhs.get('ind'):
                    rhs_ind = rhs.get('ind')
                    rhs_period = rhs.get('period', 14)
                    
                    if rhs_ind == 'SMA':
                        var_name = f"sma_{rhs_period}"
                        if var_name not in indicators:
                            code_lines.append(f"self.{var_name} = bt.indicators.SimpleMovingAverage(data.close, period={rhs_period})")
                            indicators.add(var_name)
        
        return '\n'.join(code_lines) if code_lines else "pass"
    
    def _generate_entry_logic(self, entry_conditions: list) -> str:
        """Generate entry logic using pre-calculated indicators from data feed.
        
        Args:
            entry_conditions: List of entry condition dictionaries
            
        Returns:
            Code string for buy logic
        """
        if not entry_conditions:
            return "pass"
        
        condition_parts = []
        reason_parts = []

        for condition in entry_conditions:
            if condition.get('type') != 'indicator':
                continue

            ind_name = condition.get('ind')
            period = condition.get('period', 14)
            op = condition.get('op', '>')
            rhs = condition.get('rhs')

            lhs_expr, lhs_label = self._indicator_expression(ind_name, period)

            if isinstance(rhs, dict) and rhs.get('ind'):
                rhs_expr, rhs_label = self._indicator_expression(rhs.get('ind'), rhs.get('period', 14))
            else:
                rhs_expr = str(rhs)
                rhs_label = self._format_literal(rhs)

            if lhs_expr:
                condition_parts.append(f"{lhs_expr} {op} {rhs_expr}")
                reason_parts.append(f"{lhs_label} {op} {rhs_label}")

        if not condition_parts:
            return "pass"

        conditions_str = " and ".join(condition_parts)
        reason_text = f"Entry: {' AND '.join(reason_parts)}"
        reason_literal = json.dumps(reason_text)

        return "\n".join(
            [
                f"if {conditions_str}:",
                "    size = self._determine_size(self.data.close[0])",
                "    if size > 0:",
                f"        self._place_order('buy', {reason_literal}, size)",
            ]
        )
    
    def _generate_exit_logic(self, exit_conditions: list) -> str:
        """Generate exit logic code.
        
        Args:
            exit_conditions: List of exit condition dictionaries
            
        Returns:
            Code string for sell logic
        """
        if not exit_conditions:
            return "pass"

        clauses = []

        for condition in exit_conditions:
            cond_type = condition.get('type')
            percent = condition.get('percent', 0.1)

            if cond_type == 'trailing_stop':
                clauses.append((
                    f"self.buy_price and self.data.close[0] <= self.buy_price * (1 - {percent})",
                    f"Trailing stop {percent * 100:.1f}% triggered",
                ))
            elif cond_type == 'stop_loss':
                clauses.append((
                    f"self.buy_price and self.data.close[0] <= self.buy_price * (1 - {percent})",
                    f"Stop loss {percent * 100:.1f}% triggered",
                ))
            elif cond_type == 'take_profit':
                clauses.append((
                    f"self.buy_price and self.data.close[0] >= self.buy_price * (1 + {percent})",
                    f"Take profit {percent * 100:.1f}% reached",
                ))
            elif cond_type == 'profit_target':
                clauses.append((
                    f"self.buy_price and self.data.close[0] >= self.buy_price * (1 + {percent})",
                    f"Profit target {percent * 100:.1f}% hit",
                ))

        if not clauses:
            return "pass"

        code_lines = [
            "size = int(abs(self.position.size))",
            "if size <= 0:",
            "    return",
        ]

        for idx, (expr, reason) in enumerate(clauses):
            prefix = "if" if idx == 0 else "elif"
            reason_literal = json.dumps(reason)
            code_lines.append(f"{prefix} {expr}:")
            code_lines.append(f"    self._place_order('sell', {reason_literal}, size)")
            code_lines.append("    return")

        return '\n'.join(code_lines)
    
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
            lines = [
                "if price is None or price <= 0:",
                "    return 0",
                "cash = self.broker.getcash()",
                "if cash <= 0:",
                "    return 0",
                f"target_cash = cash * {value}",
                "size = int(target_cash // price)",
                "if size <= 0:",
                "    size = int(cash // price)",
                "return max(size, 0)",
            ]
            return '\n'.join(lines)

        if sizing == 'fixed':
            return f"return max(int({int(value)}), 0)"

        return "return 0"

    def _indicator_expression(self, ind_name: str, period: int) -> Tuple[str, str]:
        """Map indicator definitions to data feed expressions and labels."""
        if ind_name == 'SMA':
            expr = f"self.data.sma_{period}[0]"
            label = f"SMA({period})"
        elif ind_name == 'EMA':
            expr = f"self.data.ema_{period}[0]"
            label = f"EMA({period})"
        elif ind_name == 'RSI':
            expr = "self.data.rsi_14[0]" if period == 14 else f"self.data.rsi_{period}[0]"
            label = f"RSI({period})"
        elif ind_name == 'MACD':
            expr = "self.data.macd[0]"
            label = "MACD"
        elif ind_name == 'MACD_SIGNAL':
            expr = "self.data.macd_signal[0]"
            label = "MACD Signal"
        elif ind_name == 'MACD_HISTOGRAM':
            expr = "self.data.macd_histogram[0]"
            label = "MACD Histogram"
        else:
            expr = ""
            label = ind_name or 'value'

        return expr, label

    def _format_literal(self, value: Any) -> str:
        """Format a literal RHS value for human-readable logging."""
        if isinstance(value, (int, float)):
            return f"{value}"
        return str(value)
