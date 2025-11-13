import yfinance as yf
from core.utils import fetch_stock_data

# Define simple thresholds
# These are illustrative. Real models use industry-relative (z-score) values.
VALUE_THRESHOLD = 20  # P/E below 20 is "Value"
QUALITY_THRESHOLD = 0.15 # ROE above 15% is "Quality"

def run_factor_investing(ticker):
    """
    (Full Implementation)
    Scores the stock on 'Value' and 'Quality' factors using yfinance info.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Fetch data to satisfy Council and simulate workload
        fetch_stock_data(ticker, period="1y")

        # --- Factor Scoring ---
        scores = {'Value': 0, 'Quality': 0}
        reasons = []

        # 1. Value Factor (P/E Ratio)
        pe_ratio = info.get('trailingPE')
        if pe_ratio:
            if pe_ratio < VALUE_THRESHOLD:
                scores['Value'] = 1 # Good
                reasons.append(f"Value: Good (P/E is {pe_ratio:.2f} vs. threshold of {VALUE_THRESHOLD})")
            else:
                scores['Value'] = -1 # Bad
                reasons.append(f"Value: Poor (P/E is {pe_ratio:.2f} vs. threshold of {VALUE_THRESHOLD})")
        else:
            reasons.append("Value: N/A (P/E data not available)")

        # 2. Quality Factor (Return on Equity - ROE)
        roe = info.get('returnOnEquity')
        if roe:
            if roe > QUALITY_THRESHOLD:
                scores['Quality'] = 1 # Good
                reasons.append(f"Quality: Good (ROE is {roe:.2%} vs. threshold of {QUALITY_THRESHOLD:.0%})")
            else:
                scores['Quality'] = -1 # Bad
                reasons.append(f"Quality: Poor (ROE is {roe:.2%} vs. threshold of {QUALITY_THRESHOLD:.0%})")
        else:
            reasons.append("Quality: N/A (ROE data not available)")
        
        # --- Generate Signal ---
        total_score = scores['Value'] + scores['Quality']
        
        if total_score > 0:
            rec = 'Buy'
        elif total_score < 0:
            rec = 'Sell'
        else:
            rec = 'Hold'
            
        summary = f"Overall factor score: {total_score}. Recommendation: {rec}.\nRationale: " + "; ".join(reasons)

        # --- Format Chart Data (Bar chart of scores) ---
        chart_data = {
            'labels': list(scores.keys()),
            'importance': list(scores.values()) # Will be 1, -1, 0 etc.
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data,
            'chart_type': 'bar'
        }
        
    except Exception as e:
        return {"error": str(e)}
