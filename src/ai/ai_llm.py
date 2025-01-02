import config
import ai.prompts as prompts
import mermaid.mermaid_helper as m
import input_helper

import requests
import json
import os
import sys

def call_llm_sequence(prompts_list, mermaid, topic_texts = "", check_valid_mermaid = True, data = "", mimeType = ""):
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
            new_mermaid = call_llm(this_prompt, data, mimeType)

            if check_valid_mermaid:
                not_valid = m.validate_mermaid(new_mermaid)
                if not_valid:
                    retries = retries + 1
            else:
                not_valid = False
                
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

def call_llm(str_user, data="", mimeType=""):
    if data != "" and (config.MULTIMODAL == False or mimeType not in config.MULTIMODAL_MIME_TYPES):
        raise Exception(f"Error: {config.CLOUD_TYPE} does not support multimodal actions.")

    result = ""
    str_system = config.SYSTEM_PROMPT

    # Azure / OpenAI / GITHUB
    if "AZURE" in config.CLOUD_TYPE and config.USE_AZURE_ENTRA:
        import ai.ai_azure_entra as ai_azure_entra
        return ai_azure_entra.call_llm_azure_entra(str_user, data, mimeType)
    
    # AWS Bedrock
    if "BEDROCK" in config.CLOUD_TYPE:
        import ai.ai_aws as ai_aws
        return ai_aws.call_llm(str_user, data, mimeType)
    
    if "AZURE+" in config.CLOUD_TYPE or \
       "OPENAI+" in config.CLOUD_TYPE or \
       "AZURE_META+" in config.CLOUD_TYPE or \
       "AZURE_Microsoft+" in config.CLOUD_TYPE or \
       "OPENROUTER+" in config.CLOUD_TYPE or \
       "GITHUB+" in config.CLOUD_TYPE:

        payload = {}

        if "OPENAI+" in config.CLOUD_TYPE and "+o1" in config.CLOUD_TYPE:
            payload["messages"] = [
                {"role": "user", "content": str_user}
            ]
            payload["max_completion_tokens"] = config.MAX_TOKENS
            payload["temperature"] = 1
        else:
            if data == "":  
                payload["messages"] = [
                        {"role": "system", "content": str_system},
                        {"role": "user", "content": str_user}
                ]
            elif mimeType == "image/png":
                payload["messages"] = [{"role": "system", "content": str_system}]
                number_tokens = 0
                for image in data:
                    number_tokens = number_tokens + input_helper.calculate_image_tokens(image)
                    if number_tokens > config.MAX_TOKENS:
                        break
                    payload["messages"].append({ 
                        "role": "user", 
                        "content": [{ 
                            "type": "image_url", 
                            "image_url": { 
                                "url": f"data:image/jpeg;base64,{image}", 
                                "detail": "high" 
                            } 
                        }] 
                    })
                payload["messages"].append({ "role": "user", "content": str_user })
            else:
                raise Exception(f"Error: {mimeType} not supported by {config.CLOUD_TYPE}")
            
            payload["max_tokens"] = config.MAX_TOKENS
            payload["temperature"] = config.LLM_TEMPERATURE

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
        
        if config.MODEL_ID == "nemotron":
            result = result.replace("mermaid mindmap\n", "")

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

    # GPT4ALL
    elif "GPT4ALL+" in config.CLOUD_TYPE:
        if not os.path.exists(os.path.join(config.MODEL_PATH, config.MODEL_ID)):
            for root, dirs, files in os.walk(config.MODEL_PATH):
                for filename in files:
                    if filename == config.MODEL_ID:
                        config.MODEL_PATH = root
                        break
            if not os.path.exists(os.path.join(config.MODEL_PATH, config.MODEL_ID)):
                raise Exception(f"Error: Model ID {config.MODEL_ID} not found in {config.MODEL_PATH}")

        from gpt4all import GPT4All
        model = GPT4All(config.MODEL_ID, model_path=config.MODEL_PATH, device=config.DEVICE, allow_download=config.ALLOW_DOWNLOAD)

        with model.chat_session(str_system):
            response = model.generate(str_user, temp=config.LLM_TEMPERATURE, max_tokens=config.MAX_TOKENS)

        result = response.replace("```mermaid", "").replace("```", "").lstrip("\n")

        lines = result.split("\n")
        if lines[0].startswith("  "):
            result = "\n".join(line[2:] for line in lines)

    # Vertex AI
    elif "VERTEXAI" in config.CLOUD_TYPE:
        import ai.ai_gcp as ai_gcp
        return ai_gcp.call_llm_gcp(str_user, data, mimeType)

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

        if data != "":
            if mimeType == "application/pdf":
                payload["contents"]["parts"].append({ "inlineData": {"data": data, "mimeType": mimeType } })
            elif mimeType == "image/png":
                for image in data:
                    payload["contents"]["parts"].append({ "inlineData": {"data": image, "mimeType": mimeType } })
            else:
                raise Exception(f"Error: {mimeType} not supported by GEMINI")

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

        usage = parsed_json["usageMetadata"]
        print("usage: " + json.dumps(usage))

        finish_reason = parsed_json["candidates"][0]["finishReason"]
        if finish_reason != "STOP":
            print("finishReason is " + finish_reason)

        result = parsed_json["candidates"][0]["content"]["parts"][0]["text"]
        if "FLASH" in config.CLOUD_TYPE:
            result = result.replace("2 space", "")
        
        result = result.replace("```mermaid", "").replace("```", "").replace("mermaid\n", "").lstrip("\n").lstrip()

    # Anthropic
    elif "ANTHROPIC" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [
                {"role": "user", "content": "Hello, Claude."},
                {"role": "assistant", "content": str_system.replace("You are ", "Hi, I'm Claude, ")}
            ]
        }

        if data == "":
            payload["messages"].append({ "role": "user", "content": str_user })
        else:
            if mimeType == "application/pdf":
                payload["messages"].append({ 
                    "role": "user", 
                    "content": [
                        {
                            "type": "document", 
                            "source":
                            { 
                                "type": "base64", 
                                "media_type": mimeType, 
                                "data": data
                            }
                        }, 
                        {
                            "type": "text", 
                            "text": str_user
                        }
                    ]
                })
            elif mimeType == "image/png":
                for image in data:
                    payload["messages"].append({ 
                        "role": "user", 
                        "content": [
                            {
                                "type": "image", 
                                "source":
                                { 
                                    "type": "base64", 
                                    "media_type": mimeType, 
                                    "data": image
                                }
                            }, 
                            {
                                "type": "text", 
                                "text": str_user
                            }
                        ]
                    })
            else:
                raise

        headers = {
            "content-type": "application/json",
            "anthropic-version": config.ANTHROPIC_VERSION,
            config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE,
        }
        if config.BETA_HEADER_KEY and config.BETA_HEADER_KEY != "":
            headers[config.BETA_HEADER_KEY] = config.BETA_HEADER_TEXT

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
        payload = {
            "model": config.MODEL_ID,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "stream": False
        }      

        if data == "":  
            payload["messages"] = [
                    {"role": "system", "content": str_system},
                    {"role": "user", "content": str_user}
            ]
        elif mimeType == "image/png":
            payload["messages"] = [{"role": "system", "content": str_system}]
            number_tokens = 0
            for image in data:
                number_tokens = number_tokens + input_helper.calculate_image_tokens(image)
                if number_tokens > config.MAX_TOKENS:
                    break
                payload["messages"].append({ 
                    "role": "user", 
                    "content": [{ 
                        "type": "image_url", 
                        "image_url": { 
                            "url": f"data:image/jpeg;base64,{image}", 
                            "detail": "high" 
                        } 
                    }] 
                })
            payload["messages"].append({ "role": "user", "content": str_user })
        else:
            raise Exception(f"Error: {mimeType} not supported by {config.CLOUD_TYPE}")
            
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
        payload = {
            "model": config.MODEL_ID,
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

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()
       
    # Perplexity
    elif "PERPLEXITY+" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
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

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()

    # DeepSeek
    elif "DEEPSEEK+" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
            "max_tokens": config.MAX_TOKENS,
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

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()

    # Alibaba Cloud
    elif "ALIBABACLOUD+" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
            "input": {
                "messages": [
                    {"role": "system", "content": str_system},
                    {"role": "user", "content": str_user}
                ]
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.LLM_TEMPERATURE,
                "enable_search": False,
                "incremental_output": False
            }
        }        

        response = requests.post(
            config.API_URL,
            headers = {
                "Content-Type": "application/json",
                config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE,
                "X-DashScope-SSE": "disable"
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

        finish_reason = parsed_json["output"]["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["output"]["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n")

    # Mistral AI
    elif "MISTRAL+" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "stream": False,
            "response_format": { "type": "text" },
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

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n").lstrip()

    # Hugging Face
    elif "HF+" in config.CLOUD_TYPE:
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

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n")

    # Fireworks.ai
    elif "FIREWORKS+" in config.CLOUD_TYPE:
        payload = {
            "model": config.MODEL_ID,
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

        finish_reason = parsed_json["choices"][0]["finish_reason"]
        if finish_reason == "length":
            print("Warning: Result truncated!")

        result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").replace("```", "").lstrip("\n")

    # MLX
    elif "MLX+" in config.CLOUD_TYPE:
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

