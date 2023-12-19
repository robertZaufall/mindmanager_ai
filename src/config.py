import os

LOG = True # write source mindmaps, destination mindmaps and prompts to file

SYSTEM_PROMPT = "You are a business consultant and helpful assistant."

CLOUD_TYPE = 'AZURE' 
# CLOUD_TYPE = 'OPENAI'
# CLOUD_TYPE = 'GEMINI'
# CLOUD_TYPE = 'GEMINIPROJECT'
# CLOUD_TYPE = 'OLLAMA+llama2'
# CLOUD_TYPE = 'OLLAMA+mistral'
# CLOUD_TYPE = 'OLLAMA+mistral-openorca'
# CLOUD_TYPE = 'OLLAMA+neural-chat'
# CLOUD_TYPE = 'OLLAMA+zephyr'
# CLOUD_TYPE = 'OLLAMA+openchat'

LLM_TEMPERATURE = float('0.3')

MAX_TOKENS_SIMPLE = int('100')
MAX_TOKENS_NORMAL = int('1000')
MAX_TOKENS_DEEP = int('4000')
TOP_MOST_RESULTS = int('5')
TOP_MOST_RESULTS_DEEP = int('6')
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
    MODEL_ID = "gemini-pro" # "gemini-pro|gemini-pro-vision"
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY_AI')

    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GOOGLE_API_KEY}"
    KEY_HEADER_TEXT = ""
    KEY_HEADER_VALUE = ""

elif CLOUD_TYPE == "GEMINIPROJECT":
    MODEL_ID = "gemini-pro" # "gemini-pro|gemini-pro-vision"
    PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
    API_ENDPOINT="us-central1-aiplatform.googleapis.com"
    LOCATION_ID="us-central1"
    GOOGLE_ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN_AI')

    API_URL = f"https://{API_ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{MODEL_ID}:streamGenerateContent"
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GOOGLE_ACCESS_TOKEN

elif "OLLAMA" in CLOUD_TYPE:
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    API_URL="http://localhost:11434/api/generate"

else:
    raise Exception("Error: Unknown CLOUD_TYPE")