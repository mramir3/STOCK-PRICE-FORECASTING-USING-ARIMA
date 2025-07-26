import streamlit as st
import pandas as pd
import yfinance as yf
# This import should be correct from our previous fixes
from pages.utils.plotly_figure import close_chart, candlestick, RSI, Moving_average, MACD

st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="wide")
st.title("📈 Stock Analysis")

STOCK_OPTIONS = {
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "Cipla Ltd.": "CIPLA.NS",
    "HDFC Bank Ltd.": "HDFCBANK.NS"
}

selected_stock_name = st.selectbox('Select a Stock for Analysis', options=list(STOCK_OPTIONS.keys()))
ticker = STOCK_OPTIONS[selected_stock_name]

@st.cache_data
def get_stock_info(ticker):
    return yf.Ticker(ticker).info

@st.cache_data
def get_historical_data(ticker):
    return yf.Ticker(ticker).history(period='max')

if 'period' not in st.session_state:
    st.session_state.period = '1y'

def set_period(period):
    st.session_state.period = period

if selected_stock_name:
    try:
        info = get_stock_info(ticker)
        # --- CHANGE 1: Get historical data ONCE, early on. ---
        data = get_historical_data(ticker)

        if not info or 'shortName' not in info or data.empty:
            st.error(f"Could not retrieve valid data for: {ticker}. The ticker might be incorrect or delisted.")
        else:
            # --- Company Info ---
            st.subheader(f"{info.get('shortName', 'N/A')} ({info.get('symbol', 'N/A')})")
            with st.expander("Company Profile", expanded=True):
                st.write(info.get('longBusinessSummary', 'No business summary available.'))
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Website:** {info.get('website', 'N/A')}")

            # --- Financial Metrics ---
            st.subheader("Key Financial Metrics")
            col1, col2 = st.columns(2)
            with col1:
                df1 = pd.DataFrame({'Metric': ['Market Cap', 'Beta', 'Trailing EPS', 'Trailing PE'], 'Value': [info.get("marketCap"), info.get("beta"), info.get("trailingEps"), info.get("trailingPE")]}).set_index('Metric')
                st.table(df1)
            with col2:
                df2 = pd.DataFrame({'Metric': ['Quick Ratio', 'Revenue/Share', 'Profit Margins', 'Debt to Equity'], 'Value': [info.get("quickRatio"), info.get("revenuePerShare"), info.get("profitMargins"), info.get("debtToEquity")]}).set_index('Metric')
                st.table(df2)

            # --- CHANGE 2: Insert the new Daily Performance section here. ---
            st.subheader("Recent Performance")
            if len(data) >= 2:
                # Create two columns for a cleaner layout
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Daily Change Metric
                    last_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    daily_change_val = last_price - prev_price
                    daily_change_pct = (daily_change_val / prev_price) * 100
                    st.metric(
                        label="Last Close Price",
                        value=f"{last_price:.2f} {info.get('currency', '')}",
                        delta=f"{daily_change_val:.2f} ({daily_change_pct:.2f}%)"
                    )
                
                with col2:
                    # Historical Data Table
                    st.write("**Historical Data (Last 10 Days)**")
                    recent_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10).sort_index(ascending=False)
                    st.dataframe(
                        recent_data.style.format({
                            'Open': '{:.2f}', 'High': '{:.2f}', 'Low': '{:.2f}',
                            'Close': '{:.2f}', 'Volume': '{:,}'
                        }),
                        use_container_width=True
                    )
            else:
                st.warning("Not enough historical data to display recent performance.")
            # --- End of new section ---

            # --- Charting Section ---
            st.markdown("---")
            st.subheader("Interactive Chart")
            if not data.empty:
                cols = st.columns(7)
                periods = ['5d', '1mo', '6mo', 'ytd', '1y', '5y', 'max']
                for i, p in enumerate(periods):
                    cols[i].button(p.upper(), on_click=set_period, args=[p], use_container_width=True, key=f"analysis_{p}")
                
                c1, c2 = st.columns([1, 1])
                chart_type = c1.selectbox('Chart Type', ('Line', 'Candle'), key='analysis_chart')
                indicator_ops = ['RSI', 'MACD'] if chart_type == 'Candle' else ['RSI', 'Moving Average', 'MACD']
                indicator = c2.selectbox('Indicator', indicator_ops, key='analysis_indicator')
                
                if chart_type == 'Line':
                    st.plotly_chart(Moving_average(data, st.session_state.period) if indicator == 'Moving Average' else close_chart(data, st.session_state.period), use_container_width=True)
                else:
                    st.plotly_chart(candlestick(data, st.session_state.period), use_container_width=True)
                
                if indicator == 'RSI': st.plotly_chart(RSI(data, st.session_state.period), use_container_width=True)
                elif indicator == 'MACD': st.plotly_chart(MACD(data, st.session_state.period), use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")