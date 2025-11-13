import pandas as pd
import numpy as np
from core.utils import fetch_stock_data

def run_momentum(ticker, short_window=50, long_window=200):
    """
    Runs a simple moving average (SMA) crossover strategy.
    """
    try:
        data = fetch_stock_data(ticker, period="3y")
        
        df = pd.DataFrame(data['Close'])
        df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
        df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()
        
        df.dropna(inplace=True)
        
        # --- Generate Signal ---
        df['Signal'] = 0
        df['Signal'][short_window:] = np.where(df['SMA_Short'][short_window:] > df['SMA_Long'][short_window:], 1, 0)
        df['Position'] = df['Signal'].diff()
        
        latest = df.iloc[-1]
        
        if latest['SMA_Short'] > latest['SMA_Long']:
            rec = 'Buy'
            summary = f"50-day SMA ({latest['SMA_Short']:.2f}) is above 200-day SMA ({latest['SMA_Long']:.2f}). Bullish trend."
        else:
            rec = 'Sell'
            summary = f"50-day SMA ({latest['SMA_Short']:.2f}) is below 200-day SMA ({latest['SMA_Long']:.2f}). Bearish trend."
            
        # --- Format Chart Data ---
        chart_data = {
            'labels': df.index.strftime('%Y-%m-%d').tolist(),
            'price': df['Close'].tolist(),
            'sma_short': df['SMA_Short'].tolist(),
            'sma_long': df['SMA_Long'].tolist(),
            'buy_signals': df.index[df['Position'] == 1].strftime('%Y-%m-%d').tolist(),
            'sell_signals': df.index[df['Position'] == -1].strftime('%Y-%m-%d').tolist()
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data
        }
        
    except Exception as e:
        return {"error": str(e)}
