import os

LOG = True # write source mindmaps, destination mindmaps and prompts to file

SYSTEM_PROMPT = "You are a business consultant and helpful assistant."



# ChatGPT, best in class
CLOUD_TYPE = 'AZURE'                           # best,        uncensored(?)
# CLOUD_TYPE = 'OPENAI'                          # best,        uncensored(?)

# Ollama (local models), best results
# CLOUD_TYPE = 'OLLAMA+mixtral'                  # best,        censored
# CLOUD_TYPE = 'OLLAMA+solar'                    # best,        uncensored
# CLOUD_TYPE = 'OLLAMA+mistral'                  # best,        uncensored
# CLOUD_TYPE = 'OLLAMA+openchat'                 # very good,   uncensored
# CLOUD_TYPE = 'OLLAMA+zephyr'                   # very good,   uncensored *
# CLOUD_TYPE = 'OLLAMA+neural-chat'              # good,        uncensored

# Ollama (local models), not working
# CLOUD_TYPE = 'OLLAMA+mistral-openorca'         # bad,         uncensored
# CLOUD_TYPE = 'OLLAMA+phi'                      # not working
# CLOUD_TYPE = 'OLLAMA+llama2'                   # not working
# CLOUD_TYPE = 'OLLAMA+llama2-uncensored'        # not working
# CLOUD_TYPE = 'OLLAMA+wizard-vicuna-uncensored' # not working
# CLOUD_TYPE = 'OLLAMA+yi'                       # not working

# Google Gemini
# CLOUD_TYPE = 'GEMINI'                          # ok
# CLOUD_TYPE = 'GEMINIPROJECT'                   #

# Claude3 (use US VPN)
# CLOUD_TYPE = 'CLAUDE3_OPUS'                    # ok
# CLOUD_TYPE = 'CLAUDE3_SONNET'                  # ok
# CLOUD_TYPE = 'CLAUDE3_HAIKU'                   # ok

# groq
# CLOUD_TYPE = 'GROQ+mixtral'                    # best

# Perplexity
# CLOUD_TYPE = 'PERPLEXITY+mistral'              # ok



LLM_TEMPERATURE = float('0.5')

MAX_TOKENS = int('4000')
MAX_RETRIES = int('3')
TOP_MOST_RESULTS = int('5')
MAX_RETURN_WORDS = int('5')
LEVELS_DEEP = int('5')

INDENT_SIZE = int('2')
LINE_SEPARATOR = "\n"

if CLOUD_TYPE == "OPENAI":
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_NATIVE')
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    OPENAI_MODEL = "gpt-4" # only for OPENAI relevant
    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY

elif CLOUD_TYPE == "AZURE":
    OPENAI_API_KEY = os.getenv('OPENAI2_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI2_API_BASE')
    OPENAI_DEPLOYMENT = os.getenv('OPENAI2_DEPLOYMENT')
    OPENAI_API_VERSION = os.getenv('OPENAI2_API_VERSION')

    OPENAI_MODEL = ""
    API_URL = f"{OPENAI_API_URL}openai/deployments/{OPENAI_DEPLOYMENT}/chat/completions?api-version={OPENAI_API_VERSION}"
    KEY_HEADER_TEXT = "api-key"
    KEY_HEADER_VALUE = OPENAI_API_KEY

elif CLOUD_TYPE == "GEMINI":
    MODEL_ID = "gemini-1.5-pro-latest" # "gemini-1.0-pro|gemini-1.0-pro-vision|gemini-1.5-pro-latest"
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY_AI')

    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GOOGLE_API_KEY}"
    KEY_HEADER_TEXT = ""
    KEY_HEADER_VALUE = ""

elif CLOUD_TYPE == "GEMINIPROJECT":
    # cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal
    # Service Account / Key -> Create new key -> JSON
    # gcloud auth activate-service-account --key-file=<path/to/your/keyfile.json>
    # gcloud auth print-access-token
    MODEL_ID = "gemini-1.5-pro-latest" # "gemini-1.0-pro|gemini-1.0-pro-vision|gemini-1.5-pro-latest"
    PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
    API_ENDPOINT="us-central1-aiplatform.googleapis.com"
    LOCATION_ID="us-central1"
    GOOGLE_ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN_AI') # limited time use

    API_URL = f"https://{API_ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{MODEL_ID}:streamGenerateContent"
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GOOGLE_ACCESS_TOKEN

elif "OLLAMA" in CLOUD_TYPE:
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    API_URL="http://localhost:11434/api/generate"

elif "CLAUDE3" in CLOUD_TYPE:
    model=CLOUD_TYPE.split("_")[-1]
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
    model = CLOUD_TYPE.split("+")[-1]
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GROQ_API_KEY
    API_URL="https://api.groq.com/openai/v1/chat/completions"
    if model == "mixtral":
        MODEL_NAME = "Mixtral-8x7b-Instruct-v0.1"
        MODEL_ID = "mixtral-8x7b-32768"
    else:
        raise Exception("Error: Unknown groq model")

elif "PERPLEXITY" in CLOUD_TYPE:
    model = CLOUD_TYPE.split("+")[-1]
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + PERPLEXITY_API_KEY
    API_URL="https://api.perplexity.ai/chat/completions"
    if model == "mistral":
        MODEL_ID = "mistral-7b-instruct"
    else:
        raise Exception("Error: Unknown Perplexity model")

else:
    raise Exception("Error: Unknown CLOUD_TYPE")