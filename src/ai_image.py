import config

import requests
import json

import random

def call_image_ai(image_path, str_user, n_count = 1):

    import httpx
    from PIL import Image
    from io import BytesIO
    import base64
    import uuid
    from urllib.parse import urlparse

    if config.CLOUD_TYPE_IMAGE != "":

        if "AZURE" in config.CLOUD_TYPE_IMAGE and config.USE_AZURE_ENTRA:
            import ai_azure_entra
            return ai_azure_entra.call_image_ai(str_user, image_path, n_count)

        # Azure + OpenAI Dall-e 3
        if "AZURE" in config.CLOUD_TYPE_IMAGE or "OPENAI" in config.CLOUD_TYPE_IMAGE:
            #format = "url"
            format = "b64_json"
            payload = {
                "prompt": str_user,
                "quality": config.IMAGE_QUALITY,
                "style": config.IMAGE_STYLE,

                "size": "1024x1024",        # 1024x1024, 1792x1024, 1024x1792
                "n": n_count,               # number of files
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
            else:
                b64_image = parsed_json['data'][0]['b64_json']
                image_data = base64.b64decode(b64_image)
                image = Image.open(BytesIO(image_data))
                image.save(image_path)

        # Stability AI / Stable Diffusion
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
            else:
                raise Exception(str(response.json()))

        # Google VertexAI            
        elif "VERTEXAI" in config.CLOUD_TYPE_IMAGE:
            import ai_gcp
            return ai_gcp.call_image_ai(str_user, image_path, n_count)

        # MLX
        elif "MLX" in config.CLOUD_TYPE_IMAGE:
            seed = config.SEED_IMAGE if config.SEED_IMAGE != 0 else random.randint(0, 2**32 - 1)
            if "sd" in config.MODEL_ID_IMAGE:
                import ai_image_mlx
                image_path = ai_image_mlx.generate_image(
                    config.MODEL_ID_IMAGE, 
                    str_user, 
                    config.NEGATIV_PROMPT_IMAGE, 
                    n_count, 
                    config.STEPS_IMAGE, 
                    0, 
                    1, 
                    1, 
                    True, 
                    False, 
                    False, 
                    image_path, 
                    seed)
            
            elif "flux" in config.MODEL_ID_IMAGE:
                import ai_image_diff
                image_path = ai_image_diff.generate_image(
                    str_user, 
                    config.NEGATIV_PROMPT_IMAGE, 
                    n_count, 
                    image_path, 
                    seed)
            else:
                raise Exception(f"Error: MODEL_ID_IMAGE for MLX not supported: {config.MODEL_ID_IMAGE}")
        else:
            raise Exception(f"Error: CLOUD_TYPE_IMAGE not supported: {config.CLOUD_TYPE_IMAGE}")

        if config.RESIZE_IMAGE and n_count == 1:
            image = Image.open(image_path)
            image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
            image.save(image_path)

        return image_path
