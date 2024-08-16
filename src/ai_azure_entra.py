import config  
import json  
import os
import requests
from openai import AzureOpenAI  
from azure.identity import InteractiveBrowserCredential  
from datetime import datetime, timedelta  
  
TOKEN_CACHE_FILE = "token_cache.json"
TOKEN_PROVIDER_NS = "https://cognitiveservices.azure.com/.default"

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
  
def call_llm_azure_entra(str_user):  
    interactive_browser_credential = InteractiveBrowserCredential()  
    token_provider = CachedTokenProvider(interactive_browser_credential, TOKEN_PROVIDER_NS)  

    client = AzureOpenAI(  
        azure_endpoint=config.OPENAI_API_URL,  
        azure_ad_token_provider=token_provider.get_token, 
        api_version=config.OPENAI_API_VERSION  
    )  

    response = client.chat.completions.create(  
        model=config.OPENAI_DEPLOYMENT,  
        temperature=config.LLM_TEMPERATURE,  
        max_tokens=config.MAX_TOKENS,  
        messages=[  
            {"role": "system", "content": config.SYSTEM_PROMPT},  
            {"role": "user", "content": str_user},  
        ]  
    )
    result = response.choices[0].message.content.replace("```mermaid", "").replace("```", "").lstrip("\n")  
    return result

def call_image_ai(str_user, image_path, n_count = 1):
    from PIL import Image
    interactive_browser_credential = InteractiveBrowserCredential()  
    token_provider = CachedTokenProvider(interactive_browser_credential, TOKEN_PROVIDER_NS)  
  
    client = AzureOpenAI(  
        azure_endpoint=config.OPENAI_API_URL,  
        azure_ad_token_provider=token_provider.get_token, 
        api_version=config.OPENAI_API_VERSION_IMAGE
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

    original_image_path = image_path
    n = 1
    for item in json_response["data"]:
        image_path = original_image_path.replace(".png", f"_{n}.png") if n_count > 1 else original_image_path

        image_url = item["url"]
        generated_image = requests.get(image_url).content
        with open(image_path, "wb") as image_file:
            image_file.write(generated_image)

        if config.RESIZE_IMAGE:
            image = Image.open(image_path)  # Assuming PIL or Pillow for image handling
            image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
            image.save(image_path)
        n+=1
            
    return image_path # path of last generated image
