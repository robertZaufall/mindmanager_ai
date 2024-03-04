import config
import prompts
import mermaid as m

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

        not_valid = True
        retries = 0
        while (not_valid and retries < config.MAX_RETRIES):
            new_mermaid = call_llm(this_prompt)
            not_valid = m.validate_mermaid(new_mermaid, config.LINE_SEPARATOR, config.INDENT_SIZE)
            if not_valid:
                retries = retries + 1
                
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
    result = ""
    
    str_system = config.SYSTEM_PROMPT

    # Azure / OpenAI
    if config.CLOUD_TYPE == "AZURE" or config.CLOUD_TYPE == "OPENAI":
        payload = {
            "max_tokens": config.MAX_TOKENS_DEEP,
            "temperature": config.LLM_TEMPERATURE,
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
    
    # OLLAMA
    elif "OLLAMA" in config.CLOUD_TYPE:
        payload = {
            "system": config.SYSTEM_PROMPT,
            "prompt": str_user,
            "model": config.MODEL_ID,
            "stream": False,
            "options": { "temperature": config.LLM_TEMPERATURE },
        }

        response = requests.post(
            config.API_URL,
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code

        if response.status_code != 200:
            raise Exception(f"Error: {response_status} - {response_text}")
        
        parsed_json = json.loads(response_text)
        result = parsed_json["response"].replace("```mermaid", "").replace("```", "").lstrip("\n")
    
    # GEMINI
    elif config.CLOUD_TYPE == "GEMINI" or config.CLOUD_TYPE == "GEMINIPROJECT":
        payload = {
            "contents": {
                "role": "user",
                "parts": [
                    { "text": str_system },
                    { "text": str_user }
                ]
            },
            "safety_settings": [
                { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },

                # not supported by now
                #{ "category": "HARM_CATEGORY_DEROGATORY", "threshold": "BLOCK_NONE" },
                #{ "category": "HARM_CATEGORY_TOXICITY", "threshold": "BLOCK_NONE" },
                #{ "category": "HARM_CATEGORY_VIOLENCE", "threshold": "BLOCK_NONE" },
                #{ "category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_NONE" },
                #{ "category": "HARM_CATEGORY_MEDICAL", "threshold": "BLOCK_NONE" },
                #{ "category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE" },
                #{ "category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_NONE" },
            ],
            "generation_config": {
                "temperature": config.LLM_TEMPERATURE, # Controls the randomness of the output. 
                #"topK": 3, # The maximum number of tokens to consider when sampling (default: 40)
                "topP": 0.95, # The maximum cumulative probability of tokens to consider when sampling (default: 0.95)
                "maxOutputTokens": config.MAX_TOKENS_DEEP, # 2k / 4k
                "candidateCount": 1,
            }
        }

        if config.KEY_HEADER_TEXT != "":
            headers = {
                "Content-Type": "application/json",
                config.KEY_HEADER_TEXT : config.KEY_HEADER_VALUE
            }
        else:
            headers = { "Content-Type": "application/json" }

        response = requests.post(
            config.API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code

        if response_status != 200:
            raise Exception(f"Error: {response_status} - {response_text}")

        if "\"finishReason\": \"STOP\"" in response_text:
            print("LLM response truncated: \"finishReason\": \"STOP\"\n")

        parsed_json = json.loads(response_text)
        
        if config.CLOUD_TYPE == "GEMINI":
            result = parsed_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            concatenated_texts = []
            for item in parsed_json:
                for candidate in item.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        text = part.get("text", "")
                        concatenated_texts.append(text)
            result = "\n".join(concatenated_texts)

        result = result.replace("```mermaid", "").replace("```", "").lstrip("\n")        

    # CLAUDE3
    elif "CLAUDE3" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
            "max_tokens": config.MAX_TOKENS_DEEP,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "user", "content": "Hello, Claude."},
                {"role": "assistant", "content": str_system.replace("You are ", "Hi, I'm Claude, ")},
                {"role": "user", "content": str_user}
            ]
        }

        response = requests.post(
            config.API_URL,
            headers={
                "content-type": "application/json",
                "anthropic-version": config.ANTHROPIC_VERSION,
                config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE,
            },
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code

        if response_status != 200:
            raise Exception(f"Error: {response_status} - {response_text}")

        parsed_json = json.loads(response_text)
        stop_reason = parsed_json["stop_reason"]
        stop_sequence = parsed_json["stop_sequence"]
        result = parsed_json["content"][0]["text"].replace("```mermaid", "").replace("```", "").replace("mermaid\n", "").lstrip("\n")

    return result
