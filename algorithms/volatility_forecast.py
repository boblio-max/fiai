import pandas as pd
import numpy as np
from core.utils import fetch_stock_data

def run_volatility_forecast(ticker, window=20):
    """
    (Simple Proxy)
    Calculates historical rolling volatility as a proxy for a GARCH model.
    """
    try:
        data = fetch_stock_data(ticker, period="1y")
        
        df = pd.DataFrame(data['Close'])
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Calculate annualized volatility
        df['Volatility'] = df['Log_Return'].rolling(window=window).std() * np.sqrt(252)
        df.dropna(inplace=True)

        latest_vol = df['Volatility'].iloc[-1]
        avg_vol = df['Volatility'].mean()

        rec = 'Hold' # Volatility models are usually for risk, not direction
        summary = (
            f"Current {window}-day annualized volatility is {latest_vol:.2%}. "
            f"The 1-year average volatility is {avg_vol:.2%}. "
            f"This is a simple proxy; a full GARCH(1,1) model would provide a more robust forecast. "
            f"This model is non-directional, so the vote is 'Hold'."
        )
            
        # --- Format Chart Data ---
        chart_data = {
            'labels': df.index.strftime('%Y-%m-%d').tolist(),
            'volatility': df['Volatility'].tolist()
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data
        }
        
    except Exception as e:
        return {"error": str(e)}
