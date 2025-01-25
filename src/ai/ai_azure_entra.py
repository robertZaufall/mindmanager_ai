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
        model=config.OPENAI_DEPLOYMENT,  
        temperature=config.LLM_TEMPERATURE,  
        max_tokens=config.MAX_TOKENS,  
        messages=messages 
    )
    result = response.choices[0].message.content.replace("```mermaid", "").replace("```", "").lstrip("\n")  
    return result

def call_image_ai(model, str_user, image_paths, n_count = 1):
    from PIL import Image

    config = cfg_image.get_image_config(model)

    interactive_browser_credential = InteractiveBrowserCredential()  
    token_provider = CachedTokenProvider(interactive_browser_credential, TOKEN_PROVIDER_NS)  
  
    client = AzureOpenAI(  
        azure_endpoint=config.IMAGE_API_URL,  
        azure_ad_token_provider=token_provider.get_token, 
        api_version=config.IMAGE_API_VERSION
    )  

    response = client.images.generate(  
        model = config.OPENAI_DEPLOYMENT_IMAGE,  
        prompt = str_user,
        n = n_count,
        quality = config.IMAGE_QUALITY,
        style = config.IMAGE_STYLE,
        size = "1024x1024"
    )  
  
    json_response = json.loads(response.model_dump_json())

    n = 1
    for item in json_response["data"]:
        image_url = item["url"]
        generated_image = requests.get(image_url).content
        for image_path in image_paths:
            image_path = image_path.replace(".png", f"_{n}.png") if n_count > 1 else image_path
            with open(image_path, "wb") as image_file:
                image_file.write(generated_image)

            if config.RESIZE_IMAGE:
                image = Image.open(image_path)  # Assuming PIL or Pillow for image handling
                image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
                image.save(image_path)
        n+=1
            
    return image_paths # path of last generated image
