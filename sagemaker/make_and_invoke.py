import boto3
import sagemaker
import json
import os
region = boto3.Session().region_name
client = boto3.client("sagemaker", region_name=region)

sagemaker_role = os.getenv["SAGEMAKER_ROLE"]
model_url = os.getenv["MODEL_URL"]
model_name = "financial-1y-wgan-gp"
endpoint_config_name = "financial-1y-wgan-gp-endpoint-config"
endpoint_name = "financial-1y-wgan-gp-endpoint-2"
image_uri = os.getenv["IMAGE_URI"] 

try:
    client.create_model(
        ModelName=model_name,
        ExecutionRoleArn=sagemaker_role,
        PrimaryContainer={"Image": image_uri, "Mode": "SingleModel", "ModelDataUrl": model_url},
    )

    print("Created model:", model_name)
except client.exceptions.ResourceInUse:
    print("Model exists, reusing:", model_name)

try:
    client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[{
            "VariantName": "AllTraffic",
            "ModelName": model_name,
            "ServerlessConfig": {"MemorySizeInMB": 2048, "MaxConcurrency": 1}
        }],
    )
    print("Created endpoint config:", endpoint_config_name)
except client.exceptions.ResourceInUse:
    print("Endpoint config exists:", endpoint_config_name)

try:
    client.create_endpoint(EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name)
    print("Creating endpoint:", endpoint_name)
except client.exceptions.ResourceInUse:
    client.update_endpoint(EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name)
    print("Updating endpoint:", endpoint_name)


waiter = client.get_waiter("endpoint_in_service")
waiter.wait(EndpointName=endpoint_name)
print("Endpoint InService:", endpoint_name)

runtime = boto3.client("sagemaker-runtime")

content_type = "application/json"
payload = [
    {
        "Open": 205.54,
        "High": 208.34,
        "Low": 203.19,
        "Close": 206.12,
        "Volume": 13304509,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-05-29"
    },
    {
        "Open": 205.86,
        "High": 207.88,
        "Low": 204.65,
        "Close": 205.94,
        "Volume": 15668216,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-05-30"
    },
    {
        "Open": 205.73,
        "High": 209.24,
        "Low": 203.34,
        "Close": 207.38,
        "Volume": 12949499,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-05-31"
    },
    {
        "Open": 206.88,
        "High": 212.54,
        "Low": 204.59,
        "Close": 210.64,
        "Volume": 27164528,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-01"
    },
    {
        "Open": 210.54,
        "High": 211.71,
        "Low": 209.42,
        "Close": 210.25,
        "Volume": 28471192,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-02"
    },
    {
        "Open": 210.5,
        "High": 211.54,
        "Low": 209.3,
        "Close": 209.86,
        "Volume": 14062903,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-03"
    },
    {
        "Open": 211.05,
        "High": 215.43,
        "Low": 210.42,
        "Close": 213.28,
        "Volume": 29185440,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-04"
    },
    {
        "Open": 213.39,
        "High": 217.2,
        "Low": 212.93,
        "Close": 215.03,
        "Volume": 28812709,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-05"
    },
    {
        "Open": 215.19,
        "High": 217.49,
        "Low": 213.49,
        "Close": 214.12,
        "Volume": 17814149,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-06"
    },
    {
        "Open": 214.08,
        "High": 217.79,
        "Low": 212.19,
        "Close": 215.39,
        "Volume": 30480953,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-07"
    },
    {
        "Open": 214.15,
        "High": 216.03,
        "Low": 213.57,
        "Close": 214.5,
        "Volume": 26648619,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-08"
    },
    {
        "Open": 214.48,
        "High": 215.99,
        "Low": 212.5,
        "Close": 213.61,
        "Volume": 13747372,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-09"
    },
    {
        "Open": 213.65,
        "High": 216.37,
        "Low": 211.42,
        "Close": 214.23,
        "Volume": 12848287,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-10"
    },
    {
        "Open": 215.82,
        "High": 217.65,
        "Low": 209.77,
        "Close": 210.24,
        "Volume": 13658796,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-11"
    },
    {
        "Open": 210.12,
        "High": 212.02,
        "Low": 204.62,
        "Close": 206.72,
        "Volume": 25598268,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-12"
    },
    {
        "Open": 206.91,
        "High": 208.97,
        "Low": 204.67,
        "Close": 205.66,
        "Volume": 18195758,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-13"
    },
    {
        "Open": 205.64,
        "High": 207.88,
        "Low": 203.03,
        "Close": 203.68,
        "Volume": 10225300,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-14"
    },
    {
        "Open": 202.97,
        "High": 205.52,
        "Low": 201.15,
        "Close": 204.42,
        "Volume": 26632783,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-15"
    },
    {
        "Open": 205.12,
        "High": 206.3,
        "Low": 200.99,
        "Close": 202.67,
        "Volume": 26312053,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-16"
    },
    {
        "Open": 203.13,
        "High": 203.72,
        "Low": 197.75,
        "Close": 199.91,
        "Volume": 19889876,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-17"
    },
    {
        "Open": 200.38,
        "High": 204.52,
        "Low": 198.51,
        "Close": 202.94,
        "Volume": 11338442,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-18"
    },
    {
        "Open": 202.38,
        "High": 203.06,
        "Low": 200.35,
        "Close": 202.58,
        "Volume": 29703419,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-19"
    },
    {
        "Open": 203.43,
        "High": 204.79,
        "Low": 201.84,
        "Close": 202.82,
        "Volume": 22963940,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-20"
    },
    {
        "Open": 201.97,
        "High": 203.47,
        "Low": 199.28,
        "Close": 200.03,
        "Volume": 20842659,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-21"
    },
    {
        "Open": 200.38,
        "High": 201.36,
        "Low": 197.15,
        "Close": 199.04,
        "Volume": 8423570,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-22"
    },
    {
        "Open": 200.35,
        "High": 201.93,
        "Low": 197.36,
        "Close": 199.36,
        "Volume": 10373139,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-23"
    },
    {
        "Open": 198.77,
        "High": 199.23,
        "Low": 194.82,
        "Close": 197.17,
        "Volume": 29999032,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-24"
    },
    {
        "Open": 196.83,
        "High": 198.48,
        "Low": 195.63,
        "Close": 198.01,
        "Volume": 17246766,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-25"
    },
    {
        "Open": 198.07,
        "High": 200.09,
        "Low": 195.79,
        "Close": 196.92,
        "Volume": 26892008,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-26"
    },
    {
        "Open": 196.62,
        "High": 197.72,
        "Low": 194.52,
        "Close": 196.44,
        "Volume": 33218352,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-27"
    },
    {
        "Open": 195.53,
        "High": 196.17,
        "Low": 194.3,
        "Close": 195.36,
        "Volume": 9873421,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-28"
    },
    {
        "Open": 195.4,
        "High": 200.51,
        "Low": 193.19,
        "Close": 199.07,
        "Volume": 31327886,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-29"
    },
    {
        "Open": 198.44,
        "High": 201.08,
        "Low": 196.34,
        "Close": 199.15,
        "Volume": 14081950,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-06-30"
    },
    {
        "Open": 199.43,
        "High": 200.26,
        "Low": 195.9,
        "Close": 197.14,
        "Volume": 23650304,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-01"
    },
    {
        "Open": 196.6,
        "High": 200.5,
        "Low": 194.73,
        "Close": 198.86,
        "Volume": 18986868,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-02"
    },
    {
        "Open": 199.78,
        "High": 200.35,
        "Low": 194.65,
        "Close": 196.53,
        "Volume": 14925877,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-03"
    },
    {
        "Open": 196.07,
        "High": 197.54,
        "Low": 195.47,
        "Close": 197.04,
        "Volume": 34582901,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-04"
    },
    {
        "Open": 196.85,
        "High": 198.29,
        "Low": 191.15,
        "Close": 193.28,
        "Volume": 13967106,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-05"
    },
    {
        "Open": 193.75,
        "High": 195.18,
        "Low": 189.46,
        "Close": 190.81,
        "Volume": 19684495,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-06"
    },
    {
        "Open": 190.1,
        "High": 192.88,
        "Low": 188.15,
        "Close": 191.28,
        "Volume": 19706838,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-07"
    },
    {
        "Open": 191.41,
        "High": 194.57,
        "Low": 190.41,
        "Close": 192.79,
        "Volume": 13118922,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-08"
    },
    {
        "Open": 193.54,
        "High": 195.82,
        "Low": 191.1,
        "Close": 193.21,
        "Volume": 31954761,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-09"
    },
    {
        "Open": 192.28,
        "High": 194.47,
        "Low": 191.15,
        "Close": 193.09,
        "Volume": 29899999,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-10"
    },
    {
        "Open": 193.19,
        "High": 194.2,
        "Low": 192.19,
        "Close": 192.6,
        "Volume": 21642511,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-11"
    },
    {
        "Open": 192.75,
        "High": 194.67,
        "Low": 187.75,
        "Close": 189.85,
        "Volume": 24736613,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-12"
    },
    {
        "Open": 190.29,
        "High": 191.19,
        "Low": 188.03,
        "Close": 188.58,
        "Volume": 18873803,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-13"
    },
    {
        "Open": 187.88,
        "High": 189.08,
        "Low": 186.83,
        "Close": 187.8,
        "Volume": 30306199,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-14"
    },
    {
        "Open": 187.06,
        "High": 190.41,
        "Low": 184.91,
        "Close": 189.88,
        "Volume": 20649115,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-15"
    },
    {
        "Open": 190.18,
        "High": 191.06,
        "Low": 187.99,
        "Close": 190.63,
        "Volume": 24937991,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-16"
    },
    {
        "Open": 190.8,
        "High": 193.02,
        "Low": 185.92,
        "Close": 187.36,
        "Volume": 32126585,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-17"
    },
    {
        "Open": 187.5,
        "High": 190.01,
        "Low": 185.95,
        "Close": 188.07,
        "Volume": 10667867,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-18"
    },
    {
        "Open": 188.26,
        "High": 189.95,
        "Low": 186.22,
        "Close": 187.43,
        "Volume": 34729123,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-19"
    },
    {
        "Open": 187.05,
        "High": 188.19,
        "Low": 185.34,
        "Close": 186.26,
        "Volume": 19858009,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-20"
    },
    {
        "Open": 186.39,
        "High": 188.19,
        "Low": 185.4,
        "Close": 187.49,
        "Volume": 31432839,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-21"
    },
    {
        "Open": 187.66,
        "High": 190.19,
        "Low": 186.02,
        "Close": 189.52,
        "Volume": 15686841,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-22"
    },
    {
        "Open": 189.11,
        "High": 192.24,
        "Low": 187.31,
        "Close": 191.38,
        "Volume": 20164411,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-23"
    },
    {
        "Open": 192.45,
        "High": 193.89,
        "Low": 187.99,
        "Close": 189.87,
        "Volume": 31755953,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-24"
    },
    {
        "Open": 190.14,
        "High": 191.88,
        "Low": 187.5,
        "Close": 189.38,
        "Volume": 9344027,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-25"
    },
    {
        "Open": 188.7,
        "High": 191.73,
        "Low": 188.15,
        "Close": 190.1,
        "Volume": 12166500,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-26"
    },
    {
        "Open": 190.47,
        "High": 192.97,
        "Low": 189.15,
        "Close": 192.05,
        "Volume": 32244264,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-27"
    },
    {
        "Open": 191.49,
        "High": 193.7,
        "Low": 190.73,
        "Close": 191.22,
        "Volume": 17179875,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-28"
    },
    {
        "Open": 191.68,
        "High": 193.47,
        "Low": 189.53,
        "Close": 190.96,
        "Volume": 15884479,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-29"
    },
    {
        "Open": 191.63,
        "High": 193.07,
        "Low": 187.73,
        "Close": 188.95,
        "Volume": 8497562,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-30"
    },
    {
        "Open": 188.48,
        "High": 190.01,
        "Low": 184.75,
        "Close": 186.78,
        "Volume": 20237301,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-07-31"
    },
    {
        "Open": 187.32,
        "High": 189.56,
        "Low": 186.29,
        "Close": 188.39,
        "Volume": 12578238,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-01"
    },
    {
        "Open": 188.63,
        "High": 191.9,
        "Low": 188.03,
        "Close": 191.04,
        "Volume": 28814992,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-02"
    },
    {
        "Open": 191.51,
        "High": 192.58,
        "Low": 190.34,
        "Close": 191.0,
        "Volume": 28788128,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-03"
    },
    {
        "Open": 192.09,
        "High": 194.86,
        "Low": 190.24,
        "Close": 193.01,
        "Volume": 29288948,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-04"
    },
    {
        "Open": 192.87,
        "High": 194.22,
        "Low": 191.29,
        "Close": 193.81,
        "Volume": 13562067,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-05"
    },
    {
        "Open": 193.37,
        "High": 193.98,
        "Low": 192.07,
        "Close": 192.65,
        "Volume": 13237196,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-06"
    },
    {
        "Open": 192.14,
        "High": 193.92,
        "Low": 191.59,
        "Close": 193.45,
        "Volume": 29662427,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-07"
    },
    {
        "Open": 192.97,
        "High": 196.99,
        "Low": 191.23,
        "Close": 196.52,
        "Volume": 30903535,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-08"
    },
    {
        "Open": 196.47,
        "High": 198.62,
        "Low": 195.94,
        "Close": 196.55,
        "Volume": 9600396,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-09"
    },
    {
        "Open": 196.75,
        "High": 201.52,
        "Low": 194.74,
        "Close": 199.72,
        "Volume": 28088365,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-10"
    },
    {
        "Open": 199.88,
        "High": 201.23,
        "Low": 192.82,
        "Close": 194.59,
        "Volume": 33288226,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-11"
    },
    {
        "Open": 195.07,
        "High": 196.87,
        "Low": 194.52,
        "Close": 196.28,
        "Volume": 17555196,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-12"
    },
    {
        "Open": 196.29,
        "High": 197.91,
        "Low": 195.73,
        "Close": 196.55,
        "Volume": 21021573,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-13"
    },
    {
        "Open": 197.41,
        "High": 198.74,
        "Low": 193.74,
        "Close": 196.06,
        "Volume": 27273297,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-14"
    },
    {
        "Open": 195.91,
        "High": 197.07,
        "Low": 194.78,
        "Close": 196.34,
        "Volume": 19066226,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-15"
    },
    {
        "Open": 197.94,
        "High": 199.2,
        "Low": 191.44,
        "Close": 192.54,
        "Volume": 21046468,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-16"
    },
    {
        "Open": 192.9,
        "High": 194.05,
        "Low": 190.26,
        "Close": 192.21,
        "Volume": 25352494,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-17"
    },
    {
        "Open": 191.72,
        "High": 194.57,
        "Low": 189.52,
        "Close": 192.99,
        "Volume": 29964696,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-18"
    },
    {
        "Open": 192.37,
        "High": 197.58,
        "Low": 190.09,
        "Close": 195.94,
        "Volume": 25955265,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-19"
    },
    {
        "Open": 196.22,
        "High": 196.71,
        "Low": 193.16,
        "Close": 195.02,
        "Volume": 27857417,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-20"
    },
    {
        "Open": 194.89,
        "High": 196.01,
        "Low": 192.43,
        "Close": 193.54,
        "Volume": 21060919,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-21"
    },
    {
        "Open": 193.96,
        "High": 195.56,
        "Low": 192.12,
        "Close": 192.67,
        "Volume": 15136029,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-22"
    },
    {
        "Open": 192.94,
        "High": 195.9,
        "Low": 191.06,
        "Close": 194.53,
        "Volume": 28241658,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-23"
    },
    {
        "Open": 194.49,
        "High": 197.33,
        "Low": 193.01,
        "Close": 195.27,
        "Volume": 34440556,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-24"
    },
    {
        "Open": 194.77,
        "High": 196.44,
        "Low": 193.12,
        "Close": 194.33,
        "Volume": 11314692,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-25"
    },
    {
        "Open": 193.45,
        "High": 196.13,
        "Low": 191.31,
        "Close": 195.42,
        "Volume": 20582006,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-26"
    },
    {
        "Open": 195.16,
        "High": 196.24,
        "Low": 194.56,
        "Close": 195.71,
        "Volume": 29496823,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-27"
    },
    {
        "Open": 196.21,
        "High": 199.37,
        "Low": 194.86,
        "Close": 197.71,
        "Volume": 14285088,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-28"
    },
    {
        "Open": 197.83,
        "High": 198.28,
        "Low": 196.0,
        "Close": 196.42,
        "Volume": 25887605,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-29"
    },
    {
        "Open": 195.68,
        "High": 197.41,
        "Low": 194.37,
        "Close": 195.87,
        "Volume": 33193536,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-30"
    },
    {
        "Open": 195.97,
        "High": 198.21,
        "Low": 194.7,
        "Close": 195.2,
        "Volume": 24353425,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-08-31"
    },
    {
        "Open": 195.43,
        "High": 196.94,
        "Low": 191.83,
        "Close": 192.44,
        "Volume": 20460255,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-09-01"
    },
    {
        "Open": 191.93,
        "High": 194.24,
        "Low": 191.32,
        "Close": 193.11,
        "Volume": 11912942,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-09-02"
    },
    {
        "Open": 193.2,
        "High": 195.34,
        "Low": 191.56,
        "Close": 193.71,
        "Volume": 16501424,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-09-03"
    },
    {
        "Open": 193.74,
        "High": 195.09,
        "Low": 191.91,
        "Close": 193.82,
        "Volume": 15468810,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-09-04"
    },
    {
        "Open": 193.15,
        "High": 194.9,
        "Low": 191.64,
        "Close": 193.46,
        "Volume": 9635156,
        "Dividends": 0.0,
        "Stock Splits": 0.0,
        "ticker": "JPM",
        "Date": "2025-09-05"
    }
]

response = runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType=content_type,
    Body=json.dumps(payload).encode("utf-8")
)

result = response["Body"].read().decode("utf-8")
print(result)
