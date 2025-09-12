from flask import Flask, request, jsonify
import torch
from models import Generator
import joblib
import pandas as pd
from preprocessing import cyclical_encoding
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, AroonIndicator, ADXIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
import os


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_DIR = os.environ.get("MODEL_DIR", "/opt/ml/model")
MODEL_PATH = os.path.join(MODEL_DIR, "financial_1y_generator.pth")
XS_PATH  = os.path.join(MODEL_DIR, "financial_1y_x_scaler.pkl")
YS_PATH  = os.path.join(MODEL_DIR, "financial_1y_y_scaler.pkl")
ENC_PATH = os.path.join(MODEL_DIR, "financial_1y_one_hot_encoder.pkl")

app = Flask(__name__)

generator = None
x_scaler = None
y_scaler = None
one_hot_encoder = None

def load_artifacts():
    global generator, x_scaler, y_scaler, one_hot_encoder
    if generator is not None:
        return
    generator = Generator(input_size=59)  # adjust for diff models
    generator.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    generator.eval()
    
    x_scaler = joblib.load(XS_PATH)
    y_scaler = joblib.load(YS_PATH)
    one_hot_encoder = joblib.load(ENC_PATH)

@app.route("/ping", methods=["GET"])
def ping():
    return "OK", 200

@app.route('/invocations', methods=["POST"])
def invoke():
    data = request.get_json()

    load_artifacts()
    
    df = pd.DataFrame(data)

    df['date'] = pd.to_datetime(df['Date'])

    year = df['date'].dt.year - 1
    month = df['date'].dt.month - 1
    day = df['date'].dt.day - 1

    period = 10
    df["year_cos"], df["year_sin"] = cyclical_encoding(year, period)
    df["month_cos"], df["month_sin"] = cyclical_encoding(month, 12)
    df["day_cos"], df["day_sin"] = cyclical_encoding(day, 31)

    df["y"] = df["Close"]

    # rsi 
    df['RSI_7'] = RSIIndicator(close=df['Close'], window=7).rsi()
    df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
    df['RSI_21'] = RSIIndicator(close=df['Close'], window=21).rsi()

    # macd
    macd_ind = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd_ind.macd()
    df['MACD_Signal'] = macd_ind.macd_signal()

    # bollinger bands
    bb_ind_7 = BollingerBands(close=df['Close'], window=7, window_dev=2)
    df['BB_High_7'] = bb_ind_7.bollinger_hband()
    df['BB_Low_7'] = bb_ind_7.bollinger_lband()
    df['BB_Width_7'] = df['BB_High_7'] - df['BB_Low_7']

    bb_ind_14 = BollingerBands(close=df['Close'], window=14, window_dev=2)
    df['BB_High_14'] = bb_ind_14.bollinger_hband()
    df['BB_Low_14'] = bb_ind_14.bollinger_lband()
    df['BB_Width_14'] = df['BB_High_14'] - df['BB_Low_14']

    bb_ind_21 = BollingerBands(close=df['Close'], window=21, window_dev=2)
    df['BB_High_21'] = bb_ind_21.bollinger_hband()
    df['BB_Low_21'] = bb_ind_21.bollinger_lband()
    df['BB_Width_21'] = df['BB_High_21'] - df['BB_Low_21']

    # aroon
    aroon_ind_7 = AroonIndicator(high=df["High"], low=df["Low"], window=7)
    df["Aroon_7"] = aroon_ind_7.aroon_indicator()
    df["Aroon_Up_7"] = aroon_ind_7.aroon_up()
    df["Aroon_Down_7"] = aroon_ind_7.aroon_down()

    aroon_ind_14 = AroonIndicator(high=df["High"], low=df["Low"], window=14)
    df["Aroon_14"] = aroon_ind_14.aroon_indicator()
    df["Aroon_Up_14"] = aroon_ind_14.aroon_up()
    df["Aroon_Down_14"] = aroon_ind_14.aroon_down()

    aroon_ind_21 = AroonIndicator(high=df["High"], low=df["Low"], window=21)
    df["Aroon_21"] = aroon_ind_21.aroon_indicator()
    df["Aroon_Up_21"] = aroon_ind_21.aroon_up()
    df["Aroon_Down_21"] = aroon_ind_21.aroon_down()

    # adx
    adx_ind_7 = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=7)
    df["ADX_7"] = adx_ind_7.adx()
    df["ADX_neg_7"] = adx_ind_7.adx_neg()
    df["ADX_pos_7"] = adx_ind_7.adx_pos()

    adx_ind_14 = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["ADX_14"] = adx_ind_14.adx()
    df["ADX_neg_14"] = adx_ind_14.adx_neg()
    df["ADX_pos_14"] = adx_ind_14.adx_pos()

    adx_ind_21 = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=21)
    df["ADX_21"] = adx_ind_21.adx()
    df["ADX_neg_21"] = adx_ind_21.adx_neg()
    df["ADX_pos_21"] = adx_ind_21.adx_pos()

    # obv
    obv_ind = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"])
    df["OBV"] = obv_ind.on_balance_volume()

    # stochastic oscillator
    stoch_osc_7 = StochasticOscillator(high=df["High"], low=df["Low"], close=df["Close"], window=7)
    df["Stoch_7"] = stoch_osc_7.stoch()
    df["Stoch_Signal_7"] = stoch_osc_7.stoch_signal()

    stoch_osc_14 = StochasticOscillator(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["Stoch_14"] = stoch_osc_14.stoch()
    df["Stoch_Signal_14"] = stoch_osc_14.stoch_signal()

    stoch_osc_21 = StochasticOscillator(high=df["High"], low=df["Low"], close=df["Close"], window=21)
    df["Stoch_21"] = stoch_osc_21.stoch()
    df["Stoch_Signal_21"] = stoch_osc_21.stoch_signal()

    ticker_encoded = one_hot_encoder.transform(df[["ticker"]])
    df = df.drop(columns=["ticker"])
    df = pd.concat([df, pd.DataFrame(ticker_encoded, index=df.index)], axis=1)

    drop_cols = [c for c in ['Date','date','y','ticker', 'Close'] if c in df.columns]
    df = df.drop(columns=drop_cols)

    x_cols = [ 
        'Open','High','Low','Volume','Dividends','Stock Splits',
        'RSI_7','RSI_14','RSI_21','MACD','MACD_Signal',
        'BB_High_7','BB_Low_7','BB_Width_7',
        'BB_High_14','BB_Low_14','BB_Width_14',
        'BB_High_21','BB_Low_21','BB_Width_21',
        'Aroon_7','Aroon_Up_7','Aroon_Down_7',
        'Aroon_14','Aroon_Up_14','Aroon_Down_14',
        'Aroon_21','Aroon_Up_21','Aroon_Down_21',
        'ADX_7','ADX_neg_7','ADX_pos_7',
        'ADX_14','ADX_neg_14','ADX_pos_14',
        'ADX_21','ADX_neg_21','ADX_pos_21',
        'OBV','Stoch_7','Stoch_Signal_7',
        'Stoch_14','Stoch_Signal_14',
        'Stoch_21','Stoch_Signal_21',
        'year_cos','year_sin','month_cos','month_sin','day_cos','day_sin',
        0,1,2,3,4,5,6,7  
    ] # should fit scalers on dataframes so feature_names_in_ works, this is a bandage solution

    df_colmap = {str(c): c for c in df.columns}
    ordered_cols = [df_colmap[str(c)] for c in x_cols]
    X = df[ordered_cols]

    print(X.head())
    print(f"X columns: {X.columns}")

    lookback = 3
    window = X.tail(lookback).values

    print(window)
    input_scaled = x_scaler.transform(window)
    
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32).unsqueeze(0)
    
    with torch.no_grad():
        output = generator(input_tensor).squeeze(0).numpy()
    
    output_rescaled = y_scaler.inverse_transform(output.reshape(1, -1)).flatten()
    
    return jsonify(output_rescaled.tolist())