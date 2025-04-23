import time
import config_image as cfg
from types import SimpleNamespace
import requests
import json

import random

def call_image_ai(model, image_paths, str_user, n_count = 1):

    import httpx
    from PIL import Image
    from io import BytesIO
    import base64
    import uuid
    from urllib.parse import urlparse

    config = cfg.get_image_config(model)

    if config.CLOUD_TYPE_IMAGE != "":

        if "AZURE" in config.CLOUD_TYPE_IMAGE and config.USE_AZURE_ENTRA_IMAGE:
            n_count = 1 # override n_count to 1
            import ai.ai_azure_entra as ai_azure_entra
            return ai_azure_entra.call_image_ai(model=model, str_user=str_user, image_paths=image_paths, n_count=n_count)

        # Azure + OpenAI Dall-e 3
        if "AZURE" in config.CLOUD_TYPE_IMAGE or "OPENAI" in config.CLOUD_TYPE_IMAGE:
            n_count = 1 # override n_count to 1
            #format = "url"
            format = "b64_json"
            payload = {
                "prompt": str_user,
                "quality": config.IMAGE_QUALITY,
                "size": config.IMAGE_SIZE,
                "n": n_count,
            }

            if config.IMAGE_MODEL_ID == "dall-e-3":
                payload["style"] = config.IMAGE_STYLE
                payload["response_format"] = format

            if config.IMAGE_MODEL_ID == "gpt-image-1":
                payload["output_format"] = "png"

            if "OPENAI" in config.CLOUD_TYPE_IMAGE:
                payload["model"] = config.IMAGE_MODEL_ID
                
            response = requests.post(
                url=config.IMAGE_API_URL,
                headers=config.IMAGE_HEADERS,
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
                for image_path in image_paths:
                    with open(image_path, "wb") as file:
                        file.write(generated_image)
            else:
                b64_image = parsed_json['data'][0]['b64_json']
                image_data = base64.b64decode(b64_image)
                image = Image.open(BytesIO(image_data))
                for image_path in image_paths:
                    image.save(image_path)

        # Stability AI / Stable Diffusion
        elif "STABILITYAI" in config.CLOUD_TYPE_IMAGE:
            n_count = 1 # override n_count to 1
            negative_prompt = config.IMAGE_NEGATIV_PROMPT if config.IMAGE_MODEL_ID != "sd3-large-turbo" else ""
            seed = config.IMAGE_SEED if config.IMAGE_SEED != 0 else random.randint(0, 2**32 - 1)
            style = config.IMAGE_STYLE_PRESET if config.MODEL_ENDPOINT == "core" else ""

            response = requests.post(
                url=config.IMAGE_API_URL,
                headers=config.IMAGE_HEADERS,
                files={"none": ''},
                data={
                    "prompt": str_user,
                    "model": config.IMAGE_MODEL_ID,
                    "output_format": config.IMAGE_OUTPUT_FORMAT,
                    "aspect_ratio": config.IMAGE_ASPECT_RATIO,
                    "negative_prompt": negative_prompt,
                    "seed": seed,
                    "IMAGE_STYLE_PRESET": style,
                },
            )

            if response.status_code == 200:
                for i in range(len(image_paths)):
                    image_paths[i] = image_paths[i].replace(".png", f"_{seed}.png")
                    with open(image_paths[i], 'wb') as file:
                        file.write(response.content)
            else:
                raise Exception(str(response.json()))

        # Ideogram AI
        elif "IDEOGRAMAI" in config.CLOUD_TYPE_IMAGE:
            n_count = 1 # override n_count to 1
            seed = config.IMAGE_SEED if config.IMAGE_SEED != 0 else random.randint(0, 2**16 - 1)

            payload = { "image_request": {
                "model": config.IMAGE_MODEL_ID,
                "magic_prompt_option": "AUTO",
                "prompt": str_user,
                "seed": seed,
            } }

            if config.IMAGE_MODEL_ID == "V_2" or config.IMAGE_MODEL_ID == "V_2_TURBO":
                payload["image_request"]["style_type"] = config.IMAGE_EXPLICIT_STYLE
                payload["image_request"]["resolution"] = config.IMAGE_RESOLUTION

            if not config.IMAGE_MODEL_ID.startswith("V_2A"):
                payload["image_request"]["negative_prompt"] = config.IMAGE_NEGATIV_PROMPT

            response = requests.post(
                url=config.IMAGE_API_URL,
                json=payload,
                headers=config.IMAGE_HEADERS
            )
            response_text = response.text
            response_status = response.status_code

            if response_status != 200:
                raise Exception(f"Error: {response_status} - {response_text}")

            parsed_json = json.loads(response_text)

            url = parsed_json['data'][0]['url']
            generated_image = httpx.get(url).content

            for i in range(len(image_paths)):
                image_paths[i] = image_paths[i].replace(".png", f"_{seed}.png")
                with open(image_paths[i], 'wb') as file:
                    file.write(generated_image)

        # Black Forest Labs
        elif "BFL" in config.CLOUD_TYPE_IMAGE:
            n_count = 1 # override n_count to 1
            seed = config.IMAGE_SEED if config.IMAGE_SEED != 0 else random.randint(0, 2**16 - 1)

            payload = {
                "prompt": str_user
            }

            if config.IMAGE_MODEL_ID == "flux-pro-1.1":
                payload["width"] = config.IMAGE_WIDTH
                payload["height"] = config.IMAGE_HEIGHT
                payload["prompt_upsampling"] = config.IMAGE_PROMPT_UPSAMPLING
                payload["seed"] = seed
                payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
                payload["output_format"] = config.IMAGE_OUTPUT_FORMAT

            elif config.IMAGE_MODEL_ID == "flux-pro":
                payload["width"] = config.IMAGE_WIDTH
                payload["height"] = config.IMAGE_HEIGHT
                payload["steps"] = config.IMAGE_STEPS
                payload["prompt_upsampling"] = config.IMAGE_PROMPT_UPSAMPLING
                payload["seed"] = seed
                payload["guidance"] = config.IMAGE_GUIDANCE
                payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
                payload["interval"] = config.IMAGE_INTERVAL
                payload["output_format"] = config.IMAGE_OUTPUT_FORMAT

            elif config.IMAGE_MODEL_ID == "flux-dev":
                payload["width"] = config.IMAGE_WIDTH
                payload["height"] = config.IMAGE_HEIGHT
                payload["steps"] = config.IMAGE_STEPS
                payload["prompt_upsampling"] = config.IMAGE_PROMPT_UPSAMPLING
                payload["seed"] = seed
                payload["guidance"] = config.IMAGE_GUIDANCE
                payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
                payload["output_format"] = config.IMAGE_OUTPUT_FORMAT

            elif config.IMAGE_MODEL_ID == "flux-pro-1.1-ultra":
                payload["seed"] = seed
                payload["aspect_ratio"] = config.IMAGE_ASPECT_RATIO
                payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
                payload["output_format"] = config.IMAGE_OUTPUT_FORMAT
                payload["raw"] = config.IMAGE_RAW

            else:
                raise Exception("Error: Unknown Flux image model")

            response = requests.post(
                url=config.IMAGE_API_URL + config.IMAGE_MODEL_ID,
                json=payload,
                headers=config.IMAGE_HEADERS
            )
            response_text = response.text
            response_status = response.status_code

            if response_status != 200:
                raise Exception(f"Error: {response_status} - {response_text}")

            parsed_json = json.loads(response_text)
            id = parsed_json['id']

            url = ""
            while True:
                result = requests.get(
                    url=config.IMAGE_API_URL + 'get_result',
                    headers=config.IMAGE_HEADERS,
                    params={'id': id}
                )

                result_status = result.status_code
                if result_status != 200:
                    raise Exception(f"Error: {result_status} - {result.text}")

                result_json = result.json()
                if result_json["status"] == "Ready":
                    url = result_json['result']['sample']
                    break
                
                time.sleep(1)

            if url != "":
                generated_image = httpx.get(url).content
                for image_path in image_paths:
                    with open(image_path, "wb") as file:
                        file.write(generated_image)
            else:
                raise Exception(f"Error generating image.")
            
        # RecraftAI
        elif "RECRAFTAI" in config.CLOUD_TYPE_IMAGE:
            n_count = 1 # override n_count to 1
            format = config.IMAGE_RESPONSE_FORMAT

            payload = {
                "prompt": str_user,
                "n": n_count,
                #"style_id": config.IMAGE_STYLE_ID,
                "style": config.IMAGE_STYLE,
                "substyle": config.IMAGE_SUBSTYLE, 
                "model": config.IMAGE_MODEL_ID,
                "response_format": format,
                "size": config.IMAGE_SIZE,
                #"controls": {
                #    "image_type": "realistic_image",
                #    "colors": [ { "rgb": [0,255,0] } ]
                #}
            }

            response = requests.post(
                url=config.IMAGE_API_URL,
                headers=config.IMAGE_HEADERS,
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
                for image_path in image_paths:
                    with open(image_path, "wb") as file:
                        file.write(generated_image)
            else:
                b64_image = parsed_json['data'][0]['b64_json']
                image_data = base64.b64decode(b64_image)
                image = Image.open(BytesIO(image_data))
                for image_path in image_paths:
                    image.save(image_path)

        # Google VertexAI            
        elif "VERTEXAI" in config.CLOUD_TYPE_IMAGE:
            n_count = 1 # override n_count to 1
            import ai.ai_gcp as ai_gcp
            return ai_gcp.call_image_ai(model=model, str_user=str_user, image_paths=image_paths, n_count=n_count)

        # MLX
        elif "MLX" in config.CLOUD_TYPE_IMAGE:
            seed = config.IMAGE_SEED if config.IMAGE_SEED != 0 else random.randint(0, 2**32 - 1)
            if "flux" in config.IMAGE_MODEL_ID or "sd3" in config.IMAGE_MODEL_ID:
                import ai.ai_image_mlx as ai_image_mlx
                image_paths = ai_image_mlx.generate_image(
                    model=model,
                    prompt=str_user, 
                    negative_prompt=config.IMAGE_NEGATIV_PROMPT, 
                    n_images=n_count, 
                    outputs=image_paths, 
                    seed=seed)
            else:
                raise Exception(f"Error: IMAGE_MODEL_ID for MLX not supported: {config.IMAGE_MODEL_ID}")
        else:
            raise Exception(f"Error: CLOUD_TYPE_IMAGE not supported: {config.CLOUD_TYPE_IMAGE}")

        if config.RESIZE_IMAGE and n_count == 1:
            for image_path in image_paths:
                image = Image.open(image_path)
                image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
                image.save(image_path)

        return image_paths
