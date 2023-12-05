import config
import prompts

import requests
import json

def call_llm_sequence(prompts_list, mermaid, topic_texts=""):
    new_mermaid = mermaid
    for prompt in prompts_list:
        new_mermaid = call_llm(prompts.prompt(prompt, new_mermaid, topic_texts=topic_texts))
    return new_mermaid

def call_llm(str_user):
    str_system = "You are a business consultant and helpful assistant."

    payload = {
        "max_tokens": config.MAX_TOKENS_DEEP,
        "temperature": config.OPENAI_TEMPERATURE,
        "messages": [
            {"role": "system", "content": str_system},
            {"role": "user", "content": str_user}
        ]
    }
    if config.CLOUD_TYPE == "OPENAI":
        payload["model"] = config.OPENAI_MODEL

    response = requests.post(
        config.API_URL,
        headers={
            "Content-Type": "application/json",
            config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE
        },
        data=json.dumps(payload)
    )
    response_text = response.text
    response_status = response.status_code

    if response_status != 200:
        raise Exception(f"Error: {response_status} - {response_text}")

    parsed_json = json.loads(response_text)
    result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").lstrip("\n")
    
    return result
