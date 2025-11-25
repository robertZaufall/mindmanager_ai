import os
import sys
import time
import config_image as cfg
from types import SimpleNamespace
import requests
import json

import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import file_helper

def call_image_ai(model, 
            image_paths, 
            context: str="",
            top_most_topic: str="", 
            subtopics: str="", 
            n_count = 1, 
            image_prompt="generic",
            data={}):

    import httpx
    from PIL import Image
    from io import BytesIO
    import base64
    import uuid
    from urllib.parse import urlparse

    config = cfg.get_image_config(model)

    if config.CLOUD_TYPE_IMAGE == "":
        raise Exception("Error: CLOUD_TYPE_IMAGE is not set in config_image.py")
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'image_prompts', f"{image_prompt}.py")
    if not os.path.exists(prompt_path):
        raise Exception(f"Error: {prompt_path} does not exist.")
    module = file_helper.load_module_from_path(prompt_path, "mprompt")
    mprompt = module.MPrompt(config.CLOUD_TYPE_IMAGE, config.IMAGE_EXPLICIT_STYLE if hasattr(config, "IMAGE_EXPLICIT_STYLE") else "")

    str_user = mprompt.get_prompt(context=context, top_most_topic=top_most_topic, subtopics=subtopics)

    if "AZURE" in config.CLOUD_TYPE_IMAGE and config.USE_AZURE_ENTRA_IMAGE:
        n_count = 1 # override n_count to 1
        import ai.ai_azure_entra as ai_azure_entra
        return ai_azure_entra.call_image_ai(model=model, str_user=str_user, image_paths=image_paths, n_count=n_count, data=data)

    # Azure + OpenAI Dall-e 3
    if "AZURE" in config.CLOUD_TYPE_IMAGE or "OPENAI" in config.CLOUD_TYPE_IMAGE:

        # sora on Azure
        if "AZURE" in config.CLOUD_TYPE_IMAGE and "sora" in config.IMAGE_MODEL_ID:
            payload = {
                "model": config.IMAGE_MODEL_ID,
                "prompt": str_user,
                "n_seconds": config.VIDEO_LENGTH,
                "width": config.IMAGE_WIDTH,
                "height": config.IMAGE_HEIGHT,
            }
        
            response = requests.post(
                url=config.IMAGE_API_URL,
                headers=config.IMAGE_HEADERS,
                data=json.dumps(payload)
            )
            response_text = response.text
            response_status = response.status_code

            if response_status not in (200,201):
                raise Exception(f"Error: {response_status} - {response_text}")

            job_id = response.json()["id"]

            status_url = config.IMAGE_API_URL.replace('/jobs?', f"/jobs/{job_id}?")

            status = None
            while status not in ("succeeded", "failed", "cancelled"):
                time.sleep(5)
                status_response = requests.get(
                    status_url, 
                    headers=config.IMAGE_HEADERS,
                ).json()
                status = status_response.get("status")
        
            if status == "succeeded":
                generations = status_response.get("generations", [])
                if generations:
                    print(f"✅ Video generation succeeded.")
                    generation_id = generations[0].get("id")
                    video_url = config.IMAGE_API_URL.replace('/jobs?', f"/{generation_id}/content/video?")
                    video_response = requests.get(
                        video_url, 
                        headers=config.IMAGE_HEADERS
                    )
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

        # sora on OpenAI
        elif "OPENAI" in config.CLOUD_TYPE_IMAGE and "sora" in config.IMAGE_MODEL_ID:
            payload = {
                "model": config.IMAGE_MODEL_ID,
                "prompt": str_user,
                "seconds": config.VIDEO_LENGTH,
                "size": config.IMAGE_SIZE,
            }
        
            response = requests.post(
                url=config.IMAGE_API_URL,
                headers=config.IMAGE_HEADERS,
                data=json.dumps(payload)
            )
            response_text = response.text
            response_status = response.status_code

            if response_status not in (200,201):
                raise Exception(f"Error: {response_status} - {response_text}")

            job_id = response.json()["id"]

            status_url = f"{config.IMAGE_API_URL}/{job_id}"

            status = None
            while status not in ("completed", "failed", "cancelled"): # queued, in_progress, completed, failed
                time.sleep(5)
                status_response = requests.get(
                    status_url, 
                    headers=config.IMAGE_HEADERS,
                ).json()
                status = status_response.get("status")
        
            if status == "completed":
                video_url = f"{config.IMAGE_API_URL}/{job_id}/content"
                video_response = requests.get(
                    video_url, 
                    headers=config.IMAGE_HEADERS
                )
                if video_response.ok:
                    for i, image_path in enumerate(image_paths):
                        image_path = image_path.replace(".png", f"_{uuid.uuid4()}.mp4")
                        image_paths[i] = image_path
                        with open(image_path, "wb") as file:
                            file.write(video_response.content)
            else:
                raise Exception(f"Job didn't succeed. Status: {status}")

        # gpt-image-1, FLUX-1.1-pro, dall-e-3
        else:

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

            if "gpt-image-1" in config.IMAGE_MODEL_ID:
                payload["output_format"] = "png"
                payload["moderation"] = config.MODERATION

            if "OPENAI" in config.CLOUD_TYPE_IMAGE :
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

        if "V_3" in config.IMAGE_MODEL_ID:
            payload = {
                "prompt": str_user,
                "seed": seed,
                "resultion": config.IMAGE_RESOLUTION,
                "rendering_speed": config.IMAGE_RENDERING_SPEED,
                "magic_prompt": "AUTO",
                "negative_prompt": config.IMAGE_NEGATIV_PROMPT,
                "style_type": config.IMAGE_STYLE_TYPE,
            }
        else:
            payload = {
                "image_request": 
                {
                    "model": config.IMAGE_MODEL_ID,
                    "magic_prompt_option": "AUTO",
                    "prompt": str_user,
                    "seed": seed,
                }
            }

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

        if config.IMAGE_MODEL_ID == "flux-2-pro":
            payload["width"] = config.IMAGE_WIDTH
            payload["height"] = config.IMAGE_HEIGHT
            payload["seed"] = seed
            payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
            payload["output_format"] = config.IMAGE_OUTPUT_FORMAT

        elif config.IMAGE_MODEL_ID == "flux-2-flex":
            payload["width"] = config.IMAGE_WIDTH
            payload["height"] = config.IMAGE_HEIGHT
            payload["steps"] = config.IMAGE_STEPS
            payload["seed"] = seed
            payload["guidance"] = config.IMAGE_GUIDANCE
            payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
            payload["output_format"] = config.IMAGE_OUTPUT_FORMAT

        elif config.IMAGE_MODEL_ID == "flux-pro-1.1":
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

        elif config.IMAGE_MODEL_ID == "flux-kontext-pro" or config.IMAGE_MODEL_ID == "flux-kontext-max":
            payload["seed"] = seed
            payload["aspect_ratio"] = config.IMAGE_ASPECT_RATIO
            payload["prompt_upsampling"] = config.IMAGE_PROMPT_UPSAMPLING
            payload["safety_tolerance"] = config.IMAGE_SAFETY_TOLERANCE
            payload["output_format"] = config.IMAGE_OUTPUT_FORMAT

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
        return ai_gcp.call_image_ai(model=model, str_user=str_user, image_paths=image_paths, n_count=n_count, data=data)

    # MLX
    elif "MLX+" in config.CLOUD_TYPE_IMAGE:
        seed = config.IMAGE_SEED if config.IMAGE_SEED != 0 else random.randint(0, 2**32 - 1)
        if "mflux-" in config.IMAGE_MODEL_ID:
            import ai.ai_image_mlx as ai_image_mlx
            image_paths = ai_image_mlx.generate_image(
                model=model,
                prompt=str_user, 
                negative_prompt=config.IMAGE_NEGATIV_PROMPT, 
                n_images=n_count, 
                outputs=image_paths, 
                seed=seed,
                data=data
                )
        else:
            raise Exception(f"Error: IMAGE_MODEL_ID for MLX not supported: {config.IMAGE_MODEL_ID}")
    
    # Alibabacloud
    elif "ALIBABACLOUD" in config.CLOUD_TYPE_IMAGE:
        n_count = 1 # override n_count to 1
        seed = config.IMAGE_SEED if config.IMAGE_SEED != 0 else random.randint(0, 2**16 - 1)

        payload = {
            "model": config.IMAGE_MODEL_ID,
            "input":
            {
                "prompt": str_user,
                "negative_prompt": config.IMAGE_NEGATIV_PROMPT,
            },
            "parameters": {
                "size": config.IMAGE_SIZE,
                "n": n_count,
                "seed": seed,
                "prompt_extend": config.IMAGE_PROMPT_EXTEND,
                "watermark": config.IMAGE_WATERMARK,
            }   
        }

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
        if 'output' not in parsed_json or 'task_id' not in parsed_json['output']:
            raise Exception("Error: Missing task_id in API response")
        id = parsed_json['output']['task_id']
        id_url = f"{config.IMAGE_API_URL_TASKS}/{id}"

        url = ""
        for _ in range(60):  # Maximum 60 retries
            result = requests.get(
                url=id_url,
                headers=config.IMAGE_HEADERS
            )

            if result.status_code != 200:
                raise Exception(f"Error: {result.status_code} - {result.text}")

            output = result.json().get("output", {})
            if output.get("task_status") == "SUCCEEDED":
                results = output.get("results", [])
                if results and "url" in results[0]:
                    url = results[0]["url"]
                    break
            time.sleep(1)
        else:
            raise Exception("Error: Image generation timed out or failed to complete.")

        if url != "":
            generated_image = httpx.get(url).content
            for image_path in image_paths:
                with open(image_path, "wb") as file:
                    file.write(generated_image)
        else:
            raise Exception(f"Error generating image.")

    # FAL
    elif "FAL" in config.CLOUD_TYPE_IMAGE:
        n_count = 1 # override n_count to 1
        format = config.IMAGE_OUTPUT_FORMAT

        if "hunyuan-image" in model:
            payload = {
                "prompt": str_user,
                "negative_prompt": config.IMAGE_NEGATIV_PROMPT,
                "image_size": config.IMAGE_SIZE,
                "num_images": n_count,
                "num_inference_steps": config.IMAGE_NUM_INFERENCE_STEPS,
                "guidance_scale": config.IMAGE_GUIDANCE_SCALE,
                "seed": config.IMAGE_SEED,
                "enable_safety_checker": config.IMAGE_ENABLE_SAFETY_CHECKER,
                "sync_mode": config.IMAGE_SYNC_MODE,
                "output_format": format,
                "enable_prompt_expansion": config.IMAGE_ENABLE_PROMPT_EXPANSION,
            }
        elif "bytedance/seedream" in model:
            payload = {
                "prompt": str_user,
                "image_size": config.IMAGE_SIZE,
                "num_images": n_count,
                "seed": config.IMAGE_SEED,
                "sync_mode": config.IMAGE_SYNC_MODE,
                "enable_safety_checker": config.IMAGE_ENABLE_SAFETY_CHECKER,
            }
        else:
            raise Exception("Error: Unknown FAL image model")
        
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

        id = parsed_json.get('request_id', '')
        if id == '':
            raise Exception("Error: Missing request_id in API response")
        status_url = parsed_json.get('status_url', '')
        if status_url == '':
            raise Exception("Error: Missing status_url in API response")

        result = None
        for _ in range(60):  # Maximum 60 retries
            status = requests.get(
                url=status_url,
                headers=config.IMAGE_HEADERS
            )

            if status.status_code not in [200, 202]:
                raise Exception(f"Error: {status.status_code} - {status.text}")

            status_json = status.json()
            if status_json.get("status") == "COMPLETED":
                response_url = status_json.get("response_url", '')
                if response_url == '':
                    raise Exception("Error: Missing response_url in API response")
                result = requests.get(
                    url=response_url,
                    headers=config.IMAGE_HEADERS
                )
                if result is None:
                    raise Exception("Error: No result from image generation.")
                result_text = result.text
                result_status = result.status_code
                if result_status != 200:
                    raise Exception(f"Error: {result_status} - {result_text}")
                break
            time.sleep(1)
        else:
            raise Exception("Error: Image generation timed out or failed to complete.")

        result_json = json.loads(result_text)
        images = result_json.get('images', [])
        for image in images:
            url = image['url']
            if url.startswith('data:image'):
                header, encoded = url.split(',', 1)
                generated_image = base64.b64decode(encoded)
            else:
                generated_image = httpx.get(url).content                
            for image_path in image_paths:
                with open(image_path, "wb") as file:
                    file.write(generated_image)

    if config.RESIZE_IMAGE and n_count == 1:
        for image_path in image_paths:
            image = Image.open(image_path)
            image = image.resize((config.RESIZE_IMAGE_WIDTH, config.RESIZE_IMAGE_HEIGHT))
            image.save(image_path)

    return image_paths
