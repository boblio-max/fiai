import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from core.utils import fetch_stock_data

def run_sentiment(ticker):
    """
    (Full Implementation)
    Runs VADER sentiment analysis on the company's 'longBusinessSummary'.
    """
    try:
        # We need the full Ticker object to get .info
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Use the long business summary as the text to analyze
        text_to_analyze = info.get('longBusinessSummary')
        
        if not text_to_analyze:
            # Fallback if no summary exists
            fetch_stock_data(ticker, period="1y") # Still fetch data for Council
            return {
                'recommendation': 'Hold',
                'summary': 'No business summary available for sentiment analysis. Defaulting to Hold.',
                'chart_data': None,
                'is_placeholder': True
            }

        # --- VADER Sentiment Analysis ---
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(text_to_analyze)
        
        # The 'compound' score is a normalized, aggregated score from -1 (v. neg) to +1 (v. pos)
        compound_score = sentiment_scores['compound']
        
        # --- Generate Signal ---
        if compound_score > 0.1:
            rec = 'Buy'
            summary = f"Positive sentiment detected (Score: {compound_score:.3f}). The company's business summary has a bullish tone."
        elif compound_score < -0.1:
            rec = 'Sell'
            summary = f"Negative sentiment detected (Score: {compound_score:.3f}). The company's business summary has a bearish tone."
        else:
            rec = 'Hold'
            summary = f"Neutral sentiment detected (Score: {compound_score:.3f}). The company's business summary is objective or balanced."
            
        # --- Format Chart Data (Bar chart of scores) ---
        chart_data = {
            'labels': ['Positive', 'Neutral', 'Negative'],
            'importance': [sentiment_scores['pos'], sentiment_scores['neu'], sentiment_scores['neg']]
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data,
            'chart_type': 'bar' # Tell the frontend to use a bar chart
        }
        
    except Exception as e:
        return {"error": str(e)}
