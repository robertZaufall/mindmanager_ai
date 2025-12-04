import input_helper
import config_llm as cfg
import config_image as cfg_image
import json  
import os
import requests
from openai import AzureOpenAI  
from azure.identity import InteractiveBrowserCredential  
from datetime import datetime, timedelta  
from types import SimpleNamespace

TOKEN_CACHE_FILE = "token_cache.json"
TOKEN_PROVIDER_NS = "https://cognitiveservices.azure.com/.default"

# Azure Entra Roles needed:
# - Cognitive Services OpenAI User
# - Cognitive Services OpenAI Contributor

def load_token_cache():  
    if os.path.exists(TOKEN_CACHE_FILE):  
        with open(TOKEN_CACHE_FILE, "r") as f:  
            return json.load(f)  
    return {}  
  
def save_token_cache(cache):  
    with open(TOKEN_CACHE_FILE, "w") as f:  
        json.dump(cache, f)  
  
class CachedTokenProvider:  
    def __init__(self, credential, scope):  
        self._credential = credential  
        self._scope = scope  
        self._token_cache = load_token_cache()  
  
    def get_token(self):  
        # Check if token is cached and not expired  
        if 'access_token' in self._token_cache:  
            token_expiry = datetime.fromisoformat(self._token_cache['expires_on'])  
            if token_expiry > datetime.utcnow():  
                return self._token_cache['access_token']  
  
        # Otherwise, get a new token  
        token = self._credential.get_token(self._scope)  
  
        # Cache the new token  
        self._token_cache = {  
            'access_token': token.token,  
            'expires_on': datetime.utcfromtimestamp(token.expires_on).isoformat()  
        }  
        save_token_cache(self._token_cache)  
  
        return token.token  
  
def call_llm_azure_entra(model, str_user, data, mimeType):

    config = cfg.get_config(model)

    if data != "" and config.MULTIMODAL == False:
        raise Exception(f"Error: {config.CLOUD_TYPE} does not support multimodal actions.")

    interactive_browser_credential = InteractiveBrowserCredential()  
    token_provider = CachedTokenProvider(interactive_browser_credential, TOKEN_PROVIDER_NS)  

    client = AzureOpenAI(  
        azure_endpoint=config.API_URL,  
        azure_ad_token_provider=token_provider.get_token, 
        api_version=config.API_VERSION  
    ) 

    str_system = config.SYSTEM_PROMPT

    if data == "":  
        messages = [
                {"role": "system", "content": str_system},
                {"role": "user", "content": str_user}
        ]
    elif mimeType == "image/png":
        messages = [{"role": "system", "content": str_system}]
        number_tokens = 0
        for image in data:
            number_tokens = number_tokens + input_helper.calculate_image_tokens(image)
            if number_tokens > config.MAX_TOKENS:
                break
            messages.append({ 
                "role": "user", 
                "content": [{ 
                    "type": "image_url", 
                    "image_url": { 
                        "url": f"data:image/jpeg;base64,{image}", 
                        "detail": "high" 
                    } 
                }] 
            })
        messages.append({ "role": "user", "content": str_user })
    else:
        raise Exception(f"Error: {mimeType} not supported by {config.CLOUD_TYPE}")

    response = client.chat.completions.create(  
        model=config.AZURE_DEPLOYMENT,  
        temperature=config.LLM_TEMPERATURE,  
        max_tokens=config.MAX_TOKENS,  
        messages=messages 
    )
    result = response.choices[0].message.content.replace("```mermaid", "").replace("```", "").lstrip("\n")  
    return result

def call_image_ai(model, str_user, image_paths, n_count = 1, data={}):
    import base64
    import time
    import uuid
    from io import BytesIO
    from PIL import Image

    config = cfg_image.get_image_config(model)

    interactive_browser_credential = InteractiveBrowserCredential()
    token_provider = CachedTokenProvider(interactive_browser_credential, TOKEN_PROVIDER_NS)
    bearer_token = token_provider.get_token()

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    if "sora" in config.IMAGE_MODEL_ID:
        payload = {
            "model": config.IMAGE_MODEL_ID,
            "prompt": str_user,
            "n_seconds": data.get("video_length"),
            "width": data.get("image_size").split("x")[0],
            "height": data.get("image_size").split("x")[1],
        }

        response = requests.post(
            url=config.IMAGE_API_URL,
            headers=headers,
            data=json.dumps(payload),
        )
        response_text = response.text
        response_status = response.status_code

        if response_status not in (200, 201):
            raise Exception(f"Error: {response_status} - {response_text}")

        job_id = response.json()["id"]
        status_url = config.IMAGE_API_URL.replace("/jobs?", f"/jobs/{job_id}?")

        status = None
        while status not in ("succeeded", "failed", "cancelled"):
            time.sleep(5)
            status_response = requests.get(
                status_url,
                headers=headers,
            ).json()
            status = status_response.get("status")

        if status == "succeeded":
            generations = status_response.get("generations", [])
            if generations:
                generation_id = generations[0].get("id")
                video_url = config.IMAGE_API_URL.replace("/jobs?", f"/{generation_id}/content/video?")
                video_response = requests.get(video_url, headers=headers)
                if video_response.ok:
                    for i, image_path in enumerate(image_paths):
                        image_path = image_path.replace(".png", f"_{uuid.uuid4()}.mp4")
                        image_paths[i] = image_path
                        with open(image_path, "wb") as file:
                            file.write(video_response.content)
            else:
                raise Exception("No generations found in job result.")
        else:
            raise Exception(f"Job didn't succeed. Status: {status}")

        return image_paths

    n_count = 1  # override n_count to 1 (align with ai_image.py)
    response_format = "b64_json"
    payload = {
        "prompt": str_user,
        "n": n_count,
    }

    if config.IMAGE_MODEL_ID == "dall-e-3":
        payload["style"] = data.get("style")
        payload["response_format"] = response_format
        payload["quality"] = data.get("image_quality")
        payload["size"] = data.get("image_size")
    elif "gpt-image-1" in config.IMAGE_MODEL_ID:
        payload["output_format"] = "png"
        payload["moderation"] = data.get("moderation")
        payload["quality"] = data.get("image_quality")
        payload["size"] = data.get("image_size")
    elif config.IMAGE_MODEL_ID == "FLUX-1.1-pro":
        payload["size"] = data.get("image_size")
        payload["prompt_upsampling"] = data.get("prompt_upsampling")
    elif config.IMAGE_MODEL_ID == "FLUX.1-Kontext-pro":
        payload["aspect_ratio"] = data.get("image_aspect_ratio")
        payload["prompt_upsampling"] = data.get("prompt_upsampling")

    response = requests.post(
        url=config.IMAGE_API_URL,
        headers=headers,
        data=json.dumps(payload),
    )
    response_text = response.text
    response_status = response.status_code

    if response_status != 200:
        raise Exception(f"Error: {response_status} - {response_text}")

    parsed_json = json.loads(response_text)
    data_item = parsed_json["data"][0]

    if response_format == "url" and data_item.get("url"):
        generated_image = requests.get(data_item["url"]).content
        for image_path in image_paths:
            with open(image_path, "wb") as file:
                file.write(generated_image)
    else:
        b64_image = data_item.get("b64_json")
        if b64_image:
            image_data = base64.b64decode(b64_image)
            image = Image.open(BytesIO(image_data))
            for image_path in image_paths:
                image.save(image_path)
        elif data_item.get("url"):
            generated_image = requests.get(data_item["url"]).content
            for image_path in image_paths:
                with open(image_path, "wb") as file:
                    file.write(generated_image)
        else:
            raise Exception("Error: No image content returned from Azure Entra image generation.")

    return image_paths
