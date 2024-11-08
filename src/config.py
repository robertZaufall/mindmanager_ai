import os

LOG = True # write source mindmaps, destination mindmaps and prompts to file

# set either MACOS_LIBRARY_FOLDER or WINDOWS_LIBRARY_FOLDER
MACOS_LIBRARY_FOLDER = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Mindjet", "MindManager", "23", "English", "Library")
WINDOWS_LIBRARY_FOLDER = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Mindjet", "MindManager", "23", "Library", "ENU")

SYSTEM_PROMPT = "You are a business consultant and helpful assistant."

# Azure serverless models, !use your model deployment name, ie. gpt-4o!
# CLOUD_TYPE = 'AZURE+gpt-4o'                                      # best
# CLOUD_TYPE = 'AZURE+gpt-4o-mini'                                 # ok
# CLOUD_TYPE = 'AZURE+gpt-4'                                       # best
# CLOUD_TYPE = 'AZURE+gpt-4-32k'                                   # best

# Azure serverless
# CLOUD_TYPE = 'AZURE_META+LLAMA3170B'                             # best, slow
# CLOUD_TYPE = 'AZURE_Microsoft+PHI35MINIINSTRUCT'                 # good

# OpenAI
# CLOUD_TYPE = 'OPENAI+gpt-4o-2024-08-06'                          # best
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini'                                # ok
# CLOUD_TYPE = 'OPENAI+gpt-4-turbo'                                # best

# Openrouter.ai
# CLOUD_TYPE = 'OPENROUTER+openai/o1-preview'                           # best in class, expensive
# CLOUD_TYPE = 'OPENROUTER+openai/o1-mini'                              # best, expensive
# CLOUD_TYPE = 'OPENROUTER+google/gemini-flash-1.5'                     # best, cheap
# CLOUD_TYPE = 'OPENROUTER+perplexity/llama-3.1-sonar-huge-128k-online' # good, slow

# Github Models
# CLOUD_TYPE = 'GITHUB+gpt-4o'                                     # best
# CLOUD_TYPE = 'GITHUB+gpt-4o-mini'                                # ok
# CLOUD_TYPE = "GITHUB+Phi-3-medium-128k-instruct"                 # not so good
# CLOUD_TYPE = "GITHUB+Phi-3.5-mini-instruct"                      # ok
# CLOUD_TYPE = "GITHUB+meta-llama-3.1-70b-instruct"                # best
# CLOUD_TYPE = "GITHUB+Mistral-large-2407"                         # good
# CLOUD_TYPE = "GITHUB+AI21-Jamba-Instruct"                        # best

# Claude3
# CLOUD_TYPE = 'CLAUDE3+OPUS'                                      # good
# CLOUD_TYPE = 'CLAUDE3+HAIKU'                                     # ok
# CLOUD_TYPE = 'CLAUDE35+SONNET'                                   # best
# CLOUD_TYPE = 'CLAUDE35+HAIKU'                                    # best

# Ollama (local models), best results
# CLOUD_TYPE = 'OLLAMA+wizardlm2'                                  # best
# CLOUD_TYPE = 'OLLAMA+llama3.1'                                   # ok
# CLOUD_TYPE = 'OLLAMA+llama3.1:70b'                               # ok, slow
# CLOUD_TYPE = 'OLLAMA+llama3.2:1b'                                # does not work
# CLOUD_TYPE = 'OLLAMA+llama3.2:3b'                                # ok
# CLOUD_TYPE = 'OLLAMA+phi3.5'                                     # does not work
# CLOUD_TYPE = 'OLLAMA+gemma2'                                     # ok
# CLOUD_TYPE = 'OLLAMA+gemma2:27b'                                 # does not work
# CLOUD_TYPE = 'OLLAMA+mixtral'                                    # ok
# CLOUD_TYPE = 'OLLAMA+solar'                                      # ok
# CLOUD_TYPE = 'OLLAMA+mistral'                                    # does not work
# CLOUD_TYPE = 'OLLAMA+openchat'                                   # does not work most of the time
# CLOUD_TYPE = 'OLLAMA+zephyr'                                     # does not work
# CLOUD_TYPE = 'OLLAMA+neural-chat'                                # does not work
# CLOUD_TYPE = 'OLLAMA+vicuna:13b-16k'                             # not good
# CLOUD_TYPE = 'OLLAMA+qwen2.5'                                    # good
# CLOUD_TYPE = 'OLLAMA+qwen2.5:14b'                                # good

# LMStudio
# CLOUD_TYPE = 'LMSTUDIO+nvidia_llama-3.1-nemotron-70b-instruct-hf'     # best, sloooow
# CLOUD_TYPE = 'LMSTUDIO+lmstudio-community/meta-llama-3.1-8b-instruct' # ok
# CLOUD_TYPE = 'LMSTUDIO+mlx-community/meta-llama-3.1-8b-instruct'      # ok
# CLOUD_TYPE = 'LMSTUDIO+bartowski/llama-3.2-3b-instruct'               # ok
# CLOUD_TYPE = 'LMSTUDIO+llama-3-8b-lexi-uncensored'                    # does not work
# CLOUD_TYPE = 'LMSTUDIO+phi-3.1-mini-4k-instruct'                      # does not work
# CLOUD_TYPE = 'LMSTUDIO+mlx-community/llama-3.2-3b-instruct'           # does not work
# CLOUD_TYPE = 'LMSTUDIO+nemotron-mini-4b-instruct'                     # does not work

# Google Gemini
# CLOUD_TYPE = 'GEMINI+gemini-1.5-pro-002'                         # best
# CLOUD_TYPE = 'GEMINI+gemini-1.5-pro-exp-0827'                    # best
# CLOUD_TYPE = 'GEMINI+gemini-1.5-flash-002'                       # best
# CLOUD_TYPE = 'GEMINI+gemini-1.5-flash-8b-exp-0924'               # best

# Google Gemini Vertex AI (needs pre-authentication ie. token)
# CLOUD_TYPE = 'VERTEXAI+gemini-1.5-pro-002'                       # best
# CLOUD_TYPE = 'VERTEXAI+gemini-1.5-pro-exp-0827'                  # best
CLOUD_TYPE = 'VERTEXAI+gemini-1.5-flash-002'                     # best

# xAI
# CLOUD_TYPE = 'XAI+grok-beta'                                     # good

# groq
# CLOUD_TYPE = 'GROQ+llama-3.1-70b-versatile'                      # best (error kg -> mm)
# CLOUD_TYPE = 'GROQ+llama-3.1-8b-instant'                         # good
# CLOUD_TYPE = 'GROQ+gemma-7b-it'                                  # good
# CLOUD_TYPE = 'GROQ+gemma2-9b-it'                                 # ok, generates maps only 3 levels deep
# CLOUD_TYPE = 'GROQ+mixtral-8x7b-32768'                           # good (token limit 5000 per minute)

# Perplexity
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-70b-instruct'                 # good
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-8b-instruct'                  # ok
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-small-128k-chat'        # good
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-large-128k-chat'        # good
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-small-128k-online'      # ok
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-large-128k-online'      # ok, up to good

# MLX server, macOS only (pip install -r requirements_mlx.txt --upgrade)
# python -m mlx_lm.server --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit --port 8080 --log-level DEBUG
# CLOUD_TYPE = 'MLX+mlx-community/Meta-Llama-3.1-8B-Instruct-4bit' # good

USE_AZURE_ENTRA = False

LLM_TEMPERATURE = float('0.5')

MAX_TOKENS = int('4000')
MAX_RETRIES = int('3')
TOP_MOST_RESULTS = int('5')
MAX_RETURN_WORDS = int('5')
LEVELS_DEEP = int('5')

INDENT_SIZE = int('2')
LINE_SEPARATOR = "\n"
OPENAI_COMPATIBILITY = False
MULTIMODAL = False
MULTIMODAL_MIME_TYPES = []

MARKDOWN_OPTIMIZATION_LEVEL = int('2')

if "OPENAI+" in CLOUD_TYPE:
    # MULTIMODAL = True
    # MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
    OPENAI_COMPATIBILITY = True
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_NATIVE')
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    OPENAI_MODEL = CLOUD_TYPE.split("+")[-1]
    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY

    if "gpt-4o" in OPENAI_MODEL:
        MAX_TOKENS = 16383
    
    MARKDOWN_OPTIMIZATION_LEVEL = 3

elif "AZURE+" in CLOUD_TYPE:
    # MULTIMODAL = True
    # MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
    OPENAI_COMPATIBILITY = True
    OPENAI_DEPLOYMENT = CLOUD_TYPE.split("+")[-1]
    OPENAI_API_KEY = os.getenv('OPENAI2_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI2_API_BASE')
    OPENAI_API_VERSION = os.getenv('OPENAI2_API_VERSION')

    OPENAI_MODEL = ""
    API_URL = f"{OPENAI_API_URL}openai/deployments/{OPENAI_DEPLOYMENT}/chat/completions?api-version={OPENAI_API_VERSION}"
    KEY_HEADER_TEXT = "api-key"
    KEY_HEADER_VALUE = OPENAI_API_KEY

    if "gpt-4o" in OPENAI_MODEL:
        MAX_TOKENS = 16383

    MARKDOWN_OPTIMIZATION_LEVEL = 3

elif "OPENROUTER+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

    OPENAI_MODEL = CLOUD_TYPE.split("+")[-1]
    API_URL = OPENROUTER_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENROUTER_API_KEY

    if "gpt-4o" in OPENAI_MODEL or "o1-mini" in OPENAI_MODEL or "o1-preview" in OPENAI_MODEL:
        MAX_TOKENS = 16383

    MARKDOWN_OPTIMIZATION_LEVEL = 3

elif "GITHUB+" in CLOUD_TYPE:
    model = CLOUD_TYPE.split("+")[-1]
    OPENAI_COMPATIBILITY = True
    GITHUB_TOKEN = os.getenv('GITHUB_MODELS_TOKEN')
    GITHUB_API_URL = "https://models.inference.ai.azure.com/chat/completions"
    OPENAI_MODEL = model

    API_URL = GITHUB_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GITHUB_TOKEN

    if "gpt-4o" in OPENAI_MODEL:
        MAX_TOKENS = 16383

    MARKDOWN_OPTIMIZATION_LEVEL = 3

elif "AZURE_META+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    META_MODEL = CLOUD_TYPE.split("+")[-1]
    OPENAI_API_KEY = os.getenv(f"AZURE_{META_MODEL}_KEY")
    OPENAI_API_URL = os.getenv(f"AZURE_{META_MODEL}_ENDPOINT") + "/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    OPENAI_MODEL = ""
    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY

elif "AZURE_Microsoft+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MICROSOFT_MODEL = CLOUD_TYPE.split("+")[-1]
    OPENAI_API_KEY = os.getenv(f"AZURE_{MICROSOFT_MODEL}_KEY")
    OPENAI_API_URL = os.getenv(f"AZURE_{MICROSOFT_MODEL}_ENDPOINT") + "/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    OPENAI_MODEL = ""
    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY

elif "GEMINI" in CLOUD_TYPE or "VERTEXAI" in CLOUD_TYPE:
    MULTIMODAL = True
    MULTIMODAL_MIME_TYPES = ["application/pdf"]

    system = CLOUD_TYPE.split("+")[0]
    if system == "GEMINI":
        model = CLOUD_TYPE.split("+")[-1]
        MAX_TOKENS = 8191
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY_AI')
        API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GOOGLE_API_KEY}"
        KEY_HEADER_TEXT = ""
        KEY_HEADER_VALUE = ""

    elif system == "VERTEXAI":
        model = CLOUD_TYPE.split("+")[-1]
        MAX_TOKENS = 8191
        PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
        API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
        LOCATION_ID = "us-central1"
        GOOGLE_ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN_AI') # limited time use
        API_URL = f"https://{API_ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{model}:generateContent"
        KEY_HEADER_TEXT = "Authorization"
        KEY_HEADER_VALUE = "Bearer " + GOOGLE_ACCESS_TOKEN

        # GCP
        # gcloud auth application-default login
        GCP_CLIENT_ID = os.getenv('GCP_CLIENT_ID')
        GCP_CLIENT_SECRET = os.getenv('GCP_CLIENT_SECRET')
        GCP_PROJECT_ID = PROJECT_ID
        GCP_ENDPOINT = API_ENDPOINT
        GCP_LOCATION = LOCATION_ID

elif "OLLAMA+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    if OPENAI_COMPATIBILITY:
        API_URL="http://localhost:11434/v1/chat/completions"
    else: 
        API_URL="http://localhost:11434/api/generate"

elif "LMSTUDIO+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    API_URL="http://localhost:1234/v1"

elif "CLAUDE3" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    generation = CLOUD_TYPE.split("+")[0]
    model = CLOUD_TYPE.split("+")[-1]
    BETA_HEADER_KEY = ""

    if generation == "CLAUDE3":
        if model == "HAIKU":
            MODEL_ID = "claude-3-haiku-20240307"
        elif model == "OPUS":
            MODEL_ID = "claude-3-opus-20240229"
            MARKDOWN_OPTIMIZATION_LEVEL = 3
        else:
            raise Exception("Error: Unsupported CLAUDE3 model")
    
    elif generation == "CLAUDE35":
        MAX_TOKENS = 8192
        if model == "HAIKU":
            MODEL_ID = "claude-3-5-haiku-20241022"
        elif model == "SONNET":
            MULTIMODAL = True
            MULTIMODAL_MIME_TYPES = ["application/pdf"]
            BETA_HEADER_KEY = "anthropic-beta"
            BETA_HEADER_TEXT = "pdfs-2024-09-25"
            
            MODEL_ID = "claude-3-5-sonnet-20241022"
            MARKDOWN_OPTIMIZATION_LEVEL = 3
        else:
            raise Exception("Error: Unsupported CLAUDE3.5 model")

    else:
        raise Exception("Error: Unknown CLAUDE model")
    
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_VERSION="2023-06-01"
    KEY_HEADER_TEXT = "x-api-key"
    KEY_HEADER_VALUE = ANTHROPIC_API_KEY
    API_URL="https://api.anthropic.com/v1/messages"

elif "XAI+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    XAI_API_KEY = os.getenv('XAI_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + XAI_API_KEY
    API_URL="https://api.x.ai/v1/chat/completions"

elif "GROQ+" in CLOUD_TYPE:
    MAX_TOKENS = 8000
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GROQ_API_KEY
    API_URL="https://api.groq.com/openai/v1/chat/completions"

elif "PERPLEXITY+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + PERPLEXITY_API_KEY
    API_URL="https://api.perplexity.ai/chat/completions"

elif "MLX+" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1] # not used
    API_URL="http://localhost:8080/v1/chat/completions"
    
else:
    raise Exception("Error: Unknown CLOUD_TYPE")


# only used for action = image, image_n

CLOUD_TYPE_IMAGE = ''

# Azure
# CLOUD_TYPE_IMAGE = 'AZURE+dall-e-3'                # best

# OpenAI
# CLOUD_TYPE_IMAGE = 'OPENAI+dall-e-3'               # best

# StabilityAI
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large'       # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large-turbo' # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-medium'      # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large'         # good
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large-turbo'   # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-medium'        # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+core'              # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+ultra'             # good

# VertexAI
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-generate-001'      # best
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-fast-generate-001' # better

# MLX
# CLOUD_TYPE_IMAGE = 'MLX+flux1'                     # best, local generation, MacOS w/ Apple Silicon only
CLOUD_TYPE_IMAGE = 'MLX+flux1-4bit'                # best, local generation, MacOS w/ Apple Silicon only
# CLOUD_TYPE_IMAGE = 'MLX+sd3'                       # ok, local generation, MacOS w/ Apple Silicon only

# IdeogramAI
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2'                # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2_TURBO'          # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_1'                # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_1_TURBO'          # best

# Black Forrest Labs
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1-ultra'        # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1'              # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro'                  # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-dev'                  # best

RESIZE_IMAGE = False
RESIZE_IMAGE_WIDTH = 1024  # source size is 1024
RESIZE_IMAGE_HEIGHT = 1024 # source size is 1024
INSERT_IMAGE_AS_BACKGROUND = True
OPTIMIZE_PROMPT_IMAGE = False # use a LLM call to optimize the prompt

if "AZURE+" in CLOUD_TYPE_IMAGE or "OPENAI+" in CLOUD_TYPE_IMAGE:
    IMAGE_EXPLICIT_STYLE = "digital art"
    IMAGE_QUALITY = "hd"  # hd, standard
    IMAGE_STYLE = "vivid" # natural, vivid

    if "AZURE+" in CLOUD_TYPE_IMAGE:
        OPENAI_API_KEY_IMAGE = os.getenv('OPENAI2_API_KEY')
        OPENAI_API_VERSION_IMAGE = '2024-02-01'
        OPENAI_DEPLOYMENT_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
        OPENAI_MODEL_IMAGE = ""
        OPENAI_IMAGE_API_URL = os.getenv('OPENAI2_API_BASE')

        IMAGE_API_URL = f"{OPENAI_IMAGE_API_URL}openai/deployments/{OPENAI_DEPLOYMENT_IMAGE}/images/generations?api-version={OPENAI_API_VERSION_IMAGE}"
        IMAGE_KEY_HEADER_TEXT = "api-key"
        IMAGE_KEY_HEADER_VALUE = OPENAI_API_KEY_IMAGE

    elif "OPENAI+" in CLOUD_TYPE_IMAGE:
        OPENAI_API_KEY_IMAGE = os.getenv('OPENAI_API_KEY_NATIVE')
        OPENAI_API_VERSION_IMAGE = ""
        OPENAI_DEPLOYMENT_IMAGE = ""
        OPENAI_MODEL_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
        OPENAI_IMAGE_API_URL = "https://api.openai.com/v1/images/generations"

        IMAGE_API_URL = OPENAI_IMAGE_API_URL
        IMAGE_KEY_HEADER_TEXT = "Authorization"
        IMAGE_KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY_IMAGE

elif "STABILITYAI+" in CLOUD_TYPE_IMAGE:
    IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]

    MODEL_ENDPOINT = IMAGE_MODEL_ID.split("-")[0]
    MODEL_ENDPOINT = "sd3" if MODEL_ENDPOINT == "sd3.5" else MODEL_ENDPOINT

    # 3d-model analog-film anime cinematic comic-book digital-art 
    # enhance fantasy-art isometric line-art low-poly modeling-compound 
    # neon-punk origami photographic pixel-art tile-texture
    IMAGE_STYLE_PRESET = "digital-art"
    IMAGE_EXPLICIT_STYLE = IMAGE_STYLE_PRESET if MODEL_ENDPOINT != "core" else ""

    IMAGE_OUTPUT_FORMAT = "png"         # png, jpeg, webp
    IMAGE_ASPECT_RATIO = "1:1"   # 16:9 1:1 21:9 2:3 3:2 4:5 5:4 9:16 9:21
    IMAGE_SEED = 0 # Stable Diffusion images are generated deterministically based on the seed value (stored in the filename)

    IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"

    STABILITYAI_API_KEY = os.getenv('STABILITYAI_API_KEY')
    IMAGE_API_URL = f"https://api.stability.ai/v2beta/stable-image/generate/{MODEL_ENDPOINT}"

elif "VERTEXAI+" in CLOUD_TYPE_IMAGE:
    IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
    IMAGE_ASPECT_RATIO = "1:1" # 1:1 (1024x1024) 9:16 (768x1408) 16:9 (1408x768) 3:4 (896x1280) 4:3 (1280x896)

    IMAGE_EXPLICIT_STYLE = "digital art"
    IMAGE_ADD_WATERMARK = False

    IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"

    IMAGE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
    IMAGE_API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
    IMAGE_LOCATION_ID = "us-central1"

    IMAGE_KEY_HEADER_TEXT = "Authorization"

    GCP_CLIENT_ID_IMAGE = os.getenv('GCP_CLIENT_ID')
    GCP_CLIENT_SECRET_IMAGE = os.getenv('GCP_CLIENT_SECRET')

    IMAGE_API_URL = f"https://{IMAGE_API_ENDPOINT}/v1/projects/{IMAGE_PROJECT_ID}/locations/{IMAGE_LOCATION_ID}/publishers/google/models/{IMAGE_MODEL_ID}:predict"

elif "MLX+" in CLOUD_TYPE_IMAGE:
    IMAGE_SEED = 0
    #https://enragedantelope.github.io/Styles-FluxDev/
    IMAGE_EXPLICIT_STYLE = "photorealistic 3D art"
    #IMAGE_EXPLICIT_STYLE = "papercraft-kirigami art"
    #IMAGE_EXPLICIT_STYLE = "computer collage art"
    IMAGE_NEGATIV_PROMPT = ""

    IMAGE_HEIGHT = 768 # 1024 # 512 # 768
    IMAGE_WIDTH = 768 # 1024 # 512 # 768

    DIFF_MODEL = "argmaxinc/stable-diffusion"

    IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
    if IMAGE_MODEL_ID == "flux1" or IMAGE_MODEL_ID == "flux1-4bit":
        if IMAGE_MODEL_ID == "flux1":
            DIFF_MODEL_VERSION = "argmaxinc/mlx-FLUX.1-schnell"
            DIFF_LOW_MEMORY_MODE = True
            DIFF_A16 = True
            DIFF_W16 = True
            IMAGE_NUM_STEPS = 4
            IMAGE_CFG_WEIGHT = 0. 
            DIFF_SHIFT = 1.0
            DIFF_USE_T5 = True
        elif IMAGE_MODEL_ID == "flux1-4bit":
            DIFF_MODEL_VERSION = "argmaxinc/mlx-FLUX.1-schnell-4bit-quantized"
            DIFF_LOW_MEMORY_MODE = True
            DIFF_A16 = True
            DIFF_W16 = True
            IMAGE_NUM_STEPS = 4
            IMAGE_CFG_WEIGHT = 0. 
            DIFF_SHIFT = 1.0
            DIFF_USE_T5 = True
        else:
            raise Exception("Error: Unknown MLX image model")

    elif IMAGE_MODEL_ID == "sd3":
        DIFF_MODEL_VERSION = "argmaxinc/mlx-stable-diffusion-3-medium"
        DIFF_LOW_MEMORY_MODE = True  # models offloading
        DIFF_A16 = True
        DIFF_W16 = True
        IMAGE_NUM_STEPS = 50         # Number of diffusion steps
        IMAGE_CFG_WEIGHT = 5. 
        DIFF_SHIFT = 3.0             # Shift for diffusion sampling
        DIFF_USE_T5 = False          # Engages T5 for stronger text embeddings (uses significantly more memory)
    else:
        raise Exception("Error: Unknown MLX image model")
    
elif "IDEOGRAMAI+" in CLOUD_TYPE_IMAGE:
    IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
    if IMAGE_MODEL_ID == "V_2" or IMAGE_MODEL_ID == "V_2_TURBO":
        IMAGE_STYLE_PRESET = "GENERAL" # DESIGN, GENERAL, REALISTIC, RENDER_3D, ANIME
        IMAGE_EXPLICIT_STYLE = IMAGE_STYLE_PRESET
    else:
        IMAGE_EXPLICIT_STYLE = "computer collage art"

    IMAGE_OUTPUT_FORMAT = "png"
    IMAGE_SEED = 0

    IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"

    IMAGE_HEIGHT = 1024
    IMAGE_WIDTH = 1024
    IMAGE_RESOLUTION = f"RESOLUTION_{IMAGE_WIDTH}_{IMAGE_HEIGHT}"

    IMAGE_KEY_HEADER_TEXT = "Api-Key"
    IMAGE_KEY_HEADER_VALUE = os.getenv('IDEOGRAMAI_API_KEY')
    IMAGE_API_URL = f"https://api.ideogram.ai/generate"

elif "BFL+" in CLOUD_TYPE_IMAGE:
    IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
    IMAGE_EXPLICIT_STYLE = "computer collage art"

    IMAGE_OUTPUT_FORMAT = "png" # png, jpeg
    IMAGE_SEED = 0
    IMAGE_SAFETY_TOLERANCE = 6 # 0-6, 6 least strict

    if IMAGE_MODEL_ID == "flux-pro-1.1-ultra":
        IMAGE_RAW = False
        IMAGE_ASPECT_RATIO = "4:3" # between 21:9 and 9:21

    elif IMAGE_MODEL_ID == "flux-pro-1.1":
        IMAGE_HEIGHT = 1024
        IMAGE_WIDTH = 1024
        IMAGE_PROMPT_UPSAMPLING = False

    elif IMAGE_MODEL_ID == "flux-pro":
        IMAGE_HEIGHT = 1024
        IMAGE_WIDTH = 1024
        IMAGE_STEPS = 28
        IMAGE_INTERVAL = 2
        IMAGE_PROMPT_UPSAMPLING = False
        IMAGE_GUIDANCE = 3

    elif IMAGE_MODEL_ID == "flux-dev":
        IMAGE_HEIGHT = 1024
        IMAGE_WIDTH = 1024
        IMAGE_STEPS = 28
        IMAGE_PROMPT_UPSAMPLING = False
        IMAGE_GUIDANCE = 3

    else:
        raise Exception("Error: Unknown Flux image model")
 
    IMAGE_KEY_HEADER_TEXT = "x-key"
    IMAGE_KEY_HEADER_VALUE = os.getenv('BFL_API_KEY')
    IMAGE_API_URL = f"https://api.bfl.ml/v1/"


# only used for action = DEEPL (translation)


CLOUD_TYPE_TRANSLATION = 'DEEPL'

if "DEEPL" in CLOUD_TYPE_TRANSLATION:
    DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
    #DEEPL_BASE_URL = "https://api.deepl.com/v2/translate"
    DEEPL_BASE_URL = "https://api-free.deepl.com/v2/translate"
    KEY_HEADER_TEXT_TRANSLATION = "Authorization"
    KEY_HEADER_VALUE_TRANSLATION = "DeepL-Auth-Key " + DEEPL_API_KEY
