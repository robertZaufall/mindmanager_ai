import config_llm as cfg
import ai.prompts as prompts
import input_helper
import file_helper
import text_helper
from types import SimpleNamespace
import requests
import json
import os
import sys

def call_llm_sequence(model, prompts_list, input, topic_texts="", data="", mimeType="", freetext=""):

    config = cfg.get_config(model)

    result = input

    log_input = ""
    log_output = ""
    log_prompt = ""

    for prompt in prompts_list:
        log_input += result + "\n\n"

        this_prompt = prompts.prompt(param=prompt, text=result, topic_texts=topic_texts, freetext=freetext)
        if this_prompt == "":
            return ""

        result = call_llm(model=model, str_user=this_prompt, data=data, mimeType=mimeType)
                
        log_output += result + "\n\n"
        log_prompt += "Prompt = " + prompt + "\n-------\n" + this_prompt + "\n\n"

    if config.LOG == True:
        file_helper.log_input_output(log_input, log_output, log_prompt)
    
    return result

def call_llm(model, str_user, data="", mimeType=""):
    config = cfg.get_config(model)
    print("Using model: " + config.CLOUD_TYPE)

    if data != "" and (config.MULTIMODAL == False or mimeType not in config.MULTIMODAL_MIME_TYPES):
        raise Exception(f"Error: {config.CLOUD_TYPE} does not support multimodal actions.")

    def get_payload():
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
        return payload
        
    def get_response(payload):
        response = requests.post(
            url=config.API_URL,
            headers=config.HEADERS,
            data=json.dumps(payload)
        )
        response_text = response.text
        response_status = response.status_code            
        if response.status_code != 200:
            raise Exception(f"Error: {response_status} - {response_text}")
        parsed_json = json.loads(response_text)

        if "GEMINI" in config.CLOUD_TYPE:
            result = parsed_json["candidates"][0]["content"]["parts"][0]["text"]
            finish_reason = parsed_json["candidates"][0].get("finishReason", "")
            if finish_reason != "STOP" and finish_reason != "":
                print("finish reason is " + finish_reason)
            usage = parsed_json.get("usageMetadata", "")

        elif "ANTHROPIC" in config.CLOUD_TYPE:
            result = parsed_json["content"][0]["text"] 
            stop_reason = parsed_json["stop_reason"]
            stop_sequence = parsed_json["stop_sequence"]
            usage = parsed_json.get("usage", "")
        else:
            # OpenAI compatible
            result = parsed_json["choices"][0]["message"]["content"]
            finish_reason = parsed_json["choices"][0].get("finish_reason", "")
            if finish_reason == "length":
                print("warning: result truncated!")
            usage = parsed_json.get("usage", "")
        
        if usage != "":
            print("usage: " + json.dumps(usage))
        return text_helper.clean_result(result)

    result = ""
    str_system = config.SYSTEM_PROMPT

    # Azure / OpenAI / GITHUB
    if "AZURE" in config.CLOUD_TYPE and config.USE_AZURE_ENTRA:
        import ai.ai_azure_entra as ai_azure_entra
        return ai_azure_entra.call_llm_azure_entra(model=model, str_user=str_user, data=data, mimeType=mimeType)
    
    # AWS Bedrock
    if "BEDROCK" in config.CLOUD_TYPE:
        import ai.ai_aws as ai_aws
        return ai_aws.call_llm(model=model, str_user=str_user, data=data, mimeType=mimeType)
    
    if "AZURE+" in config.CLOUD_TYPE or \
       "OPENAI+" in config.CLOUD_TYPE or \
       "AZURE_FOUNDRY+" in config.CLOUD_TYPE or \
       "OPENROUTER+" in config.CLOUD_TYPE or \
       "GITHUB+" in config.CLOUD_TYPE:

        payload = {}

        if ("OPENAI+" in config.CLOUD_TYPE or "AZURE+" in config.CLOUD_TYPE) and ("+o1" in config.CLOUD_TYPE or "+o3" in config.CLOUD_TYPE):
            payload["messages"] = [{"role": "user", "content": str_user}]
            payload["max_completion_tokens"] = config.MAX_TOKENS
            payload["temperature"] = 1
            if "+o3" in config.CLOUD_TYPE:
                payload["reasoning_effort"] = config.REASONING_EFFORT
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
                    payload["messages"].append({"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}", "detail": "high"}}
                    ]})
                
                payload["messages"].append({ "role": "user", "content": str_user })
            else:
                raise Exception(f"Error: {mimeType} not supported by {config.CLOUD_TYPE}")
            
            payload["max_tokens"] = config.MAX_TOKENS
            payload["temperature"] = config.LLM_TEMPERATURE

        if "OPENAI+" in config.CLOUD_TYPE or "GITHUB+" in config.CLOUD_TYPE or "OPENROUTER+" in config.CLOUD_TYPE:
            payload["model"] = config.MODEL_ID

        result = get_response(payload)
    
    # OLLAMA
    elif "OLLAMA+" in config.CLOUD_TYPE:
        payload = get_payload()
        result = get_response(payload)
    
    # LMStudio
    elif "LMSTUDIO+" in config.CLOUD_TYPE:
        models_response = requests.get(config.API_URL.replace("/chat/completions", "/models"))
        if models_response.status_code != 200:
            raise Exception(f"Error: {models_response.status_code} - {models_response.text}")
        models_data = json.loads(models_response.text)["data"]
        models_ids = [model["id"] for model in models_data]
        if config.MODEL_ID not in models_ids:
            raise Exception(f"Error: Model ID {config.MODEL_ID} not found in LMStudio models ({models_ids})")
        
        payload = get_payload()
        result = get_response(payload)

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
        result = text_helper.clean_result(response)

    # Vertex AI
    elif "VERTEXAI" in config.CLOUD_TYPE:
        import ai.ai_gcp as ai_gcp
        return ai_gcp.call_llm_gcp(model=model, str_user=str_user, data=data, mimeType=mimeType)

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
                "temperature": config.LLM_TEMPERATURE,
                "maxOutputTokens": config.MAX_TOKENS,
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
            { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" }
        ]

        result = get_response(payload)

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
                payload["messages"].append({"role": "user", "content": [
                        {"type": "document", "source": {"type": "base64", "media_type": mimeType, "data": data}},
                        {"type": "text", "text": str_user}
                ]})
            elif mimeType == "image/png":
                for image in data:
                    payload["messages"].append({"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": mimeType, "data": image}},
                        {"type": "text", "text": str_user}
                    ]})
            else:
                raise

        result = get_response(payload)

    # xAI
    elif "XAI+" in config.CLOUD_TYPE:
        if data == "":  
            payload = get_payload()
        
        elif mimeType == "image/png":
            payload = {
                "model": config.MODEL_ID,
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.LLM_TEMPERATURE,
                "stream": False
            }      
            payload["messages"] = [{"role": "system", "content": str_system}]
            number_tokens = 0
            for image in data:
                number_tokens = number_tokens + input_helper.calculate_image_tokens(image)
                if number_tokens > config.MAX_TOKENS:
                    break
                payload["messages"].append({"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}", "detail": "high"}}
                ]})
            payload["messages"].append({ "role": "user", "content": str_user })
        else:
            raise Exception(f"Error: {mimeType} not supported by {config.CLOUD_TYPE}")
            
        result = get_response(payload)

    # GROQ
    elif "GROQ+" in config.CLOUD_TYPE:
        payload = get_payload()
        result = get_response(payload)
       
    # Perplexity
    elif "PERPLEXITY+" in config.CLOUD_TYPE:
        payload = get_payload()        
        result = get_response(payload)

    # DeepSeek
    elif "DEEPSEEK+" in config.CLOUD_TYPE:
        payload = get_payload()       
        result = get_response(payload)

    # Alibaba Cloud
    elif "ALIBABACLOUD+" in config.CLOUD_TYPE:
        payload = get_payload()        
        result = get_response(payload)

    # Mistral AI
    elif "MISTRAL+" in config.CLOUD_TYPE:
        payload = get_payload()
        payload["response_format"] = { "type": "text" }
        result = get_response(payload)

    # Hugging Face
    elif "HF+" in config.CLOUD_TYPE:
        payload = get_payload()
        del payload["model"]
        result = get_response(payload)

    # Fireworks.ai
    elif "FIREWORKS+" in config.CLOUD_TYPE:
        payload = get_payload()
        result = get_response(payload)

    # MLX
    elif "MLX+" in config.CLOUD_TYPE:
        payload = get_payload()
        del payload["model"]
        result = get_response(payload)
    else:
        raise Exception("Error: Unknown CLOUD_TYPE")

    return result

