import config
import prompts
import mermaid_helper as m

import requests
import json
import os
import sys

def call_llm_sequence(prompts_list, mermaid, topic_texts=""):
    new_mermaid = mermaid

    log_input = ""
    log_output = ""
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

    # Azure / OpenAI / GITHUB
    if "AZURE" in config.CLOUD_TYPE and config.USE_AZURE_ENTRA:
        import ai_azure_entra
        return ai_azure_entra.call_llm_azure_entra(str_user)
    
    if "AZURE+" in config.CLOUD_TYPE or \
       "OPENAI+" in config.CLOUD_TYPE or \
       "AZURE_META+" in config.CLOUD_TYPE or \
       "AZURE_Microsoft+" in config.CLOUD_TYPE or \
       "OPENROUTER+" in config.CLOUD_TYPE or \
       "GITHUB+" in config.CLOUD_TYPE:

        payload = {
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
            ]
        }
        if "OPENAI+" in config.CLOUD_TYPE or "GITHUB+" in config.CLOUD_TYPE or "OPENROUTER+" in config.CLOUD_TYPE:
            payload["model"] = config.OPENAI_MODEL

        response = requests.post(
            config.API_URL,
            headers = {
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

        usage = parsed_json["usage"]
        completion_tokens = parsed_json["usage"]["completion_tokens"]
        print("usage: " + json.dumps(usage))

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()
    
    # OLLAMA
    elif "OLLAMA+" in config.CLOUD_TYPE:
        if config.OPENAI_COMPATIBILITY:
            payload = {
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.LLM_TEMPERATURE,
                "messages": [
                    {"role": "system", "content": str_system},
                    {"role": "user", "content": str_user}
                ],
                "model": config.MODEL_ID
            }
        else:
            payload = {
                "system": str_system,
                "prompt": str_user,
                "model": config.MODEL_ID,
                "stream": False,
                "options": { "temperature": config.LLM_TEMPERATURE },
            }

            if config.model == "llama3-gradient":
                payload["options"]["num_ctx"] = 256000

        response = requests.post(
            config.API_URL,
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code            

        if response.status_code != 200:
            raise Exception(f"Error: {response_status} - {response_text}")
            
        parsed_json = json.loads(response_text)

        if config.OPENAI_COMPATIBILITY:
            result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("Here is the refined mindmap data:", "").replace("```", "").lstrip("\n").lstrip()
        else:
            result = parsed_json["response"].replace("```mermaid", "").replace("```", "").replace("Here is the refined mindmap data:", "").lstrip("\n").lstrip()
        
        lines = result.split("\n")
        if lines[0].startswith("  "):
            result = "\n".join(line[2:] for line in lines)
    
    # LMStudio
    elif "LMSTUDIO+" in config.CLOUD_TYPE:
        models_response = requests.get(config.API_URL + "/models")
        if models_response.status_code != 200:
            raise Exception(f"Error: {response_status} - {response_text}")
        models_data = json.loads(models_response.text)["data"]
        models_ids = [model["id"] for model in models_data]
        if config.MODEL_ID not in models_ids:
            raise Exception(f"Error: Model ID {config.MODEL_ID} not found in LMStudio models")

        payload = {
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
            ],
            "model": config.MODEL_ID,
            "stream": False,
            "seed": 0
        }
        response = requests.post(
            config.API_URL + "/chat/completions",
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer lm-studio"
            },
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code

        if response.status_code != 200:
            raise Exception(f"Error: {response_status} - {response_text}")
            
        parsed_json = json.loads(response_text)

        result_first = parsed_json["choices"][0]["message"]["content"]
        result = result_first.replace("```mermaid", "").replace("Here is the refined mindmap data:", "").replace("```", "").lstrip("\n").lstrip()
        
        lines = result.split("\n")
        if lines[0].startswith("  "):
            result = "\n".join(line[2:] for line in lines)

    # Vertex AI
    elif "VERTEXAI" in config.CLOUD_TYPE:
        import ai_gcp
        return ai_gcp.call_llm_gcp(str_user)

    # GEMINI
    elif "GEMINI" in config.CLOUD_TYPE:
        payload = {
            "contents": {
                "role": "user",
                "parts": [
                    { "text": str_system },
                    { "text": str_user }
                ]
            },
            "generation_config": {
                "temperature": config.LLM_TEMPERATURE, # Controls the randomness of the output. 
                #"topK": 3, # The maximum number of tokens to consider when sampling (default: 40)
                "topP": 0.95, # The maximum cumulative probability of tokens to consider when sampling (default: 0.95)
                "maxOutputTokens": config.MAX_TOKENS, # 2k / 4k
                "candidateCount": 1,
            }
        }

        payload["safety_settings"] = [
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
        ]

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

        parsed_json = json.loads(response_text)
        result = parsed_json["candidates"][0]["content"]["parts"][0]["text"]
        if "FLASH" in config.CLOUD_TYPE:
            result = result.replace("2 space", "")
        result = result.replace("```mermaid", "").replace("```", "").replace("mermaid\n", "").lstrip("\n")

    # CLAUDE3
    elif "CLAUDE3" in config.CLOUD_TYPE:
        # same like OpenAI but different
        payload = {
            "model": config.MODEL_ID,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "user", "content": "Hello, Claude."},
                {"role": "assistant", "content": str_system.replace("You are ", "Hi, I'm Claude, ")},
                {"role": "user", "content": str_user}
            ]
        }

        headers = {
            "content-type": "application/json",
            "anthropic-version": config.ANTHROPIC_VERSION,
            config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE,
        }

        # extend token output size for sonnet model
        if config.MODEL_ID == "claude-3-5-sonnet-20240620":
            headers["anthropic-beta"] = "max-tokens-3-5-sonnet-2024-07-15"

        response = requests.post(
            config.API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code

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

    # xAI
    elif "XAI+" in config.CLOUD_TYPE:
        # same like OpenAI
        payload = {
            "max_tokens": config.MAX_TOKENS,
            "model": config.MODEL_ID,
            "temperature": config.LLM_TEMPERATURE,
            "stream": False,
            "messages": [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
            ]
        }        

        response = requests.post(
            config.API_URL,
            headers = {
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

        usage = parsed_json["usage"]
        print("usage: " + json.dumps(usage))

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n")

    # GROQ
    elif "GROQ+" in config.CLOUD_TYPE:
        # same like OpenAI
        payload = {
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
            ]
        }
        payload["model"] = config.MODEL_ID

        response = requests.post(
            config.API_URL,
            headers = {
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
       
    # Perplexity
    elif "PERPLEXITY+" in config.CLOUD_TYPE:
        # same like OpenAI
        payload = {
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
            ]
        }        
        payload["model"] = config.MODEL_ID

        response = requests.post(
            config.API_URL,
            headers = {
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

    # MLX
    elif "MLX+" in config.CLOUD_TYPE:
        # same like OpenAI
        payload = {
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
            ]
        }

        response = requests.post(
            config.API_URL,
            headers = {
                "Content-Type": "application/json"
            },
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code

        if response_status != 200:
            raise Exception(f"Error: {response_status} - {response_text}")

        parsed_json = json.loads(response_text)
        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n")
    else:
        raise Exception("Error: Unknown CLOUD_TYPE")

    # needed for LLama3 large models
    result = result.replace("Here is the refined mind map:\n\n", "")
    result = result.replace("Here is the refined mindmap:\n\n", "")

    return result

