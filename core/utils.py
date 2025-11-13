import yfinance as yf
import pandas as pd
from functools import lru_cache

# A list of diverse, high-volume stocks for the homepage
DEFAULT_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM',
    'V', 'JNJ', 'WMT', 'UNH', 'XOM', 'GS', 'BA'
]

# Use a simple lru_cache for in-memory caching of API calls
# This speeds up repeated requests for the same ticker
@lru_cache(maxsize=128)
def fetch_stock_data(ticker, period="1y", interval="1d"):
    """
    Fetches stock data from yfinance and returns a pandas DataFrame.
    Includes stock info (like longName) in the DataFrame's .info attribute.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    
    if data.empty:
        raise Exception(f"No data found for ticker {ticker} with period {period}")
    
    # Attach the info dict to the dataframe for easy access in routes
    data.info = stock.info
    return data

def simple_find_peaks(data, prominence=1):
    """
    A simple implementation to find peak indices in a list of data.
    'prominence' is a basic filter to avoid tiny, insignificant peaks.
    """
    peaks = []
    if len(data) < 3:
        return []
        
    for i in range(1, len(data) - 1):
        # Check if it's a local maximum
        if data[i] > data[i-1] and data[i] > data[i+1]:
            # Basic prominence check: is it significantly higher than its neighbors?
            left_dip = data[i] - data[i-1]
            right_dip = data[i] - data[i+1]
            
            if min(left_dip, right_dip) >= prominence:
                peaks.append(i)
                
    return peaks
