import os

CLOUD_TYPE = 'AZURE'  # 'AZURE/OPENAI'
OPENAI_MODEL = "gpt-4" # only for OPENAI relevant
OPENAI_TEMPERATURE = float('0.3')

MAX_TOKENS_SIMPLE = int('100')
MAX_TOKENS_NORMAL = int('1000')
MAX_TOKENS_DEEP = int('4000')
TOP_MOST_RESULTS = int('3')
TOP_MOST_RESULTS_DEEP = int('6')
MAX_RETURN_WORDS = int('5')
LEVELS_DEEP = int('5')

if CLOUD_TYPE == "OPENAI":
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_NATIVE')
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " & OPENAI_API_KEY
else:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI_API_BASE')
    OPENAI_DEPLOYMENT = os.getenv('OPENAI_DEPLOYMENT')
    OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION')

    API_URL = OPENAI_API_URL + "openai/deployments/" + OPENAI_DEPLOYMENT + "/chat/completions?api-version=" + OPENAI_API_VERSION
    KEY_HEADER_TEXT = "api-key"
    KEY_HEADER_VALUE = OPENAI_API_KEY