import config
import json
import boto3

def call_llm(str_user, data, mimeType):
    if data != "" and config.MULTIMODAL == False:
        raise Exception(f"Error: {config.CLOUD_TYPE} does not support multimodal actions.")

    result = ""
    model_id = config.AWS_MODEL_ID
    str_system = config.SYSTEM_PROMPT

    bedrock_client = boto3.client(
        service_name=config.AWS_SERVICE_NAME,
        region_name=config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY,
        aws_secret_access_key=config.AWS_SECRET_KEY
    )
    
    if model_id.startswith("amazon."):
        payload = [
            {
                "role": "user",
                "content": [{"text": str_user}],
            }
        ]

        response = bedrock_client.converse(
            modelId=model_id,
            messages=payload,
            inferenceConfig={ "maxTokens": config.MAX_TOKENS, "stopSequences":[], "temperature": config.LLM_TEMPERATURE, "topP": 0.9},
            additionalModelRequestFields={}
        )

        parsed_json = response
        response_status = parsed_json["ResponseMetadata"]["HTTPStatusCode"]
        usage = parsed_json.get("usage", {})
        result = response["output"]["message"]["content"][0]["text"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()

    elif model_id.startswith("anthropic."):
        payload = {
            config.AWS_MODEL_VERSION_KEY: config.AWS_MODEL_VERSION_TEXT,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
            ]
        }

        payload["messages"].append({ "role": "user", "content": "Hello, Claude." })
        payload["messages"].append({ "role": "assistant", "content": str_system.replace("You are ", "Hi, I'm Claude, ") })
        payload["messages"].append({ "role": "user", "content": str_user })

        response = bedrock_client.invoke_model(modelId=model_id, body=json.dumps(payload))

        response_status = response["ResponseMetadata"]["HTTPStatusCode"]
        response_text = response["body"].read().decode("utf-8")
        if response_status != 200:
            raise Exception(f"Error: {response_status} - {response_text}")

        parsed_json = json.loads(response_text)

        usage = parsed_json.get("usage", {})
        result = parsed_json["content"][0]["text"] \
                .replace("Here is the refined mind map in Mermaid syntax:", "") \
                .replace("Here is the mindmap in Mermaid syntax based on the summary:", "") \
                .replace("```mermaid", "") \
                .replace("```", "") \
                .replace("mermaid\n", "") \
                .lstrip("\n")

    elif model_id.startswith("mistral."):
        payload = {
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
            ]
        }

        payload["messages"].append({ "role": "system", "content": str_system })
        payload["messages"].append({ "role": "user", "content": str_user })                

        response = bedrock_client.invoke_model(modelId=model_id, body=json.dumps(payload))

        response_status = response["ResponseMetadata"]["HTTPStatusCode"]
        response_text = response["body"].read().decode("utf-8")
        if response_status != 200:
            raise Exception(f"Error: {response_status} - {response_text}")

        parsed_json = json.loads(response_text)

        usage = parsed_json.get("usage", {})
        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()

    else:
        raise Exception(f"Error: {model_id} not supported.")

    if len(usage) > 0:
        print("usage: " + json.dumps(usage))

    return result
