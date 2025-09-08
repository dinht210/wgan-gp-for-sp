import pandas as pd
from preprocessing import cyclical_encoding, one_hot_encoding, build_windows_per_ticker
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
import torch
from models import Generator, Discriminator
from training import Trainer
import joblib

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

split_idx = int(df.shape[0] * 0.8)
train_df, test_df = df[:split_idx], df[split_idx:]

train_ticker_encoded, test_ticker_encoded = one_hot_encoding(train_df, test_df)

feature_cols = [c for c in df.columns if c not in ["date", "y", "Close", "ticker"]]
x_train = train_df[feature_cols].values
x_test = test_df[feature_cols].values

x_train = np.concatenate([x_train, train_ticker_encoded], axis=1)
x_test = np.concatenate([x_test, test_ticker_encoded], axis=1)

y_train = train_df[["y"]].values
y_test = test_df[["y"]].values

print(f"x_train shape: {x_train.shape}, y_train shape: {y_train.shape}")
print(f"x_test shape: {x_test.shape}, y_train shape: {y_test.shape}")

x_scaler = MinMaxScaler(feature_range=(0, 1))
y_scaler = MinMaxScaler(feature_range=(0, 1))

x_train = x_scaler.fit_transform(x_train)
x_test = x_scaler.transform(x_test)

y_train = y_scaler.fit_transform(y_train)
y_test = y_scaler.transform(y_test)

print(f"After scaling: x_train shape: {x_train.shape}, y_train shape: {y_train.shape}")
# print(f"x_train columns: {feature_cols + list(range(train_ticker_encoded.shape[1]))}")

lookback = 3
x_train_slide, y_train_scalar, y_train_slide = build_windows_per_ticker(x_train, y_train, lookback, train_df['ticker'].values)
x_test_slide, y_test_scalar, y_test_slide = build_windows_per_ticker(x_test, y_test, lookback, test_df['ticker'].values)

print(f"After sliding window: x_train shape: {x_train_slide.shape}, y_train shape: {y_train_scalar.shape}, y_train_gan shape: {y_train_slide.shape}")
print(f"After sliding window: x_test shape: {x_test_slide.shape}, y_test shape: {y_test_scalar.shape}, y_test_gan shape: {y_test_slide.shape}")

batch_size = 128
train_loader = DataLoader(
    TensorDataset(x_train_slide, y_train_slide),
    batch_size=batch_size,
    shuffle=False
)
test_loader = DataLoader(
    TensorDataset(x_test_slide, y_test_slide),
    batch_size=batch_size,
    shuffle=False
)

for x_batch, y_batch in train_loader:
    print(f'Batch x train: {x_batch.shape}, Batch y train: {y_batch.shape}')
    break

for x_batch, y_batch in test_loader:
    print(f'Batch x test: {x_batch.shape}, Batch y test: {y_batch.shape}')
    break

learning_rate = 1e-4
num_epochs = 100
critic_iterations = 5
n_features = x_train.shape[1]
output_dim = y_train.shape[1]
print(f"Number of features: {n_features}, Output dimension: {output_dim}")
betas = [0.5, 0.9]
lambda_weight = 10
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

generator = Generator(n_features).to(device)
discriminator = Discriminator().to(device)

optim_g = torch.optim.Adam(generator.parameters(), lr=learning_rate, betas=betas)
optim_d = torch.optim.Adam(discriminator.parameters(), lr=learning_rate, betas=betas)

trainer = Trainer(generator, discriminator, optim_g, optim_d, lambda_weight=lambda_weight, critic_iterations=critic_iterations, device=device)

trainer.train(train_loader, epochs=num_epochs, lookback=lookback, output_dim=output_dim, device=device)

torch.save(generator.state_dict(), "models/financial_1y_generator.pth")
torch.save(discriminator.state_dict(), "models/financial_1y_discriminator.pth")
joblib.dump(x_scaler, "models/scalers/tech_1y_x_scaler.pkl")
joblib.dump(y_scaler, "models/scalers/tech_1y_y_scaler.pkl")
joblib.dump(one_hot_encoder, "models/encoders/tech_1y_one_hot_encoder.pkl")