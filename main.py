import pandas as pd
from preprocessing import cyclical_encoding
from sklearn.preprocessing import MinMaxScaler


csv_path = 'data/test3.csv'

df = pd.read_csv(csv_path)
df = df.dropna()

df['date'] = pd.to_datetime(df['date'])

year = df['date'].dt.year - 1
month = df['date'].dt.month - 1
day = df['date'].dt.day - 1

period = 10 # however long the data goes back
df["year_cos"], df["year_sin"] = cyclical_encoding(year, period)
df["month_cos"], df["month_sin"] = cyclical_encoding(month, 12)
df["day_cos"], df["day_sin"] = cyclical_encoding(day, 31)

df["y"] = df["Close"]
feature_cols = [c for c in df.columns if c not in ["date", "y", "Close"]]
x = df[feature_cols].values
y = df[["y"]].values

split_idx = int(df.shape[0] * 0.8)
x_train, x_test = x[:split_idx], x[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

print(f"x_train shape: {x_train.shape}, y_train shape: {y_train.shape}")
print(f"x_test shape: {x_test.shape}, y_train shape: {y_test.shape}")

x_scaler = MinMaxScaler(feature_range=(0, 1))
y_scaler = MinMaxScaler(feature_range=(0, 1))

x_train = x_scaler.fit_transform(x_train)
x_test = x_scaler.transform(x_test)

y_train = y_scaler.fit_transform(y_train)
y_test = y_scaler.transform(y_test)
