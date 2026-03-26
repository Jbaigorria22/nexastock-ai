import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

try:
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=[{"role": "user", "content": [{"text": "Say hello"}]}],
        inferenceConfig={"maxTokens": 50}
    )
    print(response["output"]["message"]["content"][0]["text"])
except Exception as e:
    print(f"Error: {e}")