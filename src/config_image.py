import os
from types import SimpleNamespace
from file_helper import load_env

CLOUD_TYPE_IMAGE = ''

# Azure
# CLOUD_TYPE_IMAGE = 'AZURE+dall-e-3'                                     # best
        
# OpenAI        
# CLOUD_TYPE_IMAGE = 'OPENAI+dall-e-3'                                    # best
CLOUD_TYPE_IMAGE = 'OPENAI+gpt-image-1'                                 # best
        
# StabilityAI        
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large'                            # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large-turbo'                      # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-medium'                           # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large'                              # good
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large-turbo'                        # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-medium'                             # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+core'                                   # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+ultra'                                  # good

# VertexAI
# CLOUD_TYPE_IMAGE = 'VERTEXAI+gemini-2.0-flash-preview-image-generation' # best
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-4.0-generate-preview-06-06'         # good
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-4.0-ultra-generate-preview-06-06'   # best in class
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-generate-002'                   # best

# MLX (local generation, MacOS w/ Apple Silicon only)
# CLOUD_TYPE_IMAGE = 'MLX+mflux-flux1-schnell-4bit'                       # best 
# CLOUD_TYPE_IMAGE = 'MLX+mflux-flux1-dev-4bit'                           # good 
        
# IdeogramAI        
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_3'                                     # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_3_TURBO'                               # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_3_QUALITY'                             # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2A'                                    # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2A_TURBO'                              # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2'                                     # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2_TURBO'                               # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_1'                                     # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_1_TURBO'                               # best
        
# Black Forrest Labs        
# CLOUD_TYPE_IMAGE = 'BFL+flux-kontext-pro'                               # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-kontext-max'                               # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1-ultra'                             # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1'                                   # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro'                                       # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-dev'                                       # best

# RecraftAI
# CLOUD_TYPE_IMAGE = 'RECRAFTAI+recraftv3'                                # best
# CLOUD_TYPE_IMAGE = 'RECRAFTAI+recraft20b'                               # best

def get_image_config(CLOUD_TYPE_IMAGE: str = CLOUD_TYPE_IMAGE) -> SimpleNamespace:

    config = SimpleNamespace(
        CLOUD_TYPE_IMAGE=CLOUD_TYPE_IMAGE,
    )

    config.LOG = True
    config.TURBO_MODE = True
    config.USE_AZURE_ENTRA = True
    config.RESIZE_IMAGE = False
    config.RESIZE_IMAGE_WIDTH = 1024
    config.RESIZE_IMAGE_HEIGHT = 1024
    config.INSERT_IMAGE_AS_BACKGROUND = True
    config.OPTIMIZE_PROMPT_IMAGE = False

    model = CLOUD_TYPE_IMAGE.split("+")[-1]
    config.IMAGE_MODEL_ID = model
    system = CLOUD_TYPE_IMAGE.split("+")[0]

    load_env(system)

    config.IMAGE_HEADERS = {"Content-Type": "application/json"}

    # Branch logic
    if system in ["AZURE", "OPENAI"]:
        config.USE_AZURE_ENTRA_IMAGE = os.getenv('AZURE_ENTRA_AUTH', '').lower() in ('true', '1', 'yes')
        config.IMAGE_EXPLICIT_STYLE = "digital art"
        if model == "dall-e-3":
            config.IMAGE_QUALITY = "hd"     # hd, standard, auto
            config.IMAGE_STYLE = "vivid"    # natural, vivid
            config.IMAGE_SIZE = "1024x1024" # 1024x1024, 1792x1024, 1024x1792
        if model == "gpt-image-1":
            config.IMAGE_QUALITY = "medium" # hight, medium, low, auto
            config.IMAGE_SIZE = "1024x1024" # 1024x1024, 1536x1024, 1024x1536
            config.MODERATION = "low" # low, auto

        if system == "AZURE":
            config.AZURE_DEPLOYMENT_IMAGE = model
            config.IMAGE_API_VERSION = os.getenv('AZURE_API_VERSION_IMAGE')
            config.IMAGE_API_URL = (
                f"{os.getenv('AZURE_API_URL_IMAGE')}openai/deployments/"
                f"{config.AZURE_DEPLOYMENT_IMAGE}/images/generations"
                f"?api-version={config.IMAGE_API_VERSION}"
            )
            config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "api-key":  os.getenv('AZURE_API_KEY_IMAGE') or ""}

        elif system == "OPENAI":
            config.IMAGE_API_URL = os.getenv('OPENAI_API_URL_IMAGE')
            config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Authorization": "Bearer " + (os.getenv('OPENAI_API_KEY_IMAGE') or "")}

    elif system == "STABILITYAI":
        config.MODEL_ENDPOINT = model.split("-")[0]
        # Map special case for sd3.5
        config.MODEL_ENDPOINT = "sd3" if config.MODEL_ENDPOINT == "sd3.5" else config.MODEL_ENDPOINT

        # 3d-model analog-film anime cinematic comic-book digital-art 
        # enhance fantasy-art isometric line-art low-poly modeling-compound 
        # neon-punk origami photographic pixel-art tile-texture
        config.IMAGE_STYLE_PRESET = "digital-art"
        config.IMAGE_EXPLICIT_STYLE = (
            config.IMAGE_STYLE_PRESET if config.MODEL_ENDPOINT != "core" else ""
        )
        config.IMAGE_OUTPUT_FORMAT = "png" # png, jpeg, webp
        config.IMAGE_ASPECT_RATIO = "1:1" # 16:9 1:1 21:9 2:3 3:2 4:5 5:4 9:16 9:21
        config.IMAGE_SEED = 0 # Stable Diffusion images are generated deterministically based on the seed value (stored in the filename)
        config.IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"
        config.IMAGE_API_URL = f"{os.getenv('STABILITYAI_API_URL')}{config.MODEL_ENDPOINT}"
        config.IMAGE_HEADERS = {"authorization": "Bearer " + (os.getenv('STABILITYAI_API_KEY') or ""),"accept": "image/*"}

    elif system == "VERTEXAI":
        config.GCP_CLIENT_ID_IMAGE = os.getenv('GCP_CLIENT_ID')
        config.GCP_CLIENT_SECRET_IMAGE = os.getenv('GCP_CLIENT_SECRET')
        config.GOOGLE_ACCESS_TOKEN_IMAGE = os.getenv('GOOGLE_ACCESS_TOKEN_AI')

        config.IMAGE_ASPECT_RATIO = "1:1"  # 1:1 (1024x1024) 9:16 (768x1408) 16:9 (1408x768) 3:4 (896x1280) 4:3 (1280x896)
        config.IMAGE_EXPLICIT_STYLE = "digital art"
        config.IMAGE_ADD_WATERMARK = False
        config.IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"

        if model.startswith("imagen-"):
            config.IMAGE_API_URL = (
                f"https://{os.getenv('VERTEXAI_API_ENDPOINT_IMAGE')}/v1/projects/{os.getenv('VERTEXAI_PROJECT_ID_IMAGE')}"
                f"/locations/{os.getenv('VERTEXAI_LOCATION_ID_IMAGE')}/publishers/google/models/"
                f"{model}:predict"
            )
        elif model.startswith("gemini-"):
            config.IMAGE_API_URL = (
                f"https://{os.getenv('VERTEXAI_API_ENDPOINT_IMAGE')}/v1/projects/{os.getenv('VERTEXAI_PROJECT_ID_IMAGE')}"
                f"/locations/{os.getenv('VERTEXAI_LOCATION_ID_IMAGE')}/publishers/google/models/"
                f"{model}:generateContent"
            )
        else:
            raise Exception("Error: Unknown VertexAI image model")

    elif system == "MLX":
        config.IMAGE_SEED = 0
        #https://enragedantelope.github.io/Styles-FluxDev/
        config.IMAGE_EXPLICIT_STYLE = "photorealistic 3D art"
        #config.IMAGE_EXPLICIT_STYLE = "papercraft-kirigami art"
        #config.IMAGE_EXPLICIT_STYLE = "computer collage art"
        config.IMAGE_NEGATIV_PROMPT = ""
        config.IMAGE_HEIGHT = 1024 # 1024 # 512 # 768
        config.IMAGE_WIDTH = 1024 # 1024 # 512 # 768

        if "-flux1" in model:
            if "-schnell" in model:
                config.IMAGE_MODEL_VERSION = "schnell"
                config.IMAGE_NUM_STEPS = 2 # 2-4
            elif "-dev" in model:
                config.IMAGE_MODEL_VERSION = "dev"
                config.IMAGE_NUM_STEPS = 20 # 20-25
            else:
                raise Exception("Error: image model version not supported using MLX")
            
            if "-4bit" in model:
                config.IMAGE_MODEL_QUANTIZATION = 4
            elif "-8bit" in model:
                config.IMAGE_MODEL_QUANTIZATION = 8
            else:
                raise Exception("Error: image model quantization not supported using MLX")
        else:
            raise Exception("Error: image model not supported using MLX")

    elif system == "IDEOGRAMAI":
        config.IMAGE_SEED = 0
        config.IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Api-Key": os.getenv('IDEOGRAMAI_API_KEY') or ""}

        if model in ("V_3", "V_3_TURBO", "V_3_QUALITY"):
            config.IMAGE_API_URL = os.getenv('IDEOGRAMAI_API_V3_URL')
            config.IMAGE_STYLE_TYPE = "AUTO"  # AUTO, GENERAL, REALISTIC, DESIGN
            config.IMAGE_RESOLUTION = "1024x1024"
            if model == "V_3_QUALITY":
                config.IMAGE_RENDERING_SPEED = "QUALITY"
            elif model == "V_3_TURBO":
                config.IMAGE_RENDERING_SPEED = "TURBO"
            else:
                config.IMAGE_RENDERING_SPEED = "DEFAULT"
        elif model in ("V_2", "V_2_TURBO", "V_2A", "V_2A_TURBO"):
            config.IMAGE_API_URL = os.getenv('IDEOGRAMAI_API_URL')
            config.IMAGE_STYLE_PRESET = "GENERAL"  # DESIGN, GENERAL, REALISTIC, RENDER_3D, ANIME
            config.IMAGE_EXPLICIT_STYLE = config.IMAGE_STYLE_PRESET
            config.IMAGE_RESOLUTION = "RESOLUTION_1024_1024"
            config.IMAGE_OUTPUT_FORMAT = "png"
        else:
            config.IMAGE_API_URL = os.getenv('IDEOGRAMAI_API_URL')
            config.IMAGE_EXPLICIT_STYLE = "computer collage art"
            config.IMAGE_RESOLUTION = "RESOLUTION_1024_1024"
            config.IMAGE_OUTPUT_FORMAT = "png"

    elif system == "BFL":
        config.IMAGE_EXPLICIT_STYLE = "computer collage art"
        config.IMAGE_OUTPUT_FORMAT = "png"
        config.IMAGE_SEED = 0
        config.IMAGE_SAFETY_TOLERANCE = 6  # 0-6, 6 = least strict

        # Example branching by model
        if model == "flux-kontext-pro" or model == "flux-kontext-max":
            config.IMAGE_ASPECT_RATIO = "4:3" # between 21:9 and 9:21
            config.IMAGE_PROMPT_UPSAMPLING = False
        elif model == "flux-pro-1.1-ultra":
            config.IMAGE_RAW = False
            config.IMAGE_ASPECT_RATIO = "4:3" # between 21:9 and 9:21
        elif model == "flux-pro-1.1":
            config.IMAGE_HEIGHT = 1024
            config.IMAGE_WIDTH = 1024
            config.IMAGE_PROMPT_UPSAMPLING = False
        elif model == "flux-pro":
            config.IMAGE_HEIGHT = 1024
            config.IMAGE_WIDTH = 1024
            config.IMAGE_STEPS = 28
            config.IMAGE_INTERVAL = 2
            config.IMAGE_PROMPT_UPSAMPLING = False
            config.IMAGE_GUIDANCE = 3
        elif model == "flux-dev":
            config.IMAGE_HEIGHT = 1024
            config.IMAGE_WIDTH = 1024
            config.IMAGE_STEPS = 28
            config.IMAGE_PROMPT_UPSAMPLING = False
            config.IMAGE_GUIDANCE = 3
        else:
            raise Exception("Error: Unknown Flux image model")

        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "x-key": os.getenv('BFL_API_KEY') or ""}
        config.IMAGE_API_URL = os.getenv('BFL_API_URL')

    elif system == "RECRAFTAI":
        config.IMAGE_API_URL = os.getenv('RECRAFT_API_URL')
        config.IMAGE_HEADERS = {**config.IMAGE_HEADERS, "Authorization": "Bearer " + (os.getenv('RECRAFT_API_TOKEN') or "")}
        config.IMAGE_SIZE = "1024x1024"  # 1024x1024, 1365x1024, 1024x1365, 1536x1024, 1024x1536, 1820x1024, 1024x1820, 1024x2048, 2048x1024, 1434x1024, 1024x1434, 1024x1280, 1280x1024, 1024x1707, 1707x1024"
        config.IMAGE_RESPONSE_FORMAT = "url" # url, b64_json
        config.IMAGE_EXPLICIT_STYLE = ""
        config.IMAGE_SUBSTYLE = ""

        if model == "recraftv3":

            # IMAGE_STYLE = "digital_illustration"
            # IMAGE_SUBSTYLE = "2d_art_poster" # 2d_art_poster, 2d_art_poster_2, engraving_color, grain, hand_drawn, hand_drawn_outline, handmade_3d, infantile_sketch, pixel_art
            
            config.IMAGE_STYLE = "realistic_image"
            config.IMAGE_SUBSTYLE = "enterprise"
            
            # IMAGE_STYLE = "vector_illustration"
            # IMAGE_SUBSTYLE = "engraving" # engraving, line_art, line_circuit, linocut

        elif model == "recraft20b":
            
            # IMAGE_STYLE = "digital_illustration"
            # IMAGE_SUBSTYLE = "2d_art_poster" # 2d_art_poster, 2d_art_poster_2, 3d, 80s, engraving_color, flat_air_art, glow, grain, halloween_drawings, hand_drawn, hand_drawn_outline, handmade_3d, infantile_sketch, kawaii, pixel_art, psychedelic, seamless, stickers_drawings, voxel, watercolor
            
            config.IMAGE_STYLE = "realistic_image"
            config.IMAGE_SUBSTYLE = "enterprise"
            
            # IMAGE_STYLE = "vector_illustration"
            # IMAGE_SUBSTYLE = "70s" # 70s, cartoon, doodle_line_art, engraving, flat_2, halloween_stickers, kawaii, line_art, line_circuit, linocut, seamless
            
            # IMAGE_STYLE = "icon"
            # IMAGE_SUBSTYLE = "broken_line" # broken_line, colored_outline, colored_shapes, colored_shapes_gradient, doodle_fill, doodle_offset_fill, offset_fill, outline, outline_gradient, uneven_fill

        else:
            raise Exception("Error: Unknown Recraft image model")

    else:
        # If none of the above matched, it's unknown.
        raise Exception("Error: Unknown image system")

    return config
