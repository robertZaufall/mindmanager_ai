import os

LOG = True # write source mindmaps, destination mindmaps and prompts to file

SYSTEM_PROMPT = "You are a business consultant and helpful assistant."



# Azure serverless models, !use your model deployment name, ie. gpt-4o!
CLOUD_TYPE = 'AZURE+gpt-4o'                    # best
# CLOUD_TYPE = 'AZURE+gpt-4'                     # best
# CLOUD_TYPE = 'AZURE+gpt-4-32k'                 # best
# CLOUD_TYPE = 'AZURE+gpt-35'                    # best

# OpenAI
# CLOUD_TYPE = 'OPENAI+gpt-4o'                   # best
# CLOUD_TYPE = 'OPENAI+gpt-4-turbo'              # best
# CLOUD_TYPE = 'OPENAI+gpt-3.5-turbo'            # best

# Ollama (local models), best results
# CLOUD_TYPE = 'OLLAMA+mixtral'                  # best,        censored
# CLOUD_TYPE = 'OLLAMA+solar'                    # best,        uncensored
# CLOUD_TYPE = 'OLLAMA+mistral'                  # best,        uncensored
# CLOUD_TYPE = 'OLLAMA+openchat'                 # very good,   uncensored
# CLOUD_TYPE = 'OLLAMA+zephyr'                   # very good,   uncensored *
# CLOUD_TYPE = 'OLLAMA+neural-chat'              # good,        uncensored
# CLOUD_TYPE = 'OLLAMA+wizardlm2'                # very good,   uncensored (with warnings)
# CLOUD_TYPE = 'OLLAMA+llama3'                   # good,        uncensored
# CLOUD_TYPE = 'OLLAMA+llama3:70b'               # good,        censored, slow
# CLOUD_TYPE = 'OLLAMA+phi3'                     # good,        censored
# CLOUD_TYPE = 'OLLAMA+qwen2'                    # ok,          censored

# Google Gemini
# CLOUD_TYPE = 'GEMINI_PRO'                      # good
# CLOUD_TYPE = 'GEMINI_FLASH'                    # one-shot ok, generates maps only 3 levels deep

# Google Gemini Vertex AI (needs pre-authentication ie. token)
# CLOUD_TYPE = 'GEMINIPROJECT_PRO'               # good, Vertex AI need pre-authentication
# CLOUD_TYPE = 'GEMINIPROJECT_FLASH'             # one-shot ok, generates maps only 3 levels deep

# Claude3
# CLOUD_TYPE = 'CLAUDE3_OPUS'                    # good
# CLOUD_TYPE = 'CLAUDE3_SONNET'                  # good
# CLOUD_TYPE = 'CLAUDE3_HAIKU'                   # good

# groq
# CLOUD_TYPE = 'GROQ+mixtral-8x7b-32768'         # good
# CLOUD_TYPE = 'GROQ+llama3-8b-8192'             # reduced usability
# CLOUD_TYPE = 'GROQ+llama3-70b-8192'            # good
# CLOUD_TYPE = 'GROQ+gemma-7b-it'                # good

# Perplexity
# CLOUD_TYPE = 'PERPLEXITY+llama-3-8b-instruct'            # ok
# CLOUD_TYPE = 'PERPLEXITY+llama-3-70b-instruct'           # good
# CLOUD_TYPE = 'PERPLEXITY+llama-3-sonar-small-32k-chat'   # ok
# CLOUD_TYPE = 'PERPLEXITY+llama-3-sonar-large-32k-chat'   # good
# CLOUD_TYPE = 'PERPLEXITY+llama-3-sonar-small-32k-online' # reduced usability
# CLOUD_TYPE = 'PERPLEXITY+llama-3-sonar-large-32k-online' # good

# MLX server, macOS only (pip install mlx-lm)
# python -m mlx_lm.server --model mlx-community/Meta-Llama-3-8B-Instruct-4bit --port 8080 --log-level DEBUG
# CLOUD_TYPE = 'MLX+llama3-8b'                             # good

USE_AZURE_ENTRA = False
USE_GCP_OA2 = False

LLM_TEMPERATURE = float('0.5')

MAX_TOKENS = int('4000')
MAX_RETRIES = int('3')
TOP_MOST_RESULTS = int('5')
MAX_RETURN_WORDS = int('5')
LEVELS_DEEP = int('5')

INDENT_SIZE = int('2')
LINE_SEPARATOR = "\n"
OPENAI_COMPATIBILITY = False

if "OPENAI" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_NATIVE')
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    OPENAI_MODEL = CLOUD_TYPE.split("+")[-1]
    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY

elif "AZURE" in CLOUD_TYPE:
    OPENAI_DEPLOYMENT = CLOUD_TYPE.split("+")[-1]
    OPENAI_COMPATIBILITY = True
    OPENAI_API_KEY = os.getenv('OPENAI2_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI2_API_BASE')
    OPENAI_API_VERSION = os.getenv('OPENAI2_API_VERSION')

    OPENAI_MODEL = ""
    API_URL = f"{OPENAI_API_URL}openai/deployments/{OPENAI_DEPLOYMENT}/chat/completions?api-version={OPENAI_API_VERSION}"
    KEY_HEADER_TEXT = "api-key"
    KEY_HEADER_VALUE = OPENAI_API_KEY

elif "GEMINI" in CLOUD_TYPE:
    system = CLOUD_TYPE.split("_")[0]
    if system == "GEMINI":
        model = CLOUD_TYPE.split("_")[-1]
        if model == "PRO":
            MODEL_ID = "gemini-1.5-pro-latest"
        elif model == "FLASH":
            MODEL_ID = "gemini-1.5-flash-latest"
        else:
            raise Exception("Error: Unknown GEMINI model")

        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY_AI')
        API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GOOGLE_API_KEY}"
        KEY_HEADER_TEXT = ""
        KEY_HEADER_VALUE = ""
    elif system == "GEMINIPROJECT":
        # cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal
        # -> open console
        # gcloud auth print-access-token
        # (Service Account / Key -> Create new key -> JSON)
        # (gcloud auth activate-service-account --key-file=<path/to/your/keyfile.json>)
        model = CLOUD_TYPE.split("_")[-1]
        if model == "PRO":
            MODEL_ID = "gemini-1.5-pro-preview-0514"
        elif model == "FLASH":
            MODEL_ID = "gemini-1.5-flash-preview-0514"
        else:
            raise Exception("Error: Unknown GEMINI model")

        PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
        API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
        LOCATION_ID = "us-central1"
        GOOGLE_ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN_AI') # limited time use
        API_URL = f"https://{API_ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{MODEL_ID}:generateContent"
        KEY_HEADER_TEXT = "Authorization"
        KEY_HEADER_VALUE = "Bearer " + GOOGLE_ACCESS_TOKEN
    else:
        raise Exception("Error: Unknown GEMINI system")

elif "OLLAMA" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    if OPENAI_COMPATIBILITY:
        API_URL="http://localhost:11434/v1/chat/completions"
    else: 
        API_URL="http://localhost:11434/api/generate"

elif "CLAUDE3" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    model = CLOUD_TYPE.split("_")[-1]
    if model == "HAIKU":
        MODEL_ID = "claude-3-haiku-20240307"
    elif model == "SONNET":
        MODEL_ID = "claude-3-sonnet-20240229"
    elif model == "OPUS":
        MODEL_ID = "claude-3-opus-20240229"
    else:
        raise Exception("Error: Unknown CLAUDE3 model")
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_VERSION="2023-06-01"
    KEY_HEADER_TEXT = "x-api-key"
    KEY_HEADER_VALUE = ANTHROPIC_API_KEY
    API_URL="https://api.anthropic.com/v1/messages"

elif "GROQ" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GROQ_API_KEY
    API_URL="https://api.groq.com/openai/v1/chat/completions"

elif "PERPLEXITY" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + PERPLEXITY_API_KEY
    API_URL="https://api.perplexity.ai/chat/completions"

elif "MLX" in CLOUD_TYPE:
    OPENAI_COMPATIBILITY = True
    MODEL_ID = CLOUD_TYPE.split("+")[-1] # not used, depends on how the server was started
    API_URL="http://localhost:8080/v1/chat/completions"
    
else:
    raise Exception("Error: Unknown CLOUD_TYPE")


# only used for action = image


# CLOUD_TYPE_IMAGE = ''
CLOUD_TYPE_IMAGE = 'AZURE+dall-e-3'              # better
# CLOUD_TYPE_IMAGE = 'OPENAI+dall-e-3'             # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-medium'      # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large'       # good
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large-turbo' # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+core'            # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+ultra'           # good
# CLOUD_TYPE_IMAGE = 'GOOGLEPROJECT+IMAGEN2-6'     # not so good

RESIZE_IMAGE = False
RESIZE_IMAGE_WIDTH = 800  # source size is 1024
RESIZE_IMAGE_HEIGHT = 800 # source size is 1024
INSERT_IMAGE_AS_BACKGROUND = True

if "AZURE" in CLOUD_TYPE_IMAGE or "OPENAI" in CLOUD_TYPE_IMAGE:
    EXPLICIT_STYLE = "digital art"
    IMAGE_QUALITY = "hd"  # hd, standard
    IMAGE_STYLE = "vivid" # natural, vivid

    if "AZURE" in CLOUD_TYPE_IMAGE:
        OPENAI_API_KEY_IMAGE = os.getenv('OPENAI2_API_KEY')
        OPENAI_API_VERSION_IMAGE = '2024-02-01'
        OPENAI_DEPLOYMENT_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
        OPENAI_MODEL_IMAGE = ""
        OPENAI_API_URL_IMAGE = os.getenv('OPENAI2_API_BASE')

        API_URL_IMAGE = f"{OPENAI_API_URL_IMAGE}openai/deployments/{OPENAI_DEPLOYMENT_IMAGE}/images/generations?api-version={OPENAI_API_VERSION_IMAGE}"
        KEY_HEADER_TEXT_IMAGE = "api-key"
        KEY_HEADER_VALUE_IMAGE = OPENAI_API_KEY_IMAGE

    elif "OPENAI" in CLOUD_TYPE_IMAGE:
        OPENAI_API_KEY_IMAGE = os.getenv('OPENAI_API_KEY_NATIVE')
        OPENAI_API_VERSION_IMAGE = ""
        OPENAI_DEPLOYMENT_IMAGE = ""
        OPENAI_MODEL_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
        OPENAI_API_URL_IMAGE = "https://api.openai.com/v1/images/generations"

        API_URL_IMAGE = OPENAI_API_URL_IMAGE
        KEY_HEADER_TEXT_IMAGE = "Authorization"
        KEY_HEADER_VALUE_IMAGE = "Bearer " + OPENAI_API_KEY_IMAGE

elif "STABILITYAI" in CLOUD_TYPE_IMAGE:
    MODEL_ID_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
    MODEL_ENDPOINT = MODEL_ID_IMAGE.split("-")[0]

    # 3d-model analog-film anime cinematic comic-book digital-art 
    # enhance fantasy-art isometric line-art low-poly modeling-compound 
    # neon-punk origami photographic pixel-art tile-texture
    STYLE_PRESET = "digital-art"
    EXPLICIT_STYLE = STYLE_PRESET if MODEL_ENDPOINT != "core" else ""

    OUTPUT_FORMAT_IMAGE = "png"         # png, jpeg, webp
    OUTPUT_ASPECT_RATIO_IMAGE = "1:1"   # 16:9 1:1 21:9 2:3 3:2 4:5 5:4 9:16 9:21
    SEED_IMAGE = 0 # Stable Diffusion images are generated deterministically based on the seed value (stored in the filename)

    NEGATIV_PROMPT_IMAGE = "text, characters, letters, words, labels"

    STABILITYAI_API_KEY = os.getenv('STABILITYAI_API_KEY')
    API_URL_IMAGE = f"https://api.stability.ai/v2beta/stable-image/generate/{MODEL_ENDPOINT}"

elif "GOOGLEPROJECT" in CLOUD_TYPE_IMAGE:
    # cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal
    # -> open console
    # gcloud auth print-access-token
    # (Service Account / Key -> Create new key -> JSON)
    # (gcloud auth activate-service-account --key-file=<path/to/your/keyfile.json>)
    model = CLOUD_TYPE_IMAGE.split("+")[-1]
    if model == "IMAGEN2-6":
        MODEL_ID_IMAGE = "imagegeneration@006"
    else:
        raise Exception("Error: Unknown GOOGLE image model")

    EXPLICIT_STYLE = "digital art"
    OUTPUT_ASPECT_RATIO_IMAGE = "1:1" # 1:1 (1536x1536) 9:16 (1152x2016) 16:9 (2016x1134) 3:4 (1344x1792) 4:3 (1792x1344)
    ADD_WATERMARK = False

    NEGATIV_PROMPT_IMAGE = "text, characters, letters, words, labels"

    PROJECT_ID_IMAGE = os.getenv('GOOGLE_PROJECT_ID_AI')
    API_ENDPOINT_IMAGE = "us-central1-aiplatform.googleapis.com"
    LOCATION_ID_IMAGE = "us-central1"
    GOOGLE_ACCESS_TOKEN_IMAGE = os.getenv('GOOGLE_ACCESS_TOKEN_AI') # limited time use
    API_URL_IMAGE = f"https://{API_ENDPOINT_IMAGE}/v1/projects/{PROJECT_ID_IMAGE}/locations/{LOCATION_ID_IMAGE}/publishers/google/models/{MODEL_ID_IMAGE}:predict"
    
    KEY_HEADER_TEXT_IMAGE = "Authorization"
    KEY_HEADER_VALUE_IMAGE = "Bearer " + GOOGLE_ACCESS_TOKEN_IMAGE


CLOUD_TYPE_TRANSLATION = 'DEEPL'

if "DEEPL" in CLOUD_TYPE_TRANSLATION:
    DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
    #DEEPL_BASE_URL = "https://api.deepl.com/v2/translate"
    DEEPL_BASE_URL = "https://api-free.deepl.com/v2/translate"

    KEY_HEADER_TEXT_TRANSLATION = "Authorization"
    KEY_HEADER_VALUE_TRANSLATION = "DeepL-Auth-Key " + DEEPL_API_KEY
