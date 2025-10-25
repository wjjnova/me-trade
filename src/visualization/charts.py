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

    def equity_trend_chart(
        self,
        equity_df: pd.DataFrame,
        title: str = "Equity Trend"
    ) -> go.Figure:
        """Create equity curve chart highlighting gain/loss points.

        Args:
            equity_df: DataFrame with date, value, and return_pct columns
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_df['date'],
            y=equity_df['value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2)
        ))

        if 'return_pct' in equity_df.columns:
            gain_mask = equity_df['return_pct'] >= 0
            loss_mask = ~gain_mask

            if gain_mask.any():
                gain_df = equity_df[gain_mask]
                fig.add_trace(go.Scatter(
                    x=gain_df['date'],
                    y=gain_df['value'],
                    mode='markers',
                    name='Gain',
                    marker=dict(color='#2e7d32', symbol='triangle-up', size=9),
                    hovertemplate=(
                        "Date: %{x}<br>Value: $%{y:,.2f}<br>Daily Return: %{customdata:.2f}%<extra></extra>"
                    ),
                    customdata=gain_df['return_pct'] * 100
                ))

            if loss_mask.any():
                loss_df = equity_df[loss_mask]
                fig.add_trace(go.Scatter(
                    x=loss_df['date'],
                    y=loss_df['value'],
                    mode='markers',
                    name='Loss',
                    marker=dict(color='#c62828', symbol='triangle-down', size=9),
                    hovertemplate=(
                        "Date: %{x}<br>Value: $%{y:,.2f}<br>Daily Return: %{customdata:.2f}%<extra></extra>"
                    ),
                    customdata=loss_df['return_pct'] * 100
                ))

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )

        return fig

    def daily_returns_bar_chart(
        self,
        equity_df: pd.DataFrame,
        title: str = "Daily Gain/Loss"
    ) -> go.Figure:
        """Create bar chart for daily returns showing gains vs losses.

        Args:
            equity_df: DataFrame with date and return_pct columns
            title: Chart title

        Returns:
            Plotly figure
        """
        if 'return_pct' not in equity_df.columns:
            raise ValueError("equity_df must include a 'return_pct' column")

        colors = equity_df['return_pct'].apply(
            lambda val: '#2e7d32' if val >= 0 else '#c62828'
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=equity_df['date'],
            y=equity_df['return_pct'] * 100,
            marker=dict(color=colors),
            name='Daily Return',
            hovertemplate="Date: %{x}<br>Return: %{y:.2f}%<extra></extra>"
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Return (%)",
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
    
    def candlestick_chart(
        self,
        data: pd.DataFrame,
        indicators: Optional[pd.DataFrame] = None,
        title: str = "K-Line Chart",
        show_volume: bool = True
    ) -> go.Figure:
        """Create candlestick (K-line) chart with optional indicators.
        
        Args:
            data: DataFrame with date, open, high, low, close, volume columns
            indicators: Optional DataFrame with indicator columns (SMA, RSI, etc.)
            title: Chart title
            show_volume: Whether to show volume subplot
            
        Returns:
            Plotly figure with candlestick chart and optional volume/indicators
        """
        from plotly.subplots import make_subplots
        
        # Determine number of subplots
        num_rows = 1
        row_heights = [0.7]
        subplot_titles = [title]
        
        if show_volume and 'volume' in data.columns:
            num_rows += 1
            row_heights.append(0.3)
            subplot_titles.append('Volume')
        
        # Create subplots
        fig = make_subplots(
            rows=num_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=subplot_titles
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data['date'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='OHLC',
                increasing=dict(line=dict(color='#26a69a')),  # Green
                decreasing=dict(line=dict(color='#ef5350'))   # Red
            ),
            row=1, col=1
        )
        
        # Add indicators if provided
        if indicators is not None and not indicators.empty:
            # Add moving averages
            if 'SMA_20' in indicators.columns:
                fig.add_trace(
                    go.Scatter(
                        x=indicators['date'],
                        y=indicators['SMA_20'],
                        name='SMA 20',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'SMA_50' in indicators.columns:
                fig.add_trace(
                    go.Scatter(
                        x=indicators['date'],
                        y=indicators['SMA_50'],
                        name='SMA 50',
                        line=dict(color='blue', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'SMA_200' in indicators.columns:
                fig.add_trace(
                    go.Scatter(
                        x=indicators['date'],
                        y=indicators['SMA_200'],
                        name='SMA 200',
                        line=dict(color='red', width=1)
                    ),
                    row=1, col=1
                )
            
            # Add Bollinger Bands
            if 'BB_Upper' in indicators.columns and 'BB_Lower' in indicators.columns:
                fig.add_trace(
                    go.Scatter(
                        x=indicators['date'],
                        y=indicators['BB_Upper'],
                        name='BB Upper',
                        line=dict(color='gray', width=1, dash='dot'),
                        showlegend=True
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=indicators['date'],
                        y=indicators['BB_Lower'],
                        name='BB Lower',
                        line=dict(color='gray', width=1, dash='dot'),
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # Add volume bars if requested
        if show_volume and 'volume' in data.columns:
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(data['close'], data['open'])]
            
            fig.add_trace(
                go.Bar(
                    x=data['date'],
                    y=data['volume'],
                    name='Volume',
                    marker=dict(color=colors),
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            height=600 if show_volume else 500,
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            template='plotly_white'
        )
        
        fig.update_yaxes(title_text="Price", row=1, col=1)
        if show_volume:
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    @staticmethod
    def resample_ohlcv(data: pd.DataFrame, timeframe: str = 'W') -> pd.DataFrame:
        """Resample OHLCV data to different timeframe.
        
        Args:
            data: DataFrame with date, open, high, low, close, volume columns
            timeframe: Resample frequency ('D'=day, 'W'=week, 'M'=month, 'Q'=quarter)
            
        Returns:
            Resampled DataFrame
        """
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Define aggregation rules
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        resampled.reset_index(inplace=True)
        
        return resampled
