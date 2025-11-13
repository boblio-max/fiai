import traceback
from algorithms import stat_arb, momentum, mean_reversion, ml_predictive, \
    reinforcement, factor_investing, market_making, sentiment, \
    volatility_forecast, mean_variance_opt

# Define the functions to run.
# Note: stat_arb and mean_variance are portfolio/pair-based.
# We will run them with a common pair (e.g., SPY) for a baseline.
# This is a simplification to make them fit the single-ticker model.
STRATEGIES_TO_RUN = {
    'momentum': momentum.run_momentum,
    'mean_reversion': mean_reversion.run_mean_reversion,
    'ml_predictive': ml_predictive.run_ml_predictive,
    'volatility_forecast': volatility_forecast.run_volatility_forecast,
    'stat_arb': stat_arb.run_stat_arb,
    'reinforcement': reinforcement.run_reinforcement,
    'factor_investing': factor_investing.run_factor_investing,
    'market_making': market_making.run_market_making,
    'sentiment': sentiment.run_sentiment,
    'mean_variance_opt': mean_variance_opt.run_mean_variance_opt
}

def run_council_decision(ticker):
    """
    Runs all 10 algorithms for a given ticker and aggregates their votes.
    Generates a final decision and an AI prompt.
    """
    votes = {'Buy': [], 'Sell': [], 'Hold': []}
    recommendations = {}
    ai_prompt_data = []

    for name, func in STRATEGIES_TO_RUN.items():
        try:
            # Handle pair-based strategies with a default pair (SPY)
            if name == 'stat_arb':
                # Avoid running on itself
                pair_ticker = 'SPY' if ticker.upper() != 'SPY' else 'QQQ'
                result = func(ticker, pair_ticker)
            # Handle other single-ticker strategies
            else:
                result = func(ticker)

            rec = result.get('recommendation', 'Hold')
            summary = result.get('summary', 'No summary available.')
            
            recommendations[name] = rec
            votes[rec].append(name)
            
            ai_prompt_data.append(f"--- Algorithm: {name.title()} ---\n"
                                  f"Vote: {rec}\n"
                                  f"Rationale: {summary}\n")

        except Exception as e:
            print(f"Error running {name}: {e}")
            tb = traceback.format_exc()
            recommendations[name] = 'Error'
            ai_prompt_data.append(f"--- Algorithm: {name.title()} ---\n"
                                  f"Vote: Error\n"
                                  f"Rationale: {str(e)}\n{tb}\n")

    # --- Tally Votes ---
    buy_count = len(votes['Buy'])
    sell_count = len(votes['Sell'])
    hold_count = len(votes['Hold'])

    # Determine final council vote
    if buy_count > sell_count and buy_count > hold_count:
        council_vote = 'Buy'
    elif sell_count > buy_count and sell_count > hold_count:
        council_vote = 'Sell'
    else:
        council_vote = 'Hold'

    # --- Generate AI Prompt ---
    full_ai_prompt = (
        f"**Quantum Quant Council Briefing**\n\n"
        f"**Objective:** Generate a comprehensive, long-form investment thesis for {ticker}.\n\n"
        f"**Ticker:** {ticker}\n"
        f"**Council's Collective Vote:** {council_vote}\n\n"
        f"**Vote Breakdown:**\n"
        f"* **Buy ({buy_count}):** {', '.join(votes['Buy'])}\n"
        f"* **Sell ({sell_count}):** {', '.join(votes['Sell'])}\n"
        f"* **Hold ({hold_count}):** {', '.join(votes['Hold'])}\n\n"
        f"**Individual Algorithm Analysis:**\n\n"
        f"{'\n'.join(ai_prompt_data)}\n"
        f"**Task:**\n"
        f"Synthesize all the above data. Act as a senior portfolio manager. "
        f"Write a detailed, nuanced investment decision. Consider the consensus "
        f"and, more importantly, the *disagreement* between models (e.g., 'Momentum "
        f"models are buying, but mean-reversion models are selling, suggesting...'). "
        f"Provide a final recommendation with clear justifications."
    )

    return {
        'council_vote': council_vote,
        'votes': votes,
        'recommendations': recommendations,
        'ai_prompt': full_ai_prompt
    }
