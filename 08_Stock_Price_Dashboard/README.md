# Stock Price Dashboard

## Business Problem
Investors need a way to visualize historical stock price patterns and 
get a data-driven estimate of near-term closing prices, rather than 
relying on gut feeling.

## Approach
- Pulled historical stock data using yfinance
- Engineered features from price history (e.g., moving averages, lagged prices)
- Trained regression models (Scikit-learn and XGBoost) to predict closing price
- Built an interactive Streamlit dashboard with Plotly charts to visualize price trends and predictions

## Tools & Libraries
Python, Streamlit, Plotly, Pandas, NumPy, Scikit-learn, XGBoost, yfinance

## Key Insight
XGBoost captured non-linear patterns in price movement better than 
simpler regression models, though stock prediction remains inherently 
uncertain — the dashboard is best used for trend visualization alongside predictions, not as financial advice.

## Files
- Streamlit app script