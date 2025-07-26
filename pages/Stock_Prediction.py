import streamlit as st
import pandas as pd
# No changes to imports needed
from pages.utils.model_train import get_data, get_rolling_mean, get_differencing_order, train_and_forecast_arima
from pages.utils.plotly_figure import Moving_average_forecast

st.set_page_config(page_title="Stock Prediction", page_icon="🔮", layout="wide")
st.title("🔮 Stock Prediction (ARIMA Model)")

STOCK_OPTIONS = {
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "Cipla Ltd.": "CIPLA.NS",
    "HDFC Bank Ltd.": "HDFCBANK.NS"
}

selected_stock_name = st.selectbox('Select a Stock for Prediction', options=list(STOCK_OPTIONS.keys()))
ticker = STOCK_OPTIONS[selected_stock_name]

@st.cache_data
def run_full_prediction_pipeline(ticker):
    """
    A single cached function to run the whole pipeline.
    """
    close_price = get_data(ticker)
    if close_price.empty:
        return None, None, None
        
    rolling_price = get_rolling_mean(close_price)
    d_order = get_differencing_order(rolling_price['Close'])
    
    # --- THIS IS THE ONLY LINE THAT CHANGES ---
    # We pass the Pandas Series `rolling_price['Close']` instead of the numpy array `rolling_price.values`
    rmse, forecast_df = train_and_forecast_arima(rolling_price['Close'], d_order)
    # --- END OF CHANGE ---

    # Combine historical and forecast data for plotting
    combined_plot_data = pd.concat([rolling_price, forecast_df])
    
    return rmse, forecast_df, combined_plot_data

if st.button("Generate Prediction"):
    if not ticker:
        st.warning("Please select a stock.")
    else:
        with st.spinner(f"Running prediction for {ticker}... This may take a minute."):
            try:
                rmse, forecast_data, plot_data = run_full_prediction_pipeline(ticker)
                
                if rmse is None:
                    st.error(f"Could not retrieve data or run prediction for {ticker}.")
                else:
                    st.success(f"Prediction complete for {ticker}!")
                    
                    st.metric(label="Model RMSE (Root Mean Squared Error)", value=f"{rmse:.2f} INR")
                    st.info("RMSE indicates the model's average prediction error on a test set of historical data. Lower is better.")
                    
                    st.subheader('Forecasted Close Price (Next 30 days)')
                    st.dataframe(
                        forecast_data.style.format("{:.2f}"),
                        use_container_width=True
                    )
                    
                    st.subheader("Prediction Chart")
                    st.plotly_chart(Moving_average_forecast(plot_data.iloc[-200:]), use_container_width=True)
                    st.caption("The chart shows the last 170 days of historical (30-day rolling average) price and the 30-day forecast.")

            except Exception as e:
                st.error(f"Failed to generate prediction. Error: {e}")