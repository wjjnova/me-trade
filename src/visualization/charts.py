"""
Visualization utilities for equity curves, drawdowns, and metrics.
Uses Plotly for interactive charts.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, List


class ChartGenerator:
    """Generate interactive charts for backtest results."""
    
    def equity_curve_chart(
        self,
        equity_df: pd.DataFrame,
        benchmark_df: Optional[pd.DataFrame] = None,
        title: str = "Equity Curve"
    ) -> go.Figure:
        """Create equity curve chart with optional benchmark overlay.
        
        Args:
            equity_df: DataFrame with date and value columns
            benchmark_df: Optional benchmark DataFrame
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        # Add strategy equity curve
        fig.add_trace(go.Scatter(
            x=equity_df['date'],
            y=equity_df['value'],
            mode='lines',
            name='Strategy',
            line=dict(color='blue', width=2)
        ))
        
        # Add benchmark if provided
        if benchmark_df is not None and not benchmark_df.empty:
            fig.add_trace(go.Scatter(
                x=benchmark_df['date'],
                y=benchmark_df['value'],
                mode='lines',
                name='Benchmark',
                line=dict(color='gray', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def drawdown_chart(
        self,
        equity_df: pd.DataFrame,
        title: str = "Drawdown"
    ) -> go.Figure:
        """Create drawdown chart.
        
        Args:
            equity_df: DataFrame with date and value columns
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Calculate drawdown
        values = equity_df['value']
        cummax = values.cummax()
        drawdown = (values - cummax) / cummax
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=equity_df['date'],
            y=drawdown * 100,  # Convert to percentage
            mode='lines',
            fill='tozeroy',
            name='Drawdown',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def returns_distribution(
        self,
        equity_df: pd.DataFrame,
        title: str = "Returns Distribution"
    ) -> go.Figure:
        """Create returns distribution histogram.
        
        Args:
            equity_df: DataFrame with date and value columns
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Calculate daily returns
        returns = equity_df['value'].pct_change().dropna() * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Returns',
            marker=dict(color='blue', line=dict(color='white', width=1))
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def metrics_table(
        self,
        metrics: dict,
        benchmark_metrics: Optional[dict] = None
    ) -> pd.DataFrame:
        """Create formatted metrics table for display.
        
        Args:
            metrics: Strategy metrics dictionary
            benchmark_metrics: Optional benchmark metrics
            
        Returns:
            DataFrame formatted for display
        """
        data = []
        
        metric_labels = {
            'tot_return': 'Total Return',
            'cagr': 'CAGR',
            'max_dd': 'Max Drawdown',
            'sharpe': 'Sharpe Ratio',
            'sortino': 'Sortino Ratio',
            'calmar': 'Calmar Ratio',
            'excess_return': 'Excess Return'
        }
        
        for key, label in metric_labels.items():
            if key in metrics:
                row = {'Metric': label}
                
                # Format value based on metric type
                value = metrics[key]
                if key in ['tot_return', 'cagr', 'max_dd', 'excess_return']:
                    row['Strategy'] = f"{value * 100:.2f}%"
                else:
                    row['Strategy'] = f"{value:.3f}"
                
                # Add benchmark if available
                if benchmark_metrics and key in benchmark_metrics:
                    bench_value = benchmark_metrics[key]
                    if key in ['tot_return', 'cagr', 'max_dd']:
                        row['Benchmark'] = f"{bench_value * 100:.2f}%"
                    else:
                        row['Benchmark'] = f"{bench_value:.3f}"
                
                data.append(row)
        
        return pd.DataFrame(data)
    
    def comparison_bar_chart(
        self,
        metrics: dict,
        benchmark_metrics: dict,
        title: str = "Performance Comparison"
    ) -> go.Figure:
        """Create bar chart comparing strategy to benchmark.
        
        Args:
            metrics: Strategy metrics
            benchmark_metrics: Benchmark metrics
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Select key metrics to compare
        compare_keys = ['tot_return', 'cagr', 'sharpe']
        labels = ['Total Return', 'CAGR', 'Sharpe Ratio']
        
        strategy_values = []
        benchmark_values = []
        
        for key in compare_keys:
            if key in metrics:
                value = metrics[key]
                # Convert to percentage for returns
                if key in ['tot_return', 'cagr']:
                    value = value * 100
                strategy_values.append(value)
            else:
                strategy_values.append(0)
            
            if benchmark_metrics and key in benchmark_metrics:
                value = benchmark_metrics[key]
                if key in ['tot_return', 'cagr']:
                    value = value * 100
                benchmark_values.append(value)
            else:
                benchmark_values.append(0)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Strategy',
            x=labels,
            y=strategy_values,
            marker=dict(color='blue')
        ))
        
        fig.add_trace(go.Bar(
            name='Benchmark',
            x=labels,
            y=benchmark_values,
            marker=dict(color='gray')
        ))
        
        fig.update_layout(
            title=title,
            yaxis_title="Value",
            barmode='group',
            template='plotly_white'
        )
        
        return fig
    
    def monthly_returns_heatmap(
        self,
        equity_df: pd.DataFrame,
        title: str = "Monthly Returns Heatmap"
    ) -> go.Figure:
        """Create heatmap of monthly returns.
        
        Args:
            equity_df: DataFrame with date and value columns
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Calculate monthly returns
        df = equity_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        monthly = df['value'].resample('M').last()
        monthly_returns = monthly.pct_change() * 100
        
        # Create pivot table for heatmap
        df_returns = pd.DataFrame({
            'year': monthly_returns.index.year,
            'month': monthly_returns.index.month,
            'return': monthly_returns.values
        })
        
        pivot = df_returns.pivot(index='month', columns='year', values='return')
        
        # Month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=month_labels,
            colorscale='RdYlGn',
            zmid=0,
            text=pivot.values,
            texttemplate='%{text:.1f}%',
            textfont={"size": 10},
            colorbar=dict(title="Return (%)")
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Year",
            yaxis_title="Month",
            template='plotly_white'
        )
        
        return fig
