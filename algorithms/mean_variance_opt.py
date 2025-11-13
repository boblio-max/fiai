import pandas as pd
from core.utils import fetch_stock_data
from pypfopt import EfficientFrontier, risk_models, expected_returns

def run_mean_variance_opt(ticker):
    """
    (Full Implementation)
    Runs Markowitz Mean-Variance Optimization.
    Since this is a portfolio tool, we run the user's ticker
    against a standard "60/40-like" market portfolio.
    """
    try:
        # 1. Define the portfolio universe
        # We test the ticker against a diversified set of assets.
        base_portfolio = ['SPY', 'QQQ', 'TLT', 'GLD']
        
        # Add the user's ticker, ensuring no duplicates
        if ticker.upper() in base_portfolio:
            portfolio_tickers = base_portfolio
        else:
            portfolio_tickers = [ticker] + base_portfolio

        # 2. Fetch data for all assets
        all_data = {}
        for t in portfolio_tickers:
            all_data[t] = fetch_stock_data(t, period="3y")['Close']
        
        df = pd.DataFrame(all_data).dropna()

        # 3. Run the Optimization
        # Calculate expected returns and sample covariance
        mu = expected_returns.mean_historical_return(df)
        S = risk_models.sample_cov(df)

        # Optimize for max Sharpe Ratio
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe()
        
        # Get the weight assigned to the user's ticker
        ticker_weight = weights.get(ticker, 0)
        
        # 4. Generate Signal
        if ticker_weight > 0.30: # Strong allocation
            rec = 'Buy'
            summary = f"Strong Buy Signal: In a max-Sharpe portfolio, {ticker} is allocated {ticker_weight:.2%}."
        elif ticker_weight > 0.05: # Modest allocation
            rec = 'Hold'
            summary = f"Hold Signal: In a max-Sharpe portfolio, {ticker} receives a modest allocation of {ticker_weight:.2%}."
        else: # Zero or negligible allocation
            rec = 'Sell'
            summary = f"Sell Signal: In a max-Sharpe portfolio, {ticker} is allocated {ticker_weight:.2%}, suggesting other assets offer better risk-adjusted returns."

        # --- Format Chart Data (Pie chart of weights) ---
        cleaned_weights = {k: v for k, v in weights.items() if v > 0.001} # Clean small weights

        chart_data = {
            'labels': list(cleaned_weights.keys()),
            'importance': list(cleaned_weights.values())
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data,
            'chart_type': 'pie' # Tell the frontend to use a pie/doughnut chart
        }
        
    except Exception as e:
        return {"error": f"Portfolio optimization failed: {str(e)}"}
