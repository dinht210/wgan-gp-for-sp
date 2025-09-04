import numpy as np
import pandas as pd
import re
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime, timedelta, timezone
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, AroonIndicator, ADXIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
import yfinance as yf
from pprint import pp
import traceback


"""
TODO: session, retry, error handling, logging, etc.
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

"""
SeekingAlpha scrape
"""
def fetch_titles_sa(ticker: str) -> list[str]:
    url = f"https://seekingalpha.com/symbol/{ticker}/news"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()              
    soup = BeautifulSoup(resp.text, "html5lib")
    content = soup.prettify()
    
    all_titles = re.findall(r'"title"\s*:\s*"([^"]*)"', content)
    blank_indices = [i for i, t in enumerate(all_titles) if t.strip() == ""]

    if len(blank_indices) >= 5:
        fifth_blank_idx = blank_indices[4]
        article_titles = all_titles[fifth_blank_idx + 1 :]
    else:
        article_titles = []
    
    return article_titles
    
"""
YF API
"""
# fetch historical price data from yfinance API and compute technical indicators
def get_historical(tickers, time_period, interval, sentiment, filename):
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(DATA_DIR, exist_ok=True)

    df = pd.DataFrame()

    for ticker in tickers:
        try:
            # fetch
            ticker_raw = yf.Ticker(ticker).history(period=f"{time_period}", interval=f"{interval}")
            if ticker_raw.empty:
                return "No data for ticker"

            # compute technicals
            ticker_df = ticker_raw.copy()
            ticker_df = ticker_df.tz_localize(None)
            ticker_df = ticker_df.reset_index() 
            ticker_df = ticker_df.rename(columns={"Date": "date"})
            ticker_df["date"] = pd.to_datetime(ticker_df["date"])

            # rsi 
            ticker_df['RSI_7'] = RSIIndicator(close=ticker_df['Close'], window=7).rsi()
            ticker_df['RSI_14'] = RSIIndicator(close=ticker_df['Close'], window=14).rsi()
            ticker_df['RSI_21'] = RSIIndicator(close=ticker_df['Close'], window=21).rsi()

            # macd
            macd_ind = MACD(close=ticker_df['Close'], window_slow=26, window_fast=12, window_sign=9)
            ticker_df['MACD'] = macd_ind.macd()
            ticker_df['MACD_Signal'] = macd_ind.macd_signal()

            # bollinger bands
            bb_ind_7 = BollingerBands(close=ticker_df['Close'], window=7, window_dev=2)
            ticker_df['BB_High_7'] = bb_ind_7.bollinger_hband()
            ticker_df['BB_Low_7'] = bb_ind_7.bollinger_lband()
            ticker_df['BB_Width_7'] = ticker_df['BB_High_7'] - ticker_df['BB_Low_7']

            bb_ind_14 = BollingerBands(close=ticker_df['Close'], window=14, window_dev=2)
            ticker_df['BB_High_14'] = bb_ind_14.bollinger_hband()
            ticker_df['BB_Low_14'] = bb_ind_14.bollinger_lband()
            ticker_df['BB_Width_14'] = ticker_df['BB_High_14'] - ticker_df['BB_Low_14']

            bb_ind_21 = BollingerBands(close=ticker_df['Close'], window=21, window_dev=2)
            ticker_df['BB_High_21'] = bb_ind_21.bollinger_hband()
            ticker_df['BB_Low_21'] = bb_ind_21.bollinger_lband()
            ticker_df['BB_Width_21'] = ticker_df['BB_High_21'] - ticker_df['BB_Low_21']

            # aroon
            aroon_ind_7 = AroonIndicator(high=ticker_df["High"], low=ticker_df["Low"], window=7)
            ticker_df["Aroon_7"] = aroon_ind_7.aroon_indicator()
            ticker_df["Aroon_Up_7"] = aroon_ind_7.aroon_up()
            ticker_df["Aroon_Down_7"] = aroon_ind_7.aroon_down()

            aroon_ind_14 = AroonIndicator(high=ticker_df["High"], low=ticker_df["Low"], window=14)
            ticker_df["Aroon_14"] = aroon_ind_14.aroon_indicator()
            ticker_df["Aroon_Up_14"] = aroon_ind_14.aroon_up()
            ticker_df["Aroon_Down_14"] = aroon_ind_14.aroon_down()

            aroon_ind_21 = AroonIndicator(high=ticker_df["High"], low=ticker_df["Low"], window=21)
            ticker_df["Aroon_21"] = aroon_ind_21.aroon_indicator()
            ticker_df["Aroon_Up_21"] = aroon_ind_21.aroon_up()
            ticker_df["Aroon_Down_21"] = aroon_ind_21.aroon_down()

            # adx
            adx_ind_7 = ADXIndicator(high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"], window=7)
            ticker_df["ADX_7"] = adx_ind_7.adx()
            ticker_df["ADX_neg_7"] = adx_ind_7.adx_neg()
            ticker_df["ADX_pos_7"] = adx_ind_7.adx_pos()

            adx_ind_14 = ADXIndicator(high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"], window=14)
            ticker_df["ADX_14"] = adx_ind_14.adx()
            ticker_df["ADX_neg_14"] = adx_ind_14.adx_neg()
            ticker_df["ADX_pos_14"] = adx_ind_14.adx_pos()

            adx_ind_21 = ADXIndicator(high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"], window=21)
            ticker_df["ADX_21"] = adx_ind_21.adx()
            ticker_df["ADX_neg_21"] = adx_ind_21.adx_neg()
            ticker_df["ADX_pos_21"] = adx_ind_21.adx_pos()

            # obv
            obv_ind = OnBalanceVolumeIndicator(close=ticker_df["Close"], volume=ticker_df["Volume"])
            ticker_df["OBV"] = obv_ind.on_balance_volume()

            # stochastic oscillator
            stoch_osc_7 = StochasticOscillator(high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"], window=7)
            ticker_df["Stoch_7"] = stoch_osc_7.stoch()
            ticker_df["Stoch_Signal_7"] = stoch_osc_7.stoch_signal()

            stoch_osc_14 = StochasticOscillator(high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"], window=14)
            ticker_df["Stoch_14"] = stoch_osc_14.stoch()
            ticker_df["Stoch_Signal_14"] = stoch_osc_14.stoch_signal()

            stoch_osc_21 = StochasticOscillator(high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"], window=21)
            ticker_df["Stoch_21"] = stoch_osc_21.stoch()
            ticker_df["Stoch_Signal_21"] = stoch_osc_21.stoch_signal()

            ticker_df.rename(columns={'index':'Date'}, inplace=True)
            ticker_df['ticker'] = ticker

            # collects sentiment data if requested
            if sentiment:
                news = fetch_news_data_av(ticker, time_period)
                # print(news)
                news_rows = []
                for item in news.get("feed", []):
                    score = next(
                        (
                            ts.get("ticker_sentiment_score")
                            for ts in item.get("ticker_sentiment", [])
                            if ts.get("ticker") == ticker
                        ),
                        None,
                    )
                    news_rows.append(
                        {
                            "sentiment": score,
                            "date": item.get("time_published"),
                        }
                    )

                # data cleaning news data
                news_df = pd.DataFrame(news_rows)
                news_df["sentiment"] = pd.to_numeric(news_df["sentiment"], errors="coerce")
                news_df["date"] = pd.to_datetime(news_df["date"], format="%Y%m%dT%H%M%S", errors="coerce")
                news_df = news_df.dropna(subset=["sentiment", "date"])

                # averaging sentiment per day
                daily_sent = (
                    news_df
                    .set_index("date")
                    .resample("D")["sentiment"]
                    .mean()
                    .reset_index()
                    .rename(columns={"sentiment": "avg_sentiment"})
                )

                # merging sentiment with price+technicals
                ticker_df["date"] = pd.to_datetime(ticker_df["date"])
                #merged_df = pd.merge(ticker_df, daily_sent, on="date", how="left")
            
            ticker_df = ticker_df.dropna(how="any")
            print(f"\nFeature Data for {ticker}:")
            print(ticker_df.head())

            df = pd.concat([df, ticker_df])

            csv_filename = f"{filename}.csv"
            csv_path = os.path.join(DATA_DIR, csv_filename)
            df.to_csv(csv_path, index=False)
            print(f"CSV exported to {csv_path}\n")
        except Exception as e:
            traceback.print_exc()
            return None


"""
AV API
"""
# fetch news sentiment data from alpha vantage
def fetch_news_data_av(ticker: str, time_period: str) -> dict:
    api_key = os.getenv("AV_API_KEY")
    
    # convert time period 
    if time_period.endswith('d'):
        days = int(time_period[:-1])
    elif time_period.endswith('y'):
        years = int(time_period[:-1])
        days = years * 365 
    else:
        raise ValueError("time_period must end with 'd' for days or 'y' for years")
    
    time_from_dt = datetime.now(timezone.utc) - timedelta(days=days)
    time_from = time_from_dt.strftime("%Y%m%dT%H%M")
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={api_key}&time_from={time_from}&limit=10000"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data

# fetch options data from alpha vantage
def fetch_options_data_av(ticker: str, date: str) -> dict:
    api_key = os.getenv("AV_API_KEY")
    url = f"https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol={ticker}&apikey={api_key}&date={date}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data

# fetch daily price data from alpha vantage (not used currently)
def fetch_daily_data_av(ticker: str) -> dict:
    api_key = os.getenv("AV_API_KEY")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data

# Test the updated function with different time periods
# print("Testing with 1 year of data:")
# data = create_df_av("NVDA", "1y")
# print(f"Data shape: {data.shape if data is not None else 'None'}")

# print("\nTesting with 5 days of data:")
# data_5d = create_df_av("NVDA", "5d")
# print(f"Data shape: {data_5d.shape if data_5d is not None else 'None'}")

# print("\nTesting with 2 years of data:")
# data_2y = create_df_av("NVDA", "2y")
# print(f"Data shape: {data_2y.shape if data_2y is not None else 'None'}")

tickers = ["CAT", "BA", "GE", "UPS", "DE"]
time_period = "3mo" 
interval = "1d" # valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 4h, 1d, 5d, 1wk, 1mo, 3mo]")
filename = "industrial_stocks_3mo"
get_historical(tickers, time_period, interval, False, filename)


