import config

import requests
import json
import os
import sys

import random

def call_image_ai(str_user):

    import httpx
    from PIL import Image
    from io import BytesIO
    import base64
    import uuid
    from urllib.parse import urlparse

    if config.CLOUD_TYPE_IMAGE != "":

        folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "images")
        if not os.path.exists(folder_path): os.makedirs(folder_path)
        guid = uuid.uuid4()
        image_name = f"{guid}.png"
        image_path = os.path.join(folder_path, image_name)      

        if "AZURE" in config.CLOUD_TYPE and config.USE_AZURE_ENTRA:
            import ai_azure_entra
            return ai_azure_entra.call_image_ai(str_user, image_path)

        # Azure + OpenAI
        if "AZURE" in config.CLOUD_TYPE_IMAGE or "OPENAI" in config.CLOUD_TYPE_IMAGE:
            #format = "url"
            format = "b64_json"
            payload = {
                "prompt": str_user,
                "quality": config.IMAGE_QUALITY,
                "style": config.IMAGE_STYLE,

                "size": "1024x1024",        # 1024x1024, 1792x1024, 1024x1792
                "n": 1,                     # number of files
                "response_format": format   # b64_json, url
            }

            if "OPENAI" in config.CLOUD_TYPE_IMAGE:
                payload["model"] = config.OPENAI_MODEL_IMAGE
                
            response = requests.post(
                config.API_URL_IMAGE,
                headers={
                    "Content-Type": "application/json",
                    config.KEY_HEADER_TEXT_IMAGE: config.KEY_HEADER_VALUE_IMAGE
                },
                data=json.dumps(payload)
            )
            response_text = response.text
            response_status = response.status_code

            if response_status != 200:
                raise Exception(f"Error: {response_status} - {response_text}")

            parsed_json = json.loads(response_text)

            if format == "url":
                url = parsed_json['data'][0]['url']
                generated_image = httpx.get(url).content
                with open(image_path, "wb") as file:
                    file.write(generated_image)
                image = Image.open(image_path)
            else:
                b64_image = parsed_json['data'][0]['b64_json']
                image_data = base64.b64decode(b64_image)
                image = Image.open(BytesIO(image_data))
                image.save(image_path)

        elif "STABILITYAI" in config.CLOUD_TYPE_IMAGE:
            negative_prompt = config.NEGATIV_PROMPT_IMAGE if config.MODEL_ID_IMAGE != "sd3-large-turbo" else ""
            seed = config.SEED_IMAGE if config.SEED_IMAGE != 0 else random.randint(0, 2**32 - 1)
            style = config.STYLE_PRESET if config.MODEL_ENDPOINT == "core" else ""

            response = requests.post(
                config.API_URL_IMAGE,
                headers={
                    "authorization": f"Bearer {config.STABILITYAI_API_KEY}",
                    "accept": "image/*"
                },
                files={"none": ''},
                data={
                    "prompt": str_user,
                    "model": config.MODEL_ID_IMAGE,
                    "output_format": config.OUTPUT_FORMAT_IMAGE,
                    "aspect_ratio": config.OUTPUT_ASPECT_RATIO_IMAGE,
                    "negative_prompt": negative_prompt,
                    "seed": seed,
                    "style_preset": style,
                },
            )

            image_path = image_path.replace(".png", f"_{seed}.png")
            if response.status_code == 200:
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                    image = Image.open(image_path)
            else:
                raise Exception(str(response.json()))
            
        elif "GOOGLEPROJECT" in config.CLOUD_TYPE_IMAGE:

            if "GOOGLEPROJECT" in config.CLOUD_TYPE_IMAGE and config.USE_GCP_OA2:
                import ai_gcp
                return ai_gcp.call_image_ai(str_user, image_path)

            payload = {
                "instances": [
                    {
                        "prompt": str_user
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "addWatermark": config.ADD_WATERMARK,
                }
            }

            if config.KEY_HEADER_TEXT_IMAGE != "":
                headers = {
                    "Content-Type": "application/json",
                    config.KEY_HEADER_TEXT_IMAGE : config.KEY_HEADER_VALUE_IMAGE
                }
            else:
                headers = { "Content-Type": "application/json" }

            response = requests.post(
                config.API_URL_IMAGE,
                headers=headers,
                data=json.dumps(payload)
            )
            response_text = response.text
            response_status = response.status_code

            if response_status != 200:
                raise Exception(f"Error: {response_status} - {response_text}")

            parsed_json = json.loads(response_text)

            b64_image = parsed_json['predictions'][0]['bytesBase64Encoded']
            image_data = base64.b64decode(b64_image)
            image = Image.open(BytesIO(image_data))
            image.save(image_path)


        if config.RESIZE_IMAGE:
            image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
            image.save(image_path)

        return image_path
