import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from core.utils import fetch_stock_data

def run_ml_predictive(ticker):
    """
    (Placeholder Implementation)
    Uses a Random Forest to predict next-day price direction.
    """
    try:
        data = fetch_stock_data(ticker, period="3y")
        
        df = pd.DataFrame(data['Close'])
        
        # --- Feature Engineering ---
        df['Return'] = df['Close'].pct_change()
        df['Lag_1'] = df['Return'].shift(1)
        df['Lag_5'] = df['Return'].shift(5)
        df['Rolling_Mean_10'] = df['Close'].rolling(window=10).mean().shift(1)
        
        # Target variable: 1 if next day's price is up, 0 if down
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        df.dropna(inplace=True)
        
        if df.empty:
            return {"error": "Not enough data for ML model."}

        # --- Model Training ---
        X = df[['Lag_1', 'Lag_5', 'Rolling_Mean_10']]
        y = df['Target']
        
        # Split data (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        if X_train.empty or y_train.empty:
             return {"error": "Not enough data for ML model training split."}

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # --- Prediction ---
        # Predict on the last available data point
        latest_features = df[['Lag_1', 'Lag_5', 'Rolling_Mean_10']].iloc[[-1]]
        prediction = model.predict(latest_features)[0]
        
        if prediction == 1:
            rec = 'Buy'
            summary = "Random Forest model predicts an UPWARD movement for the next trading day."
        else:
            rec = 'Sell'
            summary = "Random Forest model predicts a DOWNWARD movement for the next trading day."
            
        # Calculate accuracy for context (on test set)
        y_pred_test = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred_test)
        summary += f" Model accuracy on test data: {acc:.2%}. (Note: This is a simplified placeholder)."
        
        # --- Format Chart Data (Feature Importance) ---
        chart_data = {
            'labels': X.columns.tolist(),
            'importance': model.feature_importances_.tolist()
        }
        
        return {
            'recommendation': rec,
            'summary': summary,
            'chart_data': chart_data,
            'chart_type': 'bar' # Tell the frontend to use a bar chart
        }
        
    except Exception as e:
        return {"error": str(e)}
