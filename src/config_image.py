from logging import config
import os
from types import SimpleNamespace
from file_helper import load_env

CLOUD_TYPE_IMAGE = ''

# Azure
# CLOUD_TYPE_IMAGE = 'AZURE+dall-e-3'                                      # best
# CLOUD_TYPE_IMAGE = 'AZURE+gpt-image-1'                                   # best
# CLOUD_TYPE_IMAGE = 'AZURE+FLUX-1.1-pro'                                  # best
# CLOUD_TYPE_IMAGE = 'AZURE+FLUX.1-Kontext-pro'                            # best

# CLOUD_TYPE_IMAGE = 'AZURE+sora'                                          # good
        
# OpenAI        
# CLOUD_TYPE_IMAGE = 'OPENAI+dall-e-3'                                     # best
CLOUD_TYPE_IMAGE = 'OPENAI+gpt-image-1.5'                                #
# CLOUD_TYPE_IMAGE = 'OPENAI+gpt-image-1'                                  # good
# CLOUD_TYPE_IMAGE = 'OPENAI+gpt-image-1-mini'                             # good
# CLOUD_TYPE_IMAGE = 'OPENAI+sora-2'                                       # best
# CLOUD_TYPE_IMAGE = 'OPENAI+sora-2-pro'                                   # best

# StabilityAI        
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large'                             # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large-turbo'                       # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-medium'                            # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large'                               # good
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large-turbo'                         # poor
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-medium'                              # poor
# CLOUD_TYPE_IMAGE = 'STABILITYAI+core'                                    # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+ultra'                                   # good

# VertexAI
# CLOUD_TYPE_IMAGE = 'VERTEXAI+gemini-3-pro-image-preview'                 # best in class (nano banana pro)
# CLOUD_TYPE_IMAGE = 'VERTEXAI+gemini-3-pro-image-preview-grounding'       # best in class (nano banana pro + vendor web search grounding)
# CLOUD_TYPE_IMAGE = 'VERTEXAI+gemini-2.5-flash-image'                     # best in class (nano banana)
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-4.0-generate-001'                    # best in class
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-4.0-ultra-generate-001'              # best in class
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-4.0-fast-generate-001'               # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-generate-002'                    # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-fast-generate-001'               # good

# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-3.1-fast-generate-preview'              # best
# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-3.1-generate-preview'                   # best
# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-3.0-fast-generate-001'                  # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-3.0-generate-001'                       # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-3.0-fast-generate-preview'              # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-3.0-generate-preview'                   # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+veo-2.0-generate-001'                       # best

# MLX (local generation, MacOS w/ Apple Silicon only)
# CLOUD_TYPE_IMAGE = 'MLX+mflux-schnell-4bit'                              # good
# CLOUD_TYPE_IMAGE = 'MLX+mflux-dev-4bit'                                  # poor (slow)
# CLOUD_TYPE_IMAGE = 'MLX+mflux-krea-dev-4bit'                             # good (slow)
# CLOUD_TYPE_IMAGE = 'MLX+mflux-qwen-6bit'                                 # good (slow)
# CLOUD_TYPE_IMAGE = 'MLX+mflux-fibo-4bit'                                 #
# CLOUD_TYPE_IMAGE = 'MLX+mflux-z-image-turbo-4bit'                        #

# IdeogramAI
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_3'                                      # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_3_TURBO'                                # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_3_QUALITY'                              # best
        
# Black Forrest Labs        
# CLOUD_TYPE_IMAGE = 'BFL+flux-2-max'                                      # best (highest quality)      ($ 0,07 + 0,030 per megapixel)
# CLOUD_TYPE_IMAGE = 'BFL+flux-2-pro'                                      # best (fast and efficient)   ($ 0,03 + 0,015 per megapixel)
# CLOUD_TYPE_IMAGE = 'BFL+flux-2-flex'                                     # best (quality with control) ($ 0,06 per megapixel)
# CLOUD_TYPE_IMAGE = 'BFL+flux-kontext-pro'                                # best ($ 0,04 per image)
# CLOUD_TYPE_IMAGE = 'BFL+flux-kontext-max'                                # best ($ 0,08 per image)
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1-ultra'                              # best ($ 0,06 per image)
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1'                                    # best ($ 0,04 per image)

# RecraftAI
# CLOUD_TYPE_IMAGE = 'RECRAFTAI+recraftv3'                                 # best
# CLOUD_TYPE_IMAGE = 'RECRAFTAI+recraft20b'                                # best

# Alibaba Cloud
# CLOUD_TYPE_IMAGE = 'ALIBABACLOUD+wan2.2-t2i-flash'                       # poor
# CLOUD_TYPE_IMAGE = 'ALIBABACLOUD+wan2.2-t2i-plus'                        # poor

# Fal.ai
# CLOUD_TYPE_IMAGE = 'FAL+hunyuan-image/v3'                                # poor
# CLOUD_TYPE_IMAGE = 'FAL+bytedance/seedream/v4'                           # best


def get_image_config(CLOUD_TYPE_IMAGE: str = CLOUD_TYPE_IMAGE) -> SimpleNamespace:

    config = SimpleNamespace(
        CLOUD_TYPE_IMAGE=CLOUD_TYPE_IMAGE,
    )

    config.LOG = True
    config.USE_AZURE_ENTRA_IMAGE = False
    config.INSERT_IMAGE_AS_BACKGROUND = False
    config.OPTIMIZE_PROMPT_IMAGE = False
    config.TURBO_MODE = True

    # only relevant for MACOS platform
    config.MACOS_ACCESS = 'appscript'

    model = CLOUD_TYPE_IMAGE.split("+")[-1]
    config.IMAGE_MODEL_ID = model
    system = CLOUD_TYPE_IMAGE.split("+")[0]

    load_env(system)

    config.IMAGE_HEADERS = {"Content-Type": "application/json"}

    # Branch logic
    if system == "AZURE":
        config.USE_AZURE_ENTRA_IMAGE = os.getenv('AZURE_ENTRA_AUTH', '').lower() in ('true', '1', 'yes')

        config.AZURE_DEPLOYMENT_IMAGE = model
        if model == "dall-e-3":
            config.IMAGE_API_VERSION = os.getenv('AZURE_API_VERSION_IMAGE_EASTUS')
            config.IMAGE_API_URL = (
                f"{os.getenv('AZURE_API_URL_IMAGE_EASTUS')}openai/deployments/"
                f"{config.AZURE_DEPLOYMENT_IMAGE}/images/generations"
                f"?api-version={config.IMAGE_API_VERSION}")
            config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "api-key":  os.getenv('AZURE_API_KEY_IMAGE_EASTUS') or ""}
        elif "sora" in model:
            config.IMAGE_API_VERSION = "preview" # os.getenv('AZURE_API_VERSION_IMAGE')
            config.IMAGE_API_URL = f"{os.getenv('AZURE_API_URL_IMAGE')}openai/v1/video/generations/jobs?api-version={config.IMAGE_API_VERSION}"
            config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "api-key":  os.getenv('AZURE_API_KEY_IMAGE') or ""}
        elif model == "gpt-image-1":
            config.IMAGE_API_VERSION = os.getenv('AZURE_API_VERSION_IMAGE_EASTUS')
            config.IMAGE_API_URL = (
                f"{os.getenv('AZURE_API_URL_IMAGE_WESTUS3')}openai/deployments/"
                f"{config.AZURE_DEPLOYMENT_IMAGE}/images/generations"
                f"?api-version={config.IMAGE_API_VERSION}")
            config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "api-key":  os.getenv('AZURE_API_KEY_IMAGE_WESTUS3') or ""}
        elif model in ("FLUX-1.1-pro", "FLUX.1-Kontext-pro"):
            config.IMAGE_API_VERSION = os.getenv('AZURE_API_VERSION_IMAGE')
            config.IMAGE_API_URL = (
                f"{os.getenv('AZURE_API_URL_IMAGE')}openai/deployments/"
                f"{config.AZURE_DEPLOYMENT_IMAGE}/images/generations"
                f"?api-version={config.IMAGE_API_VERSION}")
            config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "api-key":  os.getenv('AZURE_API_KEY_IMAGE') or ""}
        else:
            raise Exception("Error: Unsupported Azure image model")

    elif system == "OPENAI":
        if model in ("dall-e-3", "gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini"):
            config.IMAGE_API_URL = os.getenv('OPENAI_API_URL_IMAGE')
        elif "sora" in model:
            config.IMAGE_API_URL = os.getenv('OPENAI_API_URL_IMAGE_VIDEO')
        else:
            raise Exception("Error: Unknown OpenAI image model")
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Authorization": "Bearer " + (os.getenv('OPENAI_API_KEY_IMAGE') or "")}
        
    elif system == "STABILITYAI":
        config.MODEL_ENDPOINT = model.split("-")[0]
        config.MODEL_ENDPOINT = "sd3" if config.MODEL_ENDPOINT == "sd3.5" else config.MODEL_ENDPOINT
        config.IMAGE_API_URL = f"{os.getenv('STABILITYAI_API_URL')}{config.MODEL_ENDPOINT}"
        config.IMAGE_HEADERS = {"authorization": "Bearer " + (os.getenv('STABILITYAI_API_KEY') or ""),"accept": "image/*"}

    elif system == "VERTEXAI":
        config.GCP_CLIENT_ID_IMAGE = os.getenv('GCP_CLIENT_ID')
        config.GCP_CLIENT_SECRET_IMAGE = os.getenv('GCP_CLIENT_SECRET')
        config.GOOGLE_ACCESS_TOKEN_IMAGE = os.getenv('GOOGLE_ACCESS_TOKEN_AI')
        config.IMAGE_PROJECT_ID = os.getenv('VERTEXAI_PROJECT_ID_IMAGE')
        config.IMAGE_LOCATION_ID = os.getenv('VERTEXAI_LOCATION_ID_IMAGE')

        if model.startswith("imagen-"):
            #config.IMAGE_ASPECT_RATIO = "16:9"  # 1:1 (1024x1024) 9:16 (768x1408) 16:9 (1408x768) 3:4 (896x1280) 4:3 (1280x896)
            config.IMAGE_API_URL = (
                f"https://{os.getenv('VERTEXAI_API_ENDPOINT_IMAGE')}/v1/projects/{config.IMAGE_PROJECT_ID}"
                f"/locations/{config.IMAGE_LOCATION_ID}/publishers/google/models/"
                f"{model}:predict"
            )
        elif model.startswith("gemini-"):
            model = model.replace("-grounding", "")
            config.IMAGE_API_URL = (
                f"https://{os.getenv('VERTEXAI_API_ENDPOINT_GLOBAL_IMAGE')}/v1/projects/{config.IMAGE_PROJECT_ID}"
                f"/locations/{os.getenv('VERTEXAI_LOCATION_ID')}/publishers/google/models/"
                f"{model}:generateContent"
            )
        elif model.startswith("veo-"):
            config.IMAGE_API_URL = (
                f"https://{os.getenv('VERTEXAI_API_ENDPOINT_IMAGE')}/v1/projects/{config.IMAGE_PROJECT_ID}"
                f"/locations/{config.IMAGE_LOCATION_ID}/publishers/google/models/"
                f"{model}:predictLongRunning"
            )
        else:
            raise Exception("Error: Unknown VertexAI image model")

    # elif system == "IDEOGRAMAI":
    #     config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Api-Key": os.getenv('IDEOGRAMAI_API_KEY') or ""}
    #     config.IMAGE_API_URL = os.getenv('IDEOGRAMAI_API_V3_URL')

    elif system == "BFL":
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "x-key": os.getenv('BFL_API_KEY') or ""}
        config.IMAGE_API_URL = os.getenv('BFL_API_URL')

    elif system == "RECRAFTAI":
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Authorization": "Bearer " + (os.getenv('RECRAFT_API_TOKEN') or "")}
        config.IMAGE_API_URL = os.getenv('RECRAFT_API_URL')

    elif system == "ALIBABACLOUD":
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Authorization": "Bearer " + (os.getenv('ALIBABACLOUD_API_KEY_IMAGE') or ""), "X-DashScope-Async": "enable"}
        config.IMAGE_API_URL = os.getenv('ALIBABACLOUD_API_URL_IMAGE')
        config.IMAGE_API_URL_TASKS = os.getenv('ALIBABACLOUD_API_URL_TASKS')

    elif system == "FAL":
        base_model = model.split("/")[0]
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Authorization": "Key " + (os.getenv('FAL_API_KEY') or "")}
        config.IMAGE_API_URL = f"{os.getenv('FAL_API_URL')}/{model}/text-to-image"
        config.IMAGE_API_URL_REQUESTS = f"{os.getenv('FAL_API_URL')}/{base_model}/requests"

    else:
        # If none of the above matched, it's unknown.
        raise Exception("Error: Unknown image system")

    return config
