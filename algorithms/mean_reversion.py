import pandas as pd
from core.utils import fetch_stock_data

def run_mean_reversion(ticker, window=20, num_std_dev=2):
    """
    Runs a mean reversion strategy using Bollinger Bands.
    """
    try:
        data = fetch_stock_data(ticker, period="1y")
        
        df = pd.DataFrame(data['Close'])
        df['SMA'] = df['Close'].rolling(window=window).mean()
        df['StdDev'] = df['Close'].rolling(window=window).std()
        
        df['Upper_Band'] = df['SMA'] + (df['StdDev'] * num_std_dev)
        df['Lower_Band'] = df['SMA'] - (df['StdDev'] * num_std_dev)
        
        df.dropna(inplace=True)
        
        # --- Generate Signal ---
        latest = df.iloc[-1]
        
        if latest['Close'] < latest['Lower_Band']:
            rec = 'Buy'
            summary = f"Price ({latest['Close']:.2f}) is below the lower Bollinger Band ({latest['Lower_Band']:.2f}). Asset is oversold."
        elif latest['Close'] > latest['Upper_Band']:
            rec = 'Sell'
            summary = f"Price ({latest['Close']:.2f}) is above the upper Bollinger Band ({latest['Upper_Band']:.2f}). Asset is overbought."
        else:
            rec = 'Hold'
            summary = f"Price ({latest['Close']:.2f}) is within the bands. No signal."
            
        # --- Format Chart Data ---
        chart_data = {
            'labels': df.index.strftime('%Y-%m-%d').tolist(),
            'price': df['Close'].tolist(),
            'sma': df['SMA'].tolist(),
            'upper_band': df['Upper_Band'].tolist(),
            'lower_band': df['Lower_Band'].tolist()
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data
        }
        
    except Exception as e:
        return {"error": str(e)}
