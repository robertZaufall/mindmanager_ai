import config_llm as cfg
import config_image as cfg_image
import requests
import json
from types import SimpleNamespace
import google.auth

from google.auth.transport.requests import Request  
from google_auth_oauthlib.flow import InstalledAppFlow  

GCP_SCOPES = [
    "https://www.googleapis.com/auth/iam.test",
    "https://www.googleapis.com/auth/cloud-platform.read-only",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/compute.readonly",
    "https://www.googleapis.com/auth/generative-language.retriever.readonly",
    "openid"
   ]  

def credentials_info(config):
    return {  
    "installed": {  
        "client_id": config.GCP_CLIENT_ID,  
        "client_secret": config.GCP_CLIENT_SECRET,  
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",  
        "token_uri": "https://oauth2.googleapis.com/token"  
    }  
}  
 
def get_oauth2_credentials(config):  
    flow = InstalledAppFlow.from_client_config(credentials_info(config), GCP_SCOPES)  
    credentials = flow.run_local_server(port=0)  
    return credentials  

def get_credentials():  
    credentials, project = google.auth.default()  
    if not credentials.valid:  
        if credentials.expired and credentials.refresh_token:  
            credentials.refresh(Request())  
        else:  
            credentials.refresh(Request())  

    return credentials  
  
def call_llm_gcp(model, str_user, param, data, mimeType):

    config = cfg.get_config(model)
    
    if data != "" and config.MULTIMODAL == False:
        raise Exception(f"Error: {model} does not support multimodal actions.")

    result = ""

    credentials = get_credentials()  
    access_token = credentials.token   
    
    payload = {
        "contents": {
            "role": "user",
            "parts": [
                { "text": config.SYSTEM_PROMPT },
                { "text": str_user }
            ]
        },
        "generation_config": {
            "temperature": config.LLM_TEMPERATURE, # Controls the randomness of the output. 
            "topP": config.TOP_P, # The maximum cumulative probability of tokens to consider when sampling (default: 0.95)
            "maxOutputTokens": config.MAX_TOKENS, # 2k / 4k
            "candidateCount": 1,
        }
    }

    if "gemini-2.5-flash-preview" in config.MODEL_ID:
        payload["generation_config"]["thinkingConfig"] = {"thinkingBudget": config.THINKING_BUDGET}

    if param.endswith("_grounding") and "-lite" not in config.MODEL_ID:
        payload["tools"] = {"google_search": {}}
            
    if data != "":
            payload["contents"]["parts"].append({ "inlineData": {"data": data, "mimeType": mimeType } })

    headers = {
        "Content-Type": "application/json",
        "Authorization" : "Bearer " + access_token
    }

    response = requests.post(
        url=config.API_URL,
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
    result = result.replace("```mermaid", "").replace("```", "").replace("mermaid\n", "").lstrip("\n").lstrip()

    return result

def call_image_ai(model, str_user, image_paths, n_count = 1):
    from PIL import Image
    from io import BytesIO
    import base64
    from urllib.parse import urlparse

    config = cfg_image.get_image_config(model)

    credentials = get_credentials()  
    access_token = credentials.token   
    headers = {
        "Content-Type": "application/json",
        "Authorization" : "Bearer " + access_token
    }
    
    if config.IMAGE_MODEL_ID.startswith("imagen-"):
        payload = {
            "instances": [
                {
                    "prompt": str_user
                }
            ],
            "parameters": {
                "sampleCount": n_count,
                "addWatermark": config.IMAGE_ADD_WATERMARK,
            }
        }
    elif config.IMAGE_MODEL_ID.startswith("gemini-"):
        payload = {
            "contents": {
                "role": "user",
                "parts": [
                    { "text": "Please generate a " + str_user }
                ]
            },
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "OFF"
                }
            ]
        }
    else:
        raise Exception(f"Error: {config.MODEL_ID} is not supported.")

    response = requests.post(
        url=config.IMAGE_API_URL,
        headers=headers,
        data=json.dumps(payload)
    )
    response_text = response.text
    response_status = response.status_code

    if response_status != 200 or response_text == "":
        raise Exception(f"Error: {response_status} - {response_text}")

    parsed_json = json.loads(response_text)

    image = None
    if config.IMAGE_MODEL_ID.startswith("imagen-"):
        b64_image = parsed_json['predictions'][0]['bytesBase64Encoded']
        image_data = base64.b64decode(b64_image)
        image = Image.open(BytesIO(image_data))
    
    elif config.IMAGE_MODEL_ID.startswith("gemini-"):
        parts = parsed_json["candidates"][0]["content"]["parts"]
        for part in parts:
            if "inlineData" in part:
                image_data = part["inlineData"]["data"]
                mimeType = part["inlineData"]["mimeType"]
                if mimeType == "image/png":
                    image_data = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_data))
                break

    if image:
        if config.RESIZE_IMAGE:
            image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
            for image_path in image_paths:
                image.save(image_path)
        else:
            for image_path in image_paths:
                image.save(image_path)
    else:
        raise Exception(f"Error: No image data found in the response.")
            
    return image_paths