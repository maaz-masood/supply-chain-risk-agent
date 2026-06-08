from dotenv import load_dotenv
load_dotenv()

import os
import boto3

# Set the bearer token
bedrock_api_key = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = bedrock_api_key

# Create client without other credentials
client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy"
)

import json

response = client.invoke_model(
    modelId="amazon.nova-micro-v1:0",
    body=json.dumps({
        "messages": [{
            "role": "user",
            "content": [{"text": "Say hello in one sentence."}]
        }],
        "inferenceConfig": {"maxTokens": 100}
    }),
    contentType="application/json",
    accept="application/json"
)

result = json.loads(response['body'].read())
print(result['output']['message']['content'][0]['text'])