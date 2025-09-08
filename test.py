#get the last 3 days of ticker information for aapl stock from yfinance
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=3)   
df = yf.download("AAPL", period="3d", interval="1d")
df.reset_index(inplace=True)
df['ticker'] = 'AAPL'
df['date'] = df['Date'].dt.strftime('%Y%m%dT%H%M%S')
df = df.drop(columns=['Date'])
df = df.replace({np.nan: None})
data = df.to_dict(orient='records')
print(data)