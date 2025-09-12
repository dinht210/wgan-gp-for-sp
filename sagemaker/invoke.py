import yfinance as yf
import pandas as pd
import boto3
import json

# creates input data
def build_payload(ticker="JPM", days=100):
    df = yf.download(
        ticker,
        period=f"{days}d",
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column", 
    )

    if isinstance(df.columns, pd.MultiIndex):
        if ticker in df.columns.get_level_values(1):
            df = df.xs(ticker, axis=1, level=1)
        else:
            df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    df = df.assign(
        Date = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d"),
        Dividends = 0.0,
        **{"Stock Splits": 0.0},
        ticker = ticker,
    )

    cols = [
        "Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits", "ticker", "Date"
    ]

    df = df[cols]
    df["Open"]   = df["Open"].astype(float)
    df["High"]   = df["High"].astype(float)
    df["Low"]    = df["Low"].astype(float)
    df["Close"]  = df["Close"].astype(float)
    df["Volume"] = df["Volume"].astype(int)

    return df.to_dict(orient="records")

payload = build_payload("GS", days=100)

endpoint_name = "financial-1y-wgan-gp-endpoint-2"   
region = "us-east-1"

runtime = boto3.client("sagemaker-runtime", region_name=region)

resp = runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="application/json",
    Accept="application/json",
    Body=json.dumps(payload).encode("utf-8"),
)

result = json.loads(resp["Body"].read().decode("utf-8"))
print(result) 