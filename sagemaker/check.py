import boto3, json
sm = boto3.client("sagemaker", region_name="us-east-1")

endpoint = sm.describe_endpoint(EndpointName="financial-1y-wgan-gp-endpoint")
print("Status:", endpoint["EndpointStatus"])
print("FailureReason:", endpoint.get("FailureReason",""))
print("EndpointConfig:", endpoint["EndpointConfigName"])

config = sm.describe_endpoint_config(EndpointConfigName=endpoint["EndpointConfigName"])
print(json.dumps(config["ProductionVariants"][0].get("ServerlessConfig", {}), indent=2))
