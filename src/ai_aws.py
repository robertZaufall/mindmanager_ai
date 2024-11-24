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

    payload = {
        config.AWS_MODEL_VERSION_KEY: config.AWS_MODEL_VERSION_TEXT,
        "max_tokens": config.MAX_TOKENS,
        "temperature": config.LLM_TEMPERATURE,
        "messages": [
        ]
    }

    if model_id.startswith("anthropic."):
        payload["messages"].append({ "role": "user", "content": "Hello, Claude." })
        payload["messages"].append({ "role": "assistant", "content": str_system.replace("You are ", "Hi, I'm Claude, ") })
    else:
        payload["messages"].append({ "role": "system", "content": str_system })
        payload["messages"].append({ "role": "user", "content": str_user })
                
    payload["messages"].append({ "role": "user", "content": str_user })

    response = bedrock_client.invoke_model(modelId=model_id, body=json.dumps(payload))

    response_status = response["ResponseMetadata"]["HTTPStatusCode"]

    response_text = response["body"].read().decode("utf-8")
    if response_status != 200:
        raise Exception(f"Error: {response_status} - {response_text}")

    parsed_json = json.loads(response_text)

    usage = parsed_json["usage"]
    print("usage: " + json.dumps(usage))

    stop_reason = parsed_json["stop_reason"]
    stop_sequence = parsed_json["stop_sequence"]

    result = parsed_json["content"][0]["text"] \
            .replace("Here is the refined mind map in Mermaid syntax:", "") \
            .replace("Here is the mindmap in Mermaid syntax based on the summary:", "") \
            .replace("```mermaid", "") \
            .replace("```", "") \
            .replace("mermaid\n", "") \
            .lstrip("\n")

    return result
