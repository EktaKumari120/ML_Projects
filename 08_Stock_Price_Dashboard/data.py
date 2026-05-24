import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, period):
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(period=period)
    df.reset_index(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    if df["Date"].dt.tz is not None:
        df["Date"] = df["Date"].dt.tz_localize(None)
    return df

# df = fetch_stock_data("TSLA",'1d')
# print(df.head())