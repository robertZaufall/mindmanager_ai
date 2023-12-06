import config
import prompts

import requests
import json
import os
import sys

def call_llm_sequence(prompts_list, mermaid, topic_texts=""):
    new_mermaid = mermaid

    log_input = "# Test at https://mermaid.live/edit\n\n"
    log_output = "# Test at https://mermaid.live/edit\n\n"
    log_prompt = ""
    for prompt in prompts_list:
        log_input += new_mermaid + "\n\n"

        this_prompt = prompts.prompt(prompt, new_mermaid, topic_texts=topic_texts)
        new_mermaid = call_llm(this_prompt)

        log_output += new_mermaid + "\n\n"
        log_prompt += "Prompt = " + prompt + "\n-------\n" + this_prompt + "\n\n"

    if config.LOG == True:
        try:
            folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "log")
            if not os.path.exists(folder_path): os.makedirs(folder_path)        
            with open(folder_path + "/input.txt", "w", errors='ignore') as file:
                file.write(log_input)
            with open(folder_path + "/output.txt", "w") as file:
                file.write(log_output)
            with open(folder_path + "/prompt.txt", "w") as file:
                file.write(log_prompt)
        except:
            print("Error writing log files.")
    
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
    result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n")
    
    return result
