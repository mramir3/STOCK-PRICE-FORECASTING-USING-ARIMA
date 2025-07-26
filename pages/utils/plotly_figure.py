import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import ta

def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns), fill_color='paleturquoise', align='left'),
        cells=dict(values=[df[col] for col in df.columns], fill_color='lavender', align='left'))
    ])
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig

def get_period_data(df, period):
    if period == "max": return df
    offset_map = {'d': 'D', 'mo': 'M', 'y': 'Y'}
    num, freq = int(period[:-1]), offset_map[period[-1]]
    end_date = df.index.max()
    if freq == 'Y': start_date = end_date - pd.DateOffset(years=num)
    elif freq == 'M': start_date = end_date - pd.DateOffset(months=num)
    else: start_date = end_date - pd.DateOffset(days=num)
    return df[df.index >= start_date]

def candlestick(df, period):
    df_period = get_period_data(df, period)
    fig = go.Figure(data=[go.Candlestick(x=df_period.index, open=df_period['Open'], high=df_period['High'], low=df_period['Low'], close=df_period['Close'])])
    fig.update_layout(title_text='Candlestick Chart', xaxis_rangeslider_visible=False, template='plotly_dark')
    return fig

def close_chart(df, period):
    df_period = get_period_data(df, period)
    fig = go.Figure(data=[go.Scatter(x=df_period.index, y=df_period['Close'], mode='lines', name='Close Price')])
    fig.update_layout(title_text='Close Price', template='plotly_dark')
    return fig

def RSI(df, period):
    df_period = get_period_data(df, period).copy()
    df_period['RSI'] = ta.momentum.RSIIndicator(close=df_period['Close'], window=14).rsi()
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=df_period.index, y=df_period['RSI'], name='RSI'), row=1, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(title_text='Relative Strength Index (RSI)', template='plotly_dark')
    return fig

def MACD(df, period):
    df_period = get_period_data(df, period).copy()
    macd = ta.trend.MACD(close=df_period['Close'])
    df_period['MACD'], df_period['MACD_signal'] = macd.macd(), macd.macd_signal()
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=df_period.index, y=df_period['MACD'], name='MACD'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_period.index, y=df_period['MACD_signal'], name='Signal Line'), row=1, col=1)
    fig.update_layout(title_text='MACD', template='plotly_dark')
    return fig

def Moving_average(df, period):
    df_period = get_period_data(df, period).copy()
    df_period['SMA50'] = df_period['Close'].rolling(window=50).mean()
    df_period['SMA200'] = df_period['Close'].rolling(window=200).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_period.index, y=df_period['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df_period.index, y=df_period['SMA50'], mode='lines', name='50-Day SMA'))
    fig.add_trace(go.Scatter(x=df_period.index, y=df_period['SMA200'], mode='lines', name='200-Day SMA'))
    fig.update_layout(title_text='Moving Averages', template='plotly_dark')
    return fig

def Moving_average_forecast(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Historical/Forecasted Price'))
    fig.update_layout(title_text='Price Forecast vs. Historical Data', template='plotly_dark', xaxis_title="Date", yaxis_title="Price (INR)")
    return fig