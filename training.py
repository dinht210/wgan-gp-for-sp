import torch
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import pandas as pd
import torch.nn as nn
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import math
from torch.utils.data import DataLoader, TensorDataset


CSV_PATH   = "data/historical/NVDA_10y_False_2.csv"
df = pd.read_csv(CSV_PATH)
df = df.dropna()

df["date"] = pd.to_datetime(df["date"])

month = df["date"].dt.month - 1
day = df["date"].dt.day - 1
hour = df["date"].dt.hour
minute = df["date"].dt.minute

df["month_cos"], df["month_sin"] = np.cos(2*np.pi*month/12), np.sin(2*np.pi*month/12)
df["day_cos"], df["day_sin"] = np.cos(2*np.pi*day/31), np.sin(2*np.pi*day/31)
df["hour_cos"], df["hour_sin"] = np.cos(2*np.pi*hour/24), np.sin(2*np.pi*hour/24)
df["minute_cos"], df["minute_sin"] = np.cos(2*np.pi*minute/60), np.sin(2*np.pi*minute/60)

df["y"] = df["Close"]
feature_cols = [c for c in df.columns if c not in ["date", "y"]]
x = df[feature_cols].values
y = df["y"].values

split = int(df.shape[0]* 0.8)
train_x, test_x = x[: split, :], x[split - 20:, :]
train_y, test_y = y[: split, ], y[split - 20: , ]

print(f'trainX: {train_x.shape} trainY: {train_y.shape}')
print(f'testX: {test_x.shape} testY: {test_y.shape}')

x_scaler = MinMaxScaler(feature_range = (0, 1))
y_scaler = MinMaxScaler(feature_range = (0, 1))

train_x = x_scaler.fit_transform(train_x)
test_x = x_scaler.transform(test_x)

train_y = y_scaler.fit_transform(train_y.reshape(-1, 1))
test_y = y_scaler.transform(test_y.reshape(-1, 1))

learning_rate = 0.000115
num_epochs = 100
batch_size = 128
LOOKBACK = 3
critic_iterations = 5  # Number of critic (discriminator) updates per generator update

train_x_slide, train_y_scalar, train_y_gan = sliding_window(train_x, train_y, LOOKBACK)
test_x_slide, test_y_slide, test_y_gan = sliding_window(test_x, test_y, LOOKBACK)

train_loader = DataLoader(
    TensorDataset(train_x_slide, train_y_gan),
    batch_size=batch_size,
    shuffle=True
)

#print("Windows:", train_x_slide.shape, "Target-history tensor:", train_y_gan.shape)

n_features = 54
output_dim = 1      

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

modelG = Generator(n_features).to(device)
modelD = Discriminator().to(device)

optimizerG = torch.optim.Adam(modelG.parameters(), lr = learning_rate, betas = (0.0, 0.9), weight_decay = 1e-3)
optimizerD = torch.optim.Adam(modelD.parameters(), lr = learning_rate, betas = (0.0, 0.9), weight_decay = 1e-3)

histG = np.zeros(num_epochs)
histD = np.zeros(num_epochs)
count = 0
for epoch in range(num_epochs):
    loss_G = []
    loss_D = []
    for (x, y) in train_loader:
        x = x.to(device)
        y = y.to(device)

        # Train Discriminator (Critic) multiple times
        for _ in range(critic_iterations):
            fake_data = modelG(x)
            fake_data = torch.cat([y[:, :LOOKBACK, :], fake_data.reshape(-1, 1, output_dim)], axis = 1)
            critic_real = modelD(y)
            critic_fake = modelD(fake_data)
            gp, grad_norm = gradient_penalty(modelD, y, fake_data, device)
            lossD = -(torch.mean(critic_real) - torch.mean(critic_fake)) + 10 * gp
            modelD.zero_grad()
            lossD.backward(retain_graph = True)
            optimizerD.step()
            loss_D.append(lossD.item())

        # Train Generator once
        fake_data = modelG(x)
        fake_data = torch.cat([y[:, :LOOKBACK, :], fake_data.reshape(-1, 1, output_dim)], axis = 1)
        output_fake = modelD(fake_data)
        lossG = -torch.mean(output_fake)
        modelG.zero_grad()
        lossG.backward()
        optimizerG.step()
        loss_G.append(lossG.item()) 

    histG[epoch] = sum(loss_G) 
    histD[epoch] = sum(loss_D)    
    print(f'[{epoch+1}/{num_epochs}] LossD: {sum(loss_D)} LossG:{sum(loss_G)}')

    def gradient_penalty(discriminator, real_data, fake_data, device):
        batch_size = real_data.size(0)
        alpha = torch.rand(batch_size, 1, 1).to(device)
        interpolates = (alpha * real_data + ((1 - alpha) * fake_data)).requires_grad_(True)
        disc_interpolates = discriminator(interpolates)
        gradients = torch.autograd.grad(outputs=disc_interpolates, inputs=interpolates,
                                        grad_outputs=torch.ones(disc_interpolates.size()).to(device),
                                        create_graph=True, retain_graph=True, only_inputs=True)[0]
        gradients = gradients.view(gradients.size(0), -1)
        gradient_norm = gradients.norm(2, dim=1)
        gradient_penalty = ((gradient_norm - 1) ** 2).mean()
        return gradient_penalty, gradient_norm.mean()