import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
from sklearn.metrics import mean_squared_error

def get_data(ticker):
    """Fetches the last 5 years of close price data."""
    data = yf.download(ticker, period='5y')
    return data[['Close']] if not data.empty else pd.DataFrame()

def get_rolling_mean(data, window=30):
    """Calculates the rolling mean."""
    return data.rolling(window=window).mean().dropna()

def get_differencing_order(timeseries):
    """Finds the order of differencing 'd' for ARIMA model using ADF test."""
    result = adfuller(timeseries.dropna())
    if result[1] <= 0.05:
        return 0
    result = adfuller(timeseries.diff().dropna())
    if result[1] <= 0.05:
        return 1
    return 2

def train_and_forecast_arima(data, d_order, p=5, q=0, steps=30):
    """
    Trains an ARIMA model, evaluates it, and forecasts future steps.
    This version ensures a clean numpy array is passed to the model.
    """
    # --- THIS IS THE KEY FIX ---
    # Convert the input Pandas Series to a clean NumPy array of float values.
    # We keep the original `data` Series to get the date index later.
    data_values = data.astype(float).values
    # --- END OF FIX ---

    # Use 80% of data for training, 20% for testing to get a meaningful RMSE
    train_size = int(len(data_values) * 0.8)
    train_data, test_data = data_values[0:train_size], data_values[train_size:len(data_values)]

    # --- 1. Get a meaningful RMSE on the test set ---
    history = [x for x in train_data]
    predictions = []
    for t in range(len(test_data)):
        # We pass the list `history` which is already clean.
        model_eval = ARIMA(history, order=(p, d_order, q))
        model_fit_eval = model_eval.fit()
        output = model_fit_eval.forecast()
        yhat = output[0]
        predictions.append(yhat)
        obs = test_data[t]
        history.append(obs)
    
    rmse = np.sqrt(mean_squared_error(test_data, predictions))

    # --- 2. Train the final model on ALL data (as a clean numpy array) ---
    final_model = ARIMA(data_values, order=(p, d_order, q))
    final_model_fit = final_model.fit()
    
    forecast_values = final_model_fit.forecast(steps=steps)
    
    # Use the index from the original `data` Series to create the future date range
    last_date = data.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps)
    
    forecast_df = pd.DataFrame(forecast_values, index=future_dates, columns=['Close'])
    
    return rmse, forecast_df