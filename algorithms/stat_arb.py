import pandas as pd
import numpy as np
from core.utils import fetch_stock_data

def run_stat_arb(ticker1, ticker2, window=20):
    """
    Performs a pairs trading analysis using the Z-Score of the spread.
    """
    try:
        data1 = fetch_stock_data(ticker1, period="1y")['Close']
        data2 = fetch_stock_data(ticker2, period="1y")['Close']
        
        # Align data
        df = pd.DataFrame({'T1': data1, 'T2': data2}).dropna()
        
        if df.empty:
            return {"error": "No overlapping data for tickers."}

        # Calculate spread (using ratio)
        df['Spread'] = np.log(df['T1'] / df['T2'])
        
        # Calculate Z-Score
        df['Mean'] = df['Spread'].rolling(window=window).mean()
        df['StdDev'] = df['Spread'].rolling(window=window).std()
        df['Z_Score'] = (df['Spread'] - df['Mean']) / df['StdDev']
        
        df.dropna(inplace=True)
        
        # --- Generate Signal ---
        latest_z = df['Z_Score'].iloc[-1]
        
        if latest_z > 2.0:
            rec = 'Sell'
            summary = f"Spread Z-Score ({latest_z:.2f}) is > 2.0. Signal: Short the spread (Sell {ticker1}, Buy {ticker2})."
        elif latest_z < -2.0:
            rec = 'Buy'
            summary = f"Spread Z-Score ({latest_z:.2f}) is < -2.0. Signal: Long the spread (Buy {ticker1}, Sell {ticker2})."
        else:
            rec = 'Hold'
            summary = f"Spread Z-Score ({latest_z:.2f}) is between -2.0 and 2.0. No signal."
            
        # --- Format Chart Data ---
        chart_data = {
            'labels': df.index.strftime('%Y-%m-%d').tolist(),
            'z_score': df['Z_Score'].tolist(),
            'upper_band': [2.0] * len(df),
            'lower_band': [-2.0] * len(df)
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data
        }
        
    except Exception as e:
        return {"error": str(e)}
