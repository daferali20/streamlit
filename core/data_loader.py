import yfinance as yf
import pandas_ta as ta
import pandas as pd

def get_stock_data(ticker="AAPL", period="3mo", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval)
    df.dropna(inplace=True)

    df["RSI"] = ta.rsi(df["Close"], length=14)
    df["SMA_20"] = ta.sma(df["Close"], length=20)
    df["SMA_50"] = ta.sma(df["Close"], length=50)
    df["MACD"] = ta.macd(df["Close"])["MACD_12_26_9"]

    df.dropna(inplace=True)
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    return df
