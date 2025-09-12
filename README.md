# wgan-gp-for-sp
using wgan with gradient penalty to predict stock prices from yfinance

models are trained with data up to 9/5/2025

to invoke endpoint:
- modify build_payload() function in sagemaker/invoke.py with ticker/day information (recommended 50+ days for indicator calculation)
- run python3 sagemaker/invoke.py

inspo and help with model development: <br>
https://github.com/EmilienDupont/wgan-gp/tree/master <br>
https://github.com/ChickenBenny/Stock-prediction-with-GAN-and-WGAN 
