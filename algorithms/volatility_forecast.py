import pandas as pd
import numpy as np
from core.utils import fetch_stock_data
from arch import arch_model

def run_volatility_forecast(ticker):
    """
    (Full Implementation)
    Fits a GARCH(1,1) model to forecast volatility.
    """
    try:
        data = fetch_stock_data(ticker, period="2y")
        
        # Calculate log returns, which are standard for GARCH models
        returns = 100 * np.log(data['Close'] / data['Close'].shift(1)).dropna()
        
        if returns.empty:
            return {"error": "Not enough data to calculate returns."}

        # --- GARCH Model ---
        # We use a GARCH(1,1) model, which is the most common specification.
        # 'vol='Garch'' specifies the GARCH model. p=1, q=1.
        model = arch_model(returns, vol='Garch', p=1, q=1)
        
        # Fit the model. disp='off' disables the convergence output
        model_fit = model.fit(disp='off')
        
        # --- Forecast ---
        # Forecast the next 1 day
        forecast = model_fit.forecast(horizon=1)
        
        # Get the forecasted variance and convert to annualized volatility
        # The variance is in 'h.1'
        var_forecast = forecast.variance['h.1'].iloc[-1]
        
        # GARCH model was on returns * 100, so variance is 10000x.
        # We divide by 100 to get volatility (std dev)
        vol_forecast_daily = np.sqrt(var_forecast) / 100
        vol_forecast_annualized = vol_forecast_daily * np.sqrt(252)
        
        # --- Context ---
        current_vol_annualized = (returns.std() / 100) * np.sqrt(252)

        rec = 'Hold' # Volatility models are non-directional
        summary = (
            f"The GARCH(1,1) model forecasts an annualized volatility of {vol_forecast_annualized:.2%} "
            f"for the next trading day. This compares to the 2-year average "
            f"historical volatility of {current_vol_annualized:.2%}. "
            f"This model is for risk assessment, not price direction."
        )
            
        # --- Format Chart Data (Volatility Forecast vs. Historical) ---
        chart_data = {
            'labels': returns.index.strftime('%Y-%m-%d').tolist(),
            # Plotting conditional volatility from the model
            'volatility': (model_fit.conditional_volatility / 100) * np.sqrt(252)
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data
        }
        
    except Exception as e:
        return {"error": f"GARCH model failed to converge or run: {str(e)}"}
