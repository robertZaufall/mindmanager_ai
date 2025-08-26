import uuid
import config_llm as cfg
import config_image as cfg_image
import requests
import json
import time
import os
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
    
    long_running = False
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
                },
                {
                    "category": "HARM_CATEGORY_IMAGE_HATE",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_IMAGE_DANGEROUS_CONTENT",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_IMAGE_HARASSMENT",
                    "threshold": "OFF"
                },
                {
                    "category": "HARM_CATEGORY_IMAGE_SEXUALLY_EXPLICIT",
                    "threshold": "OFF"
                }
            ]
        }
    elif config.IMAGE_MODEL_ID.startswith("veo-"):
        seed = config.VIDEO_SEED
        if seed == 0:
            seed = int.from_bytes(os.urandom(4), "big")

        long_running = True
        payload = {
            # "endpoint": f"projects/{config.IMAGE_PROJECT_ID}/locations/{config.IMAGE_LOCATION_ID}/publishers/google/models/{config.IMAGE_MODEL_ID}",
            "instances": [
                {
                    "prompt": str_user,
                }
            ],
            "parameters": {
                "aspectRatio": config.VIDEO_ASPECT_RATIO,
                "sampleCount": config.VIDEO_SAMPLE_COUNT,
                "durationSeconds": config.VIDEO_LENGTH,
                "personGeneration": config.VIDEO_PERSON_GENERATION,
                "addWatermark": config.VIDEO_ADD_WATERMARK,
                "includeRaiReason": config.VIDEO_INCLUDE_RAI_REASON,
                "generateAudio": config.VIDEO_GENERATE_AUDIO,
                "seed": seed,
                "negativePrompt": config.VIDEO_NEGATIVE_PROMPT
            }
        }
        if config.IMAGE_MODEL_ID.startswith("veo-3"):
            payload["parameters"]["resolution"] = config.VIDEO_RESOLUTION
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
    if not long_running:

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
    else:
        name = parsed_json.get("name")
        # name = "projects/PROJECT_ID/locations/us-central1/publishers/google/models/MODEL_ID/operations/a1b07c8e-7b5a-4aba-bb34-3e1ccb8afcc8"
        operations_url = config.IMAGE_API_URL.replace(":predictLongRunning", ":fetchPredictOperation")
        operations_payload = {
            "operationName": name
        }

        done = None
        while not done:
            time.sleep(5)
            operations_response = requests.post(
                url=operations_url,
                headers=headers,
                data=json.dumps(operations_payload)
            )
            operations_response_text = operations_response.text
            operations_response_status = operations_response.status_code

            if operations_response_status != 200 or operations_response_text == "":
                raise Exception(f"Error: {operations_response_status} - {operations_response_text}")

            operations_response_parsed_json = json.loads(operations_response_text)

            done = operations_response_parsed_json.get("done", False)
            if done:
                if operations_response_parsed_json.get("response"):
                    video_data = operations_response_parsed_json["response"].get("videos", [])
                    if video_data:
                        base64_array = video_data[0].get("bytesBase64Encoded")
                        if base64_array:
                            if isinstance(base64_array, list):
                                b64_str = "".join(base64_array)
                            else:
                                b64_str = base64_array
                            b64_str += "=" * (-len(b64_str) % 4)
                            video_bytes = base64.b64decode(b64_str)

                            for i, image_path in enumerate(image_paths):
                                image_path = image_path.replace(".png", f"_{uuid.uuid4()}.mp4")
                                image_paths[i] = image_path
                                with open(image_path, "wb") as file:
                                    file.write(video_bytes)
                            return image_paths
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