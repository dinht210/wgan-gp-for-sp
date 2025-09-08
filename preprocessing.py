import numpy as np
import torch
import re
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def sliding_window(x: np.array, y: np.array, window: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    x_ = []
    y_ = []
    y_gan = []

    for i in range(window, x.shape[0]):
        tmp_x = x[i - window: i, :]
        tmp_y = y[i]
        tmp_y_gan = y[i - window: i + 1]
        x_.append(tmp_x)
        y_.append(tmp_y)
        y_gan.append(tmp_y_gan)

    x_ = torch.from_numpy(np.array(x_)).float()
    y_ = torch.from_numpy(np.array(y_)).float()
    y_gan = torch.from_numpy(np.array(y_gan)).float()

    return x_, y_, y_gan

def build_windows_per_ticker(x: np.array, y: np.array, window: int, tickers: np.array) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    x_, y_, y_gan_ = [], [], []

    df_x, df_y = pd.DataFrame(x), pd.DataFrame(y)
    df_ticker = pd.Series(tickers)
    for _, index_mask in df_ticker.groupby(df_ticker).groups.items():
        x_ticker = df_x.iloc[index_mask].values
        y_ticker = df_y.iloc[index_mask].values

        if len(x_ticker) > window:
            x_w, y_w, y_gan_w = sliding_window(x_ticker, y_ticker, window)
            x_.append(x_w)
            y_.append(y_w)
            y_gan_.append(y_gan_w)

    x_ = torch.cat(x_, dim=0)
    y_ = torch.cat(y_, dim=0)
    y_gan_ = torch.cat(y_gan_, dim=0)

    return x_, y_, y_gan_


def remove_unicode(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


def date_encoding(date) -> dict:
    #ts = datetime.strptime(date, "%Y%m%dT%H%M%S")
    # year = ts.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    #second = date.second
    # might add day of the week via one hot encoding

    hours_cos, hours_sin = cyclical_encoding(hour, 24)
    minutes_cos, minutes_sin = cyclical_encoding(minute, 60)
    month_cos, month_sin = cyclical_encoding(month, 12)
    day_cos, day_sin = cyclical_encoding(day, 31)

    date_data = {"month_cos": month_cos, 
                "month_sin": month_sin, 
                "day_cos": day_cos, 
                "day_sin": day_sin, 
                "hours_cos": hours_cos, 
                "hours_sin": hours_sin, 
                "minutes_cos": minutes_cos, 
                "minutes_sin": minutes_sin, 
                }

    # consider adding minmaxscaler to time data

    return date_data


def cyclical_encoding(time, max_days: int) -> list[int]:
    radians = 2 * np.pi * time / max_days
    return np.cos(radians), np.sin(radians)


def one_hot_encoding(train_df, test_df):
    one_hot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    one_hot_encoder.fit(train_df[["ticker"]])
    train_encoded = one_hot_encoder.transform(train_df[["ticker"]])
    test_encoded = one_hot_encoder.transform(test_df[["ticker"]])

    return train_encoded, test_encoded, one_hot_encoder
    # encoding = {}
    # for cat in categories:
    #     if cat == category:
    #         encoding[cat] = 1
    #     else:
    #         encoding[cat] = 0
    # return encoding



