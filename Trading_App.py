import streamlit as st

# Set page configuration - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Trading App Home",
    page_icon="🏠",
    layout="wide",
)

# --- Main Page Content ---
st.title("STOCK PRICE FORECASTING :bar_chart:")
st.subheader("We provide the greatest platform for you to collect all information prior to investing in stocks.")

st.markdown("---")

# Use columns for a cleaner layout
col1, col2 = st.columns([1, 2])

with col1:
    st.image("app.png", use_column_width=True)

with col2:
    st.markdown("## We provide the following services")
    st.markdown("#### :one: Stock Analysis")
    st.write("Navigate to the **Stock Analysis** page to see key data, financial statements, and historical charts for top NSE-listed companies like TCS, Cipla, and HDFC Bank.")
    
    st.markdown("#### :two: Stock Prediction")
    st.write("Navigate to the **Stock Prediction** page to see predicted closing prices for the next 30 days based on a sophisticated time-series forecasting model.")
    
    st.info("Please use the navigation panel on the left to select a service.")

st.markdown("---")
st.write("Disclaimer: This is not financial advice. All data is for informational purposes only.")