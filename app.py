import random
import json
import pandas as pd
from flask import Flask, render_template, jsonify, request, abort

# Import core utilities
from core.utils import fetch_stock_data, simple_find_peaks, DEFAULT_STOCKS
from core.council import run_council_decision

# Import all algorithm functions
from algorithms import stat_arb, momentum, mean_reversion, ml_predictive, \
    reinforcement, factor_investing, market_making, sentiment, \
    volatility_forecast, mean_variance_opt

app = Flask(__name__)

# --- Metadata for Strategies ---
# This dictionary drives the algorithm pages dynamically.
STRATEGY_METADATA = {
    'stat_arb': {
        'title': 'Statistical Arbitrage (Pairs Trading)',
        'description': 'Identifies two highly correlated stocks and trades on the temporary divergence of their price spread. It assumes the spread will revert to its historical mean.',
        'math': 'Calculates the Z-Score of the price ratio spread (StockA / StockB). A Z-Score > 2.0 suggests shorting the spread (Sell A, Buy B), while a Z-Score < -2.0 suggests longing the spread (Buy A, Sell B).',
        'tickers_required': 2,
        'function': stat_arb.run_stat_arb
    },
    'momentum': {
        'title': 'Momentum / Trend Following',
        'description': 'A classic strategy that assumes assets that have performed well recently will continue to perform well (and vice-versa). This implementation uses a Simple Moving Average (SMA) crossover.',
        'math': 'Generates a "Buy" signal when the short-term 50-day SMA crosses above the long-term 200-day SMA. A "Sell" signal is generated when the 50-day SMA crosses below the 200-day SMA.',
        'tickers_required': 1,
        'function': momentum.run_momentum
    },
    'mean_reversion': {
        'title': 'Mean Reversion (Bollinger Bands)',
        'description': 'This strategy operates on the assumption that stock prices will revert to their historical average or mean. It identifies overbought or oversold conditions.',
        'math': 'Uses Bollinger Bands (20-day SMA ± 2 standard deviations). A "Buy" signal occurs when the price drops below the lower band. A "Sell" signal occurs when the price rises above the upper band.',
        'tickers_required': 1,
        'function': mean_reversion.run_mean_reversion
    },
    'ml_predictive': {
        'title': 'Machine Learning (Random Forest)',
        'description': '(Placeholder Implementation) Uses a Random Forest classifier to predict the next day\'s price direction (Up or Down) based on lagged returns and moving average features.',
        'math': 'Features: Lag-1, Lag-5 returns, 10-day rolling mean. Target: 1 if next-day close > today\'s close, 0 otherwise. A simple model is trained on 80% of the data to predict the most recent signal.',
        'tickers_required': 1,
        'function': ml_predictive.run_ml_predictive
    },
    'reinforcement': {
        'title': 'Reinforcement Learning (Deep Q-Learning)',
        'description': '(Conceptual Placeholder) An advanced AI strategy where an "agent" learns the optimal trading policy (Buy, Sell, Hold) by interacting with the market environment to maximize a cumulative reward.',
        'math': 'This page is a placeholder. A full implementation would involve defining a state space (e.g., price, volume, indicators), an action space (Buy/Sell/Hold), and a reward function, then training a deep neural network (e.g., Deep Q-Network) over millions of simulated steps.',
        'tickers_required': 1,
        'function': reinforcement.run_reinforcement
    },
    'factor_investing': {
        'title': 'Multi-Factor Investing',
        'description': '(Conceptual Placeholder) A portfolio strategy that selects assets based on their exposure to specific "factors" (e.g., Value, Momentum, Quality, Low-Volatility) that have historically provided excess returns.',
        'math': 'This is a placeholder. A real implementation would involve screening a universe of stocks, calculating factor scores for each (e.g., P/E ratio for Value, 12-month return for Momentum), and building a portfolio that optimizes for exposure to desired factors.',
        'tickers_required': 1,
        'function': factor_investing.run_factor_investing
    },
    'market_making': {
        'title': 'Market Making Simulation',
        'description': '(Conceptual Placeholder) A high-frequency strategy that involves providing liquidity to the market by placing simultaneous buy (bid) and sell (ask) orders, capturing the "bid-ask spread".',
        'math': 'This is a placeholder. A simulation would model inventory risk and order book dynamics, using models like Avellaneda-Stoikov to determine the optimal bid and ask prices relative to a "fair" value.',
        'tickers_required': 1,
        'function': market_making.run_market_making
    },
    'sentiment': {
        'title': 'NLP Sentiment Analysis',
        'description': '(Conceptual Placeholder) Trades based on the collective sentiment (positive, negative, neutral) extracted from news headlines, social media (like X/Twitter), or financial reports.',
        'math': 'This is a placeholder. A real implementation would use a Natural Language Processing (NLP) model (e.g., BERT, VADER) to score text data, aggregate sentiment over time, and generate trades when sentiment crosses a threshold (e.g., Buy on high positive sentiment).',
        'tickers_required': 1,
        'function': sentiment.run_sentiment
    },
    'volatility_forecast': {
        'title': 'Volatility Forecasting (GARCH)',
        'description': '(Placeholder Implementation) A model used to predict future volatility, which is crucial for risk management, options pricing, and volatility-targeting strategies.',
        'math': 'This is a simple proxy using 20-day rolling historical volatility. A full GARCH(1,1) model would be a more robust autoregressive model that forecasts variance based on past squared returns and past variances.',
        'tickers_required': 1,
        'function': volatility_forecast.run_volatility_forecast
    },
    'mean_variance_opt': {
        'title': 'Mean-Variance Optimization (Markowitz)',
        'description': '(Conceptual Placeholder) A portfolio allocation strategy that finds the optimal portfolio weights to maximize expected return for a given level of risk (variance).',
        'math': 'This is a placeholder. This strategy applies to a *portfolio* of assets, not a single ticker. A full implementation would require multiple tickers, calculate their expected returns and covariance matrix, and solve for the "Efficient Frontier".',
        'tickers_required': 1,
        'function': mean_variance_opt.run_mean_variance_opt
    }
}


# ==========================================
# ==          Frontend Routes           ==
# ==========================================

@app.route('/')
def home():
    """
    Renders the homepage with a chart for a random stock.
    Assigns random strategies to data peaks for interactive linking.
    """
    try:
        # 1. Pick a random stock
        ticker = random.choice(DEFAULT_STOCKS)
        data = fetch_stock_data(ticker, period="1y")
        
        if data.empty:
            raise Exception("No data found for default ticker.")

        # 2. Format data for Chart.js
        chart_data = {
            'labels': data.index.strftime('%Y-%m-%d').tolist(),
            'prices': data['Close'].tolist()
        }
        
        # 3. Find peaks and assign random strategies
        prices = data['Close'].tolist()
        peak_indices = simple_find_peaks(prices, prominence=5) # Find modest peaks
        
        peaks_with_strategies = []
        strategy_keys = list(STRATEGY_METADATA.keys())
        
        for idx in peak_indices:
            peaks_with_strategies.append({
                'index': idx,
                'date': data.index[idx].strftime('%Y-%m-%d'),
                'price': prices[idx],
                'strategy': random.choice(strategy_keys) # Assign random strategy
            })

        return render_template('home.html', 
                               ticker=ticker,
                               stock_name=data.info.get('longName', ticker),
                               chart_data_json=json.dumps(chart_data),
                               peaks_json=json.dumps(peaks_with_strategies))
    
    except Exception as e:
        app.logger.error(f"Error loading homepage: {e}")
        return render_template('home.html', 
                               ticker="ERROR",
                               stock_name="Could not load data",
                               chart_data_json=json.dumps({'labels': [], 'prices': []}),
                               peaks_json=json.dumps([]))


@app.route('/algorithm/<strategy_name>')
def algorithm_page(strategy_name):
    """
    Renders the generic algorithm page, passing in the specific
    metadata (title, description, etc.) for the requested strategy.
    """
    if strategy_name not in STRATEGY_METADATA:
        abort(404)
        
    strategy_details = STRATEGY_METADATA[strategy_name]
    
    return render_template('algorithm.html', 
                           strategy_name=strategy_name,
                           strategy=strategy_details)


@app.route('/council')
def council_page():
    """Renders the Quant Council page."""
    return render_template('council.html')


# ==========================================
# ==            API Endpoints           ==
# ==========================================

@app.route('/api/run_algorithm/<strategy_name>', methods=['POST'])
def api_run_algorithm(strategy_name):
    """
    API endpoint to run a specific algorithm.
    Takes ticker(s) as JSON and returns algorithm results.
    """
    if strategy_name not in STRATEGY_METADATA:
        return jsonify({"error": "Strategy not found"}), 404
        
    data = request.get_json()
    ticker1 = data.get('ticker1')
    ticker2 = data.get('ticker2')
    
    if not ticker1:
        return jsonify({"error": "Ticker 1 is required"}), 400
        
    strategy_info = STRATEGY_METADATA[strategy_name]
    
    try:
        # Call the correct function based on the strategy
        if strategy_info['tickers_required'] == 2:
            if not ticker2:
                return jsonify({"error": "Ticker 2 is required for this strategy"}), 400
            result = strategy_info['function'](ticker1, ticker2)
        else:
            result = strategy_info['function'](ticker1)
            
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error running algorithm {strategy_name}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/run_council/<ticker>', methods=['GET'])
def api_run_council(ticker):
    """
    API endpoint to run the entire Quant Council on a single ticker.
    """
    if not ticker:
        return jsonify({"error": "A ticker is required"}), 400
        
    try:
        council_result = run_council_decision(ticker)
        return jsonify(council_result)
        
    except Exception as e:
        app.logger.error(f"Error running council: {e}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# ==         Error Handlers             ==
# ==========================================

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template('base.html', title="404 - Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 page."""
    return render_template('base.html', title="500 - Internal Error"), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000
