import os
from dataclasses import dataclass, field
from typing import List, Optional

LOG = True # write source mindmaps, destination mindmaps and prompts to file

# Azure serverless models, !use your model deployment name, ie. gpt-4o!
# CLOUD_TYPE = 'AZURE+gpt-4o'                                           # best
CLOUD_TYPE = 'AZURE+gpt-4o-mini'                                      # ok
# CLOUD_TYPE = 'AZURE+gpt-4'                                            # best
# CLOUD_TYPE = 'AZURE+gpt-4-32k'                                        # best

# Azure serverless     
# CLOUD_TYPE = 'AZURE_META+LLAMA3170B'                                  # best, slow
# CLOUD_TYPE = 'AZURE_Microsoft+PHI35MINIINSTRUCT'                      # good

# OpenAI     
# CLOUD_TYPE = 'OPENAI+gpt-4o-2024-11-20'                               # best
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini'                                     # ok
# CLOUD_TYPE = 'OPENAI+gpt-4-turbo'                                     # best
# CLOUD_TYPE = 'OPENAI+o1'                                              # not available by now
# CLOUD_TYPE = 'OPENAI+o1-preview'                                      # best
# CLOUD_TYPE = 'OPENAI+o1-mini'                                         # best

# Github Models
# CLOUD_TYPE = 'GITHUB+gpt-4o'                                          # best
# CLOUD_TYPE = 'GITHUB+gpt-4o-mini'                                     # ok
# CLOUD_TYPE = "GITHUB+Phi-3-medium-128k-instruct"                      # not so good
# CLOUD_TYPE = "GITHUB+Phi-3.5-mini-instruct"                           # ok
# CLOUD_TYPE = "GITHUB+meta-llama-3.1-70b-instruct"                     # best
# CLOUD_TYPE = "GITHUB+Mistral-large-2407"                              # good
# CLOUD_TYPE = "GITHUB+AI21-Jamba-Instruct"                             # best

# Anthropic     
# CLOUD_TYPE = 'ANTHROPIC+claude-3-5-sonnet-20241022'                   # best
# CLOUD_TYPE = 'ANTHROPIC+claude-3-5-haiku-20241022'                    # best
# CLOUD_TYPE = 'ANTHROPIC+claude-3-opus-20240229'                       # good
# CLOUD_TYPE = 'ANTHROPIC+claude-3-haiku-20240307'                      # ok

# Google Gemini
# CLOUD_TYPE = 'GEMINI+gemini-exp-1206'                                 # best in class
# CLOUD_TYPE = 'GEMINI+gemini-exp-1121'                                 # best in class
# CLOUD_TYPE = 'GEMINI+gemini-1.5-pro-latest'                           # best in class
# CLOUD_TYPE = 'GEMINI+gemini-1.5-flash-latest'                         # good
# CLOUD_TYPE = 'GEMINI+gemini-1.5-flash-8b-latest'                      # better
# CLOUD_TYPE = 'GEMINI+gemini-2.0-flash-exp'                            # best in class
# CLOUD_TYPE = 'GEMINI+gemini-2.0-flash-thinking-exp-1219'              # response not compatible

# Google Gemini Vertex AI (OAuth2)     
# CLOUD_TYPE = 'VERTEXAI+gemini-1.5-pro-002'                            # good (frequent 'recitation' errors)
# CLOUD_TYPE = 'VERTEXAI+gemini-1.5-flash-002'                          # good
# CLOUD_TYPE = 'VERTEXAI+gemini-pro-experimental'                       # best, does not come to an end every time
# CLOUD_TYPE = 'VERTEXAI+gemini-flash-experimental'                     # good
# CLOUD_TYPE = 'VERTEXAI+gemini-2.0-flash-exp'                          # best in class

# AWS Bedrock
# CLOUD_TYPE = 'BEDROCK+amazon.nova-pro-v1:0'                           # best, max token output only 5120
# CLOUD_TYPE = 'BEDROCK+amazon.nova-lite-v1:0'                          # best, max token output only 5120
# CLOUD_TYPE = 'BEDROCK+amazon.titan-text-premier-v1:0'                 # ok, max token output only 3000
# CLOUD_TYPE = 'BEDROCK+anthropic.claude-3-5-sonnet-20240620-v1:0'      # best
# CLOUD_TYPE = 'BEDROCK+mistral.mistral-large-2402-v1:0'                # ok

# xAI     
# CLOUD_TYPE = 'XAI+grok-beta'                                          # good
# CLOUD_TYPE = 'XAI+grok-vision-beta'                                   # best
# CLOUD_TYPE = 'XAI+grok-2-1212'                                        # best
# CLOUD_TYPE = 'XAI+grok-2-vision-1212'                                 # best

# DeepSeek
# CLOUD_TYPE = 'DEEPSEEK+deepseek-chat'                                 # best (V3!)

# Alibaba Cloud
# CLOUD_TYPE = 'ALIBABACLOUD+qwen-max'                                  # best, max token output only 2000
# CLOUD_TYPE = 'ALIBABACLOUD+qwen-turbo'                                # good, max token output only 1500
# CLOUD_TYPE = 'ALIBABACLOUD+qwen-plus'                                 # good, max token output only 1500

# Mistral AI
# CLOUD_TYPE = 'MISTRAL+mistral-large-latest'                           # best in class
# CLOUD_TYPE = 'MISTRAL+ministral-3b-latest'                            # ok
# CLOUD_TYPE = 'MISTRAL+ministral-8b-latest'                            # ok
# CLOUD_TYPE = 'MISTRAL+mistral-small-latest'                           # best
# CLOUD_TYPE = 'MISTRAL+pixtral-large-latest'                           # best
# CLOUD_TYPE = 'MISTRAL+pixtral-12b-2409'                               # good, free
# CLOUD_TYPE = 'MISTRAL+open-mistral-nemo'                              # not working, free

# groq     
# CLOUD_TYPE = 'GROQ+llama-3.3-70b-specdec'                             # best (6000 token per minute limit)
# CLOUD_TYPE = 'GROQ+llama-3.3-70b-versatile'                           # best (6000 token per minute limit)
# CLOUD_TYPE = 'GROQ+llama-3.1-8b-instant'                              # good
# CLOUD_TYPE = 'GROQ+gemma-7b-it'                                       # good
# CLOUD_TYPE = 'GROQ+gemma2-9b-it'                                      # ok, generates maps only 3 levels deep
# CLOUD_TYPE = 'GROQ+mixtral-8x7b-32768'                                # good (token limit 5000 per minute)

# Perplexity     
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-small-128k-online'           # good
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-large-128k-online'           # better, slow
# CLOUD_TYPE = 'PERPLEXITY+llama-3.1-sonar-huge-128k-online'            # best, slow

# Firekworks.ai
# CLOUD_TYPE = 'FIREWORKS+qwen-qwq-32b-preview'                         # does not work
# CLOUD_TYPE = 'FIREWORKS+qwen2p5-72b-instruct'                         # good
# CLOUD_TYPE = 'FIREWORKS+llama-v3p3-70b-instruct'                      # good

# Openrouter.ai
# CLOUD_TYPE = 'OPENROUTER+openai/o1-preview'                           # best
# CLOUD_TYPE = 'OPENROUTER+openai/o1-mini'                              # best
# CLOUD_TYPE = 'OPENROUTER+google/gemini-flash-1.5'                     # best
# CLOUD_TYPE = 'OPENROUTER+perplexity/llama-3.1-sonar-huge-128k-online' # good

# Hugging Face
# CLOUD_TYPE = 'HF+meta-llama/Meta-Llama-3-8B-Instruct'                 # good
# CLOUD_TYPE = 'HF+meta-llama/Llama-3.1-70B-Instruct'                   # needs pro-subscription
# CLOUD_TYPE = 'HF+meta-llama/Llama-3.1-8B-Instruct'                    # needs pro-subscription

# Ollama (local models), best results     
# CLOUD_TYPE = 'OLLAMA+wizardlm2'                                       # best
# CLOUD_TYPE = 'OLLAMA+llama3.1'                                        # ok
# CLOUD_TYPE = 'OLLAMA+llama3.2:3b'                                     # ok
# CLOUD_TYPE = 'OLLAMA+llama3.3:70b'                                    # best, slow
# CLOUD_TYPE = 'OLLAMA+mixtral'                                         # ok
# CLOUD_TYPE = 'OLLAMA+solar'                                           # ok
# CLOUD_TYPE = 'OLLAMA+qwen2.5'                                         # good
# CLOUD_TYPE = 'OLLAMA+qwen2.5:14b'                                     # good
# CLOUD_TYPE = 'OLLAMA+nemotron'                                        # best, slow

# LMStudio
# CLOUD_TYPE = 'LMSTUDIO+nvidia_llama-3.1-nemotron-70b-instruct-hf'     # best, slow
# CLOUD_TYPE = 'LMSTUDIO+lmstudio-community/meta-llama-3.1-8b-instruct' # ok
# CLOUD_TYPE = 'LMSTUDIO+mlx-community/meta-llama-3.1-8b-instruct'      # ok
# CLOUD_TYPE = 'LMSTUDIO+bartowski/llama-3.2-3b-instruct'               # ok
# CLOUD_TYPE = 'LMSTUDIO+qwen2.5-14b-instruct'                          # best
# CLOUD_TYPE = 'LMSTUDIO+qwen2.5-32b-instruct'                          # ok
# CLOUD_TYPE = 'LMSTUDIO+llama-3.3-70b-instruct'                        # best, slow

# GPT4All
# CLOUD_TYPE = 'GPT4ALL+Llama-3.2-3B-Instruct-Q4_0.gguf'                # ok
# CLOUD_TYPE = 'GPT4ALL+Llama-3.3-70B-Instruct-Q4_K_M.gguf'             # best, slow

# MLX server, macOS only (pip install -r requirements_mlx.txt --upgrade)
# python -m mlx_lm.server --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit --port 8080 --log-level DEBUG
# CLOUD_TYPE = 'MLX+mlx-community/Meta-Llama-3.1-8B-Instruct-4bit'      # good

@dataclass
class Config:
    CLOUD_TYPE: str = ""
    LOG: bool = True

    # Top-level / global config
    SYSTEM_PROMPT: str = ""
    MARKMAP_TEMPLATE: str = ""
    MERMAID_TEMPLATE: str = ""
    
    USE_AZURE_ENTRA: bool = False

    LLM_TEMPERATURE: float = 0.5
    MAX_TOKENS: int = 4000
    MAX_RETRIES: int = 3
    TOP_MOST_RESULTS: int = 5
    MAX_RETURN_WORDS: int = 5
    LEVELS_DEEP: int = 5
    
    INDENT_SIZE: int = 2
    LINE_SEPARATOR: str = "\n"
    
    OPENAI_COMPATIBILITY: bool = False
    
    MULTIMODAL: bool = False
    MULTIMODAL_MIME_TYPES: List[str] = field(default_factory=list)
    MULTIMODAL_PDF_TO_IMAGE_DPI: int = 200
    
    MARKDOWN_OPTIMIZATION_LEVEL: int = 2
    
    # Common fields that may be set by branches
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None
    OPENAI_DEPLOYMENT: Optional[str] = None
    OPENAI_API_VERSION: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
    
    API_URL: Optional[str] = None
    KEY_HEADER_TEXT: Optional[str] = None
    KEY_HEADER_VALUE: Optional[str] = None
    
    # Azure Meta
    META_MODEL: Optional[str] = None
    
    # Azure Microsoft
    MICROSOFT_MODEL: Optional[str] = None
    
    # Google
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_ACCESS_TOKEN: Optional[str] = None
    PROJECT_ID: Optional[str] = None
    API_ENDPOINT: Optional[str] = None
    LOCATION_ID: Optional[str] = None
    GCP_CLIENT_ID: Optional[str] = None
    GCP_CLIENT_SECRET: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None
    GCP_ENDPOINT: Optional[str] = None
    GCP_LOCATION: Optional[str] = None
    
    # Bedrock
    AWS_MODEL_ID: Optional[str] = None
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    AWS_SERVICE_NAME: Optional[str] = None
    AWS_MODEL_VERSION_KEY: Optional[str] = None
    AWS_MODEL_VERSION_TEXT: Optional[str] = None
    AWS_REGION: Optional[str] = None
    
    # Misc model ID fields
    MODEL_ID: Optional[str] = None
    MODEL_PATH: Optional[str] = None
    ALLOW_DOWNLOAD: Optional[bool] = None
    DEVICE: Optional[str] = None
    
    # Anthropic
    BETA_HEADER_KEY: Optional[str] = None
    BETA_HEADER_TEXT: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_VERSION: Optional[str] = None
    
    # XAI
    XAI_API_KEY: Optional[str] = None
    
    # GITHUB
    GITHUB_TOKEN: Optional[str] = None
    
    # GROQ
    GROQ_API_KEY: Optional[str] = None
    
    # PERPLEXITY
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # DEEPSEEK
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # ALIBABACLOUD
    ALIBABACLOUD_API_KEY: Optional[str] = None
    
    # MISTRAL
    MISTRAL_API_KEY: Optional[str] = None
    
    # HF
    HF_API_KEY: Optional[str] = None
    
    # FIREWORKS
    FIREWORKS_API_KEY: Optional[str] = None


def get_config(CLOUD_TYPE: str = CLOUD_TYPE) -> Config:
    config = Config()

    config.CLOUD_TYPE = CLOUD_TYPE
    config.LOG = LOG

    # defaults
    config.MARKMAP_TEMPLATE = """
    <div class="markmap">
    <script type="text/template">
    ---
    markmap:
    colorFreezeLevel: {{colorFreezeLevel}}
    initialExpandLevel: -1
    ---
    {{markmap}}
    </script>
    </div>
    """

    config.MERMAID_TEMPLATE= """
    <div class="mermaid">
    %%{init: {"theme": "dark"}}%% 
    {{mermaid}}
    </div>
    """

    config.SYSTEM_PROMPT = """
    You are a highly experienced business consultant with expertise in 
    strategic planning, financial analysis, marketing, and organizational development.
    Provide detailed, insightful, and professional advice tailored to the needs of business clients.
    Your responses should reflect the latest industry trends and best practices.
    """
    config.USE_AZURE_ENTRA = False
    config.LLM_TEMPERATURE = 0.5
    config.MAX_TOKENS = 4000
    config.MAX_RETRIES = 3
    config.TOP_MOST_RESULTS = 5
    config.MAX_RETURN_WORDS = 5
    config.LEVELS_DEEP = 5
    config.INDENT_SIZE = 2
    config.LINE_SEPARATOR = "\n"
    config.OPENAI_COMPATIBILITY = False
    config.MULTIMODAL = False
    config.MULTIMODAL_MIME_TYPES = []
    config.MULTIMODAL_PDF_TO_IMAGE_DPI = 200
    config.MARKDOWN_OPTIMIZATION_LEVEL = 2

    # based on CLOUD_TYPE
    if "OPENAI+" in CLOUD_TYPE:
        if "gpt-4o" in CLOUD_TYPE:
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
        config.OPENAI_COMPATIBILITY = True
        config.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_NATIVE')
        config.OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
        config.OPENAI_DEPLOYMENT = ""
        config.OPENAI_API_VERSION = ""
        config.OPENAI_MODEL = CLOUD_TYPE.split("+")[-1]
        config.API_URL = config.OPENAI_API_URL
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.OPENAI_API_KEY or "")

        model = config.OPENAI_MODEL
        if "gpt-4o" in model:
            config.MAX_TOKENS = 16383
        elif "o1-mini" in model:
            config.MAX_TOKENS = 65535
        elif "o1-preview" in model:
            config.MAX_TOKENS = 32767

        config.MARKDOWN_OPTIMIZATION_LEVEL = 3

    elif "AZURE+" in CLOUD_TYPE:
        if "gpt-4o" in CLOUD_TYPE:
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
        config.OPENAI_COMPATIBILITY = True
        config.OPENAI_DEPLOYMENT = CLOUD_TYPE.split("+")[-1]
        config.OPENAI_API_KEY = os.getenv('OPENAI2_API_KEY')
        config.OPENAI_API_URL = os.getenv('OPENAI2_API_BASE')
        config.OPENAI_API_VERSION = os.getenv('OPENAI2_API_VERSION')
        config.OPENAI_MODEL = ""
        if config.OPENAI_API_URL and config.OPENAI_DEPLOYMENT and config.OPENAI_API_VERSION:
            config.API_URL = (
                f"{config.OPENAI_API_URL}openai/deployments/"
                f"{config.OPENAI_DEPLOYMENT}/chat/completions"
                f"?api-version={config.OPENAI_API_VERSION}"
            )
        config.KEY_HEADER_TEXT = "api-key"
        config.KEY_HEADER_VALUE = config.OPENAI_API_KEY or ""
        if "gpt-4o" in CLOUD_TYPE:
            config.MAX_TOKENS = 16383
        config.MARKDOWN_OPTIMIZATION_LEVEL = 3

    elif "OPENROUTER+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
        config.OPENAI_MODEL = CLOUD_TYPE.split("+")[-1]
        config.API_URL = "https://openrouter.ai/api/v1/chat/completions"
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.OPENROUTER_API_KEY or "")
        if any(s in config.OPENAI_MODEL for s in ["gpt-4o", "o1-mini", "o1-preview"]):
            config.MAX_TOKENS = 16383
        config.MARKDOWN_OPTIMIZATION_LEVEL = 3

    elif "GITHUB+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        model = CLOUD_TYPE.split("+")[-1]
        config.GITHUB_TOKEN = os.getenv('GITHUB_MODELS_TOKEN')
        config.OPENAI_MODEL = model
        config.API_URL = "https://models.inference.ai.azure.com/chat/completions"
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.GITHUB_TOKEN or "")
        if "gpt-4o" in model:
            config.MAX_TOKENS = 16383
        config.MARKDOWN_OPTIMIZATION_LEVEL = 3

    elif "AZURE_META+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        meta_model = CLOUD_TYPE.split("+")[-1]
        config.META_MODEL = meta_model
        config.OPENAI_API_KEY = os.getenv(f"AZURE_{meta_model}_KEY")
        endpoint = os.getenv(f"AZURE_{meta_model}_ENDPOINT")
        config.OPENAI_API_URL = endpoint + "/v1/chat/completions" if endpoint else None
        config.OPENAI_DEPLOYMENT = ""
        config.OPENAI_API_VERSION = ""
        config.OPENAI_MODEL = ""
        config.API_URL = config.OPENAI_API_URL
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.OPENAI_API_KEY or "")

    elif "AZURE_Microsoft+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        microsoft_model = CLOUD_TYPE.split("+")[-1]
        config.MICROSOFT_MODEL = microsoft_model
        config.OPENAI_API_KEY = os.getenv(f"AZURE_{microsoft_model}_KEY")
        endpoint = os.getenv(f"AZURE_{microsoft_model}_ENDPOINT")
        config.OPENAI_API_URL = endpoint + "/v1/chat/completions" if endpoint else None
        config.OPENAI_DEPLOYMENT = ""
        config.OPENAI_API_VERSION = ""
        config.OPENAI_MODEL = ""
        config.API_URL = config.OPENAI_API_URL
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.OPENAI_API_KEY or "")

    elif "GEMINI" in CLOUD_TYPE or "VERTEXAI" in CLOUD_TYPE:
        config.MULTIMODAL = True
        config.MULTIMODAL_MIME_TYPES = ["application/pdf"]
        system = CLOUD_TYPE.split("+")[0]
        model = CLOUD_TYPE.split("+")[-1]
        config.MAX_TOKENS = 8191

        if system == "GEMINI":
            config.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY_AI')
            config.API_URL = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={config.GOOGLE_API_KEY}"
            )
            config.KEY_HEADER_TEXT = ""
            config.KEY_HEADER_VALUE = ""
        elif system == "VERTEXAI":
            config.PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
            config.API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
            config.LOCATION_ID = "us-central1"
            config.GOOGLE_ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN_AI')
            config.API_URL = (
                f"https://{config.API_ENDPOINT}/v1beta1/projects/{config.PROJECT_ID}/"
                f"locations/{config.LOCATION_ID}/publishers/google/models/{model}:generateContent"
            )
            config.KEY_HEADER_TEXT = "Authorization"
            config.KEY_HEADER_VALUE = "Bearer " + (config.GOOGLE_ACCESS_TOKEN or "")
            
            # Example GCP environment fields
            config.GCP_CLIENT_ID = os.getenv('GCP_CLIENT_ID')
            config.GCP_CLIENT_SECRET = os.getenv('GCP_CLIENT_SECRET')
            config.GCP_PROJECT_ID = config.PROJECT_ID
            config.GCP_ENDPOINT = config.API_ENDPOINT
            config.GCP_LOCATION = config.LOCATION_ID

    elif "BEDROCK" in CLOUD_TYPE:
        config.AWS_MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
        config.AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
        config.AWS_SERVICE_NAME = "bedrock-runtime"
        config.AWS_MODEL_VERSION_KEY = ""
        config.AWS_MODEL_VERSION_TEXT = ""
        config.AWS_REGION = "us-east-1"
        if config.AWS_MODEL_ID.startswith("anthropic."):
            config.AWS_REGION = "eu-central-1"
            config.AWS_MODEL_VERSION_KEY = "anthropic_version"
            config.AWS_MODEL_VERSION_TEXT = "bedrock-2023-05-31"
        elif config.AWS_MODEL_ID.startswith("mistral."):
            pass
        elif config.AWS_MODEL_ID.startswith("amazon.titan-"):
            config.MAX_TOKENS = 3000
        elif config.AWS_MODEL_ID.startswith("amazon.nova-"):
            config.MAX_TOKENS = 5120
        else:
            raise Exception("Error: Unsupported AWS Bedrock model.")

    elif "OLLAMA+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        if config.OPENAI_COMPATIBILITY:
            config.API_URL="http://localhost:11434/v1/chat/completions"
        else: 
            config.API_URL="http://localhost:11434/api/generate"


    elif "LMSTUDIO+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.API_URL = "http://localhost:1234/v1"

    elif "GPT4ALL+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.MODEL_PATH = os.path.join(
            os.path.expanduser("~"),
            "Library",
            "Application Support",
            "nomic.ai",
            "GPT4ALL"
        )
        config.MAX_TOKENS = 2000
        config.ALLOW_DOWNLOAD = False
        config.DEVICE = "gpu"
        config.API_URL = ""

    elif "ANTHROPIC" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.BETA_HEADER_KEY = ""
        config.BETA_HEADER_TEXT = ""
        config.MARKDOWN_OPTIMIZATION_LEVEL = 3

        if "claude-3-5" in config.MODEL_ID:
            config.MAX_TOKENS = 8192
            if "sonnet" in config.MODEL_ID:
                config.MULTIMODAL = True
                config.MULTIMODAL_MIME_TYPES = ["application/pdf"]
        
        config.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        config.ANTHROPIC_VERSION = "2023-06-01"
        config.KEY_HEADER_TEXT = "x-api-key"
        config.KEY_HEADER_VALUE = config.ANTHROPIC_API_KEY or ""
        config.API_URL = "https://api.anthropic.com/v1/messages"

    elif "XAI+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.XAI_API_KEY = os.getenv('XAI_API_KEY')
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.XAI_API_KEY or "")
        config.API_URL = "https://api.x.ai/v1/chat/completions"
        if "-vision-" in config.MODEL_ID:
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]

    elif "GROQ+" in CLOUD_TYPE:
        config.MAX_TOKENS = 8000
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.GROQ_API_KEY or "")
        config.API_URL = "https://api.groq.com/openai/v1/chat/completions"

    elif "PERPLEXITY+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.PERPLEXITY_API_KEY or "")
        config.API_URL = "https://api.perplexity.ai/chat/completions"

    elif "DEEPSEEK+" in CLOUD_TYPE:
        config.MAX_TOKENS = 8000
        config.OPENAI_COMPATIBILITY = False
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.DEEPSEEK_API_KEY or "")
        config.API_URL = "https://api.deepseek.com/beta/chat/completions"

    elif "ALIBABACLOUD+" in CLOUD_TYPE:
        config.MAX_TOKENS = 2000 if "qwen-max" in CLOUD_TYPE else 1500
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.ALIBABACLOUD_API_KEY = os.getenv('ALIBABACLOUD_API_KEY')
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.ALIBABACLOUD_API_KEY or "")
        config.API_URL = (
            "https://dashscope-intl.aliyuncs.com/api/v1/"
            "services/aigc/text-generation/generation"
        )

    elif "MISTRAL+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
        config.API_URL = "https://api.mistral.ai/v1/chat/completions"
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.MISTRAL_API_KEY or "")

    elif "HF+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]
        config.HF_API_KEY = os.getenv('HF_API_KEY')
        config.API_URL = (
            f"https://api-inference.huggingface.co/models/"
            f"{config.MODEL_ID}/v1/chat/completions"
        )
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.HF_API_KEY or "")

    elif "FIREWORKS+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        model_prefix = "accounts/fireworks/models/"
        config.MODEL_ID = model_prefix + CLOUD_TYPE.split("+")[-1]
        config.FIREWORKS_API_KEY = os.getenv('FIREWORKS_API_KEY')
        config.API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
        config.KEY_HEADER_TEXT = "Authorization"
        config.KEY_HEADER_VALUE = "Bearer " + (config.FIREWORKS_API_KEY or "")

    elif "MLX+" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = True
        config.MODEL_ID = CLOUD_TYPE.split("+")[-1]  # not used
        config.API_URL = "http://localhost:8080/v1/chat/completions"

    else:
        raise Exception("Error: Unknown CLOUD_TYPE")

    return config


# only used for action = image, image_n

CLOUD_TYPE_IMAGE = ''

# Azure
# CLOUD_TYPE_IMAGE = 'AZURE+dall-e-3'                        # best
        
# OpenAI        
# CLOUD_TYPE_IMAGE = 'OPENAI+dall-e-3'                       # best
        
# StabilityAI        
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large'               # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-large-turbo'         # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3.5-medium'              # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large'                 # good
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-large-turbo'           # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+sd3-medium'                # bad results
# CLOUD_TYPE_IMAGE = 'STABILITYAI+core'                      # better
# CLOUD_TYPE_IMAGE = 'STABILITYAI+ultra'                     # good

# VertexAI
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-generate-001'      # best
# CLOUD_TYPE_IMAGE = 'VERTEXAI+imagen-3.0-fast-generate-001' # better

# MLX (local generation, MacOS w/ Apple Silicon only)
CLOUD_TYPE_IMAGE = 'MLX+mflux-flux1-schnell-4bit'          # best 
# CLOUD_TYPE_IMAGE = 'MLX+mflux-flux1-dev-4bit'              # good 
        
# IdeogramAI        
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2'                        # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_2_TURBO'                  # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_1'                        # best
# CLOUD_TYPE_IMAGE = 'IDEOGRAMAI+V_1_TURBO'                  # best
        
# Black Forrest Labs        
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1-ultra'                # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro-1.1'                      # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-pro'                          # best
# CLOUD_TYPE_IMAGE = 'BFL+flux-dev'                          # best

# RecraftAI
# CLOUD_TYPE_IMAGE = 'RECRAFTAI+recraftv3'                   # best
# CLOUD_TYPE_IMAGE = 'RECRAFTAI+recraft20b'                  # best


@dataclass
class ImageConfig:
    CLOUD_TYPE_IMAGE: str = ""
    LOG: bool = True

    # Common / top-level fields
    RESIZE_IMAGE: bool = False
    RESIZE_IMAGE_WIDTH: int = 1024
    RESIZE_IMAGE_HEIGHT: int = 1024
    INSERT_IMAGE_AS_BACKGROUND: bool = True
    OPTIMIZE_PROMPT_IMAGE: bool = False

    # Azure/OpenAI fields
    IMAGE_EXPLICIT_STYLE: Optional[str] = None
    IMAGE_QUALITY: Optional[str] = None
    IMAGE_STYLE: Optional[str] = None

    OPENAI_API_KEY_IMAGE: Optional[str] = None
    OPENAI_API_VERSION_IMAGE: Optional[str] = None
    OPENAI_DEPLOYMENT_IMAGE: Optional[str] = None
    OPENAI_MODEL_IMAGE: Optional[str] = None
    OPENAI_IMAGE_API_URL: Optional[str] = None

    IMAGE_API_URL: Optional[str] = None
    IMAGE_KEY_HEADER_TEXT: Optional[str] = None
    IMAGE_KEY_HEADER_VALUE: Optional[str] = None

    # STABILITYAI+
    IMAGE_MODEL_ID: Optional[str] = None
    MODEL_ENDPOINT: Optional[str] = None
    IMAGE_STYLE_PRESET: Optional[str] = None
    IMAGE_OUTPUT_FORMAT: Optional[str] = None
    IMAGE_ASPECT_RATIO: Optional[str] = None
    IMAGE_SEED: int = 0
    IMAGE_NEGATIV_PROMPT: Optional[str] = None
    STABILITYAI_API_KEY: Optional[str] = None

    # Vertex AI
    IMAGE_ADD_WATERMARK: Optional[bool] = None
    IMAGE_PROJECT_ID: Optional[str] = None
    IMAGE_API_ENDPOINT: Optional[str] = None
    IMAGE_LOCATION_ID: Optional[str] = None
    GCP_CLIENT_ID_IMAGE: Optional[str] = None
    GCP_CLIENT_SECRET_IMAGE: Optional[str] = None
    GOOGLE_ACCESS_TOKEN_IMAGE: Optional[str] = None

    # MLX+
    IMAGE_HEIGHT: Optional[int] = None
    IMAGE_WIDTH: Optional[int] = None
    IMAGE_MODEL_VERSION: Optional[str] = None
    IMAGE_NUM_STEPS: Optional[int] = None
    IMAGE_MODEL_QUANTIZATION: Optional[int] = None

    # IDEOGRAMAI+
    IMAGE_RESOLUTION: Optional[str] = None

    # BFL+
    IMAGE_SAFETY_TOLERANCE: Optional[int] = None
    IMAGE_RAW: Optional[bool] = None
    IMAGE_PROMPT_UPSAMPLING: Optional[bool] = None
    IMAGE_STEPS: Optional[int] = None
    IMAGE_INTERVAL: Optional[int] = None
    IMAGE_GUIDANCE: Optional[int] = None

    # RECRAFTAI+
    IMAGE_SIZE: Optional[str] = None
    IMAGE_RESPONSE_FORMAT: Optional[str] = None
    IMAGE_SUBSTYLE: Optional[str] = None


def get_image_config(CLOUD_TYPE_IMAGE: str = CLOUD_TYPE_IMAGE) -> ImageConfig:
    config = ImageConfig()

    config.CLOUD_TYPE_IMAGE = CLOUD_TYPE_IMAGE
    config.LOG = LOG

    # Default values
    config.RESIZE_IMAGE = False
    config.RESIZE_IMAGE_WIDTH = 1024
    config.RESIZE_IMAGE_HEIGHT = 1024
    config.INSERT_IMAGE_AS_BACKGROUND = True
    config.OPTIMIZE_PROMPT_IMAGE = False

    # Branch logic
    if "AZURE+" in CLOUD_TYPE_IMAGE or "OPENAI+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_EXPLICIT_STYLE = "digital art"
        config.IMAGE_QUALITY = "hd"    # hd, standard
        config.IMAGE_STYLE = "vivid"  # natural, vivid

        if "AZURE+" in CLOUD_TYPE_IMAGE:
            config.OPENAI_API_KEY_IMAGE = os.getenv('OPENAI2_API_KEY')
            config.OPENAI_API_VERSION_IMAGE = '2024-02-01'
            config.OPENAI_DEPLOYMENT_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
            config.OPENAI_MODEL_IMAGE = ""
            config.OPENAI_IMAGE_API_URL = os.getenv('OPENAI2_API_BASE')
            config.IMAGE_API_URL = (
                f"{config.OPENAI_IMAGE_API_URL}openai/deployments/"
                f"{config.OPENAI_DEPLOYMENT_IMAGE}/images/generations"
                f"?api-version={config.OPENAI_API_VERSION_IMAGE}"
            )
            config.IMAGE_KEY_HEADER_TEXT = "api-key"
            config.IMAGE_KEY_HEADER_VALUE = config.OPENAI_API_KEY_IMAGE

        elif "OPENAI+" in CLOUD_TYPE_IMAGE:
            config.OPENAI_API_KEY_IMAGE = os.getenv('OPENAI_API_KEY_NATIVE')
            config.OPENAI_API_VERSION_IMAGE = ""
            config.OPENAI_DEPLOYMENT_IMAGE = ""
            config.OPENAI_MODEL_IMAGE = CLOUD_TYPE_IMAGE.split("+")[-1]
            config.OPENAI_IMAGE_API_URL = "https://api.openai.com/v1/images/generations"
            config.IMAGE_API_URL = config.OPENAI_IMAGE_API_URL
            config.IMAGE_KEY_HEADER_TEXT = "Authorization"
            config.IMAGE_KEY_HEADER_VALUE = "Bearer " + (
                config.OPENAI_API_KEY_IMAGE or ""
            )

    elif "STABILITYAI+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
        config.MODEL_ENDPOINT = config.IMAGE_MODEL_ID.split("-")[0]
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
        config.STABILITYAI_API_KEY = os.getenv('STABILITYAI_API_KEY')
        config.IMAGE_API_URL = f"https://api.stability.ai/v2beta/stable-image/generate/{config.MODEL_ENDPOINT}"

    elif "VERTEXAI+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
        config.IMAGE_ASPECT_RATIO = "1:1"  # 1:1 (1024x1024) 9:16 (768x1408) 16:9 (1408x768) 3:4 (896x1280) 4:3 (1280x896)
        config.IMAGE_EXPLICIT_STYLE = "digital art"
        config.IMAGE_ADD_WATERMARK = False
        config.IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"

        config.IMAGE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
        config.IMAGE_API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
        config.IMAGE_LOCATION_ID = "us-central1"
        config.IMAGE_KEY_HEADER_TEXT = "Authorization"
        config.GCP_CLIENT_ID_IMAGE = os.getenv('GCP_CLIENT_ID')
        config.GCP_CLIENT_SECRET_IMAGE = os.getenv('GCP_CLIENT_SECRET')
        config.GOOGLE_ACCESS_TOKEN_IMAGE = os.getenv('GOOGLE_ACCESS_TOKEN_AI')

        config.IMAGE_API_URL = (
            f"https://{config.IMAGE_API_ENDPOINT}/v1/projects/{config.IMAGE_PROJECT_ID}"
            f"/locations/{config.IMAGE_LOCATION_ID}/publishers/google/models/"
            f"{config.IMAGE_MODEL_ID}:predict"
        )

    elif "MLX+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
        config.IMAGE_SEED = 0
        #https://enragedantelope.github.io/Styles-FluxDev/
        config.IMAGE_EXPLICIT_STYLE = "photorealistic 3D art"
        #config.IMAGE_EXPLICIT_STYLE = "papercraft-kirigami art"
        #config.IMAGE_EXPLICIT_STYLE = "computer collage art"
        config.IMAGE_NEGATIV_PROMPT = ""
        config.IMAGE_HEIGHT = 1024 # 1024 # 512 # 768
        config.IMAGE_WIDTH = 1024 # 1024 # 512 # 768

        if "-flux1" in config.IMAGE_MODEL_ID:
            if "-schnell" in config.IMAGE_MODEL_ID:
                config.IMAGE_MODEL_VERSION = "schnell"
                config.IMAGE_NUM_STEPS = 2 # 2-4
            elif "-dev" in config.IMAGE_MODEL_ID:
                config.IMAGE_MODEL_VERSION = "dev"
                config.IMAGE_NUM_STEPS = 20 # 20-25
            else:
                raise Exception("Error: image model version not supported using MLX")
            
            if "-4bit" in config.IMAGE_MODEL_ID:
                config.IMAGE_MODEL_QUANTIZATION = 4
            elif "-8bit" in config.IMAGE_MODEL_ID:
                config.IMAGE_MODEL_QUANTIZATION = 8
            else:
                raise Exception("Error: image model quantization not supported using MLX")
        else:
            raise Exception("Error: image model not supported using MLX")

    elif "IDEOGRAMAI+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
        if config.IMAGE_MODEL_ID in ("V_2", "V_2_TURBO"):
            config.IMAGE_STYLE_PRESET = "GENERAL"  # DESIGN, GENERAL, REALISTIC, RENDER_3D, ANIME
            config.IMAGE_EXPLICIT_STYLE = config.IMAGE_STYLE_PRESET
        else:
            config.IMAGE_EXPLICIT_STYLE = "computer collage art"

        config.IMAGE_OUTPUT_FORMAT = "png"
        config.IMAGE_SEED = 0
        config.IMAGE_NEGATIV_PROMPT = "text, characters, letters, words, labels"
        config.IMAGE_HEIGHT = 1024
        config.IMAGE_WIDTH = 1024
        config.IMAGE_RESOLUTION = f"RESOLUTION_{config.IMAGE_WIDTH}_{config.IMAGE_HEIGHT}"

        config.IMAGE_KEY_HEADER_TEXT = "Api-Key"
        config.IMAGE_KEY_HEADER_VALUE = os.getenv('IDEOGRAMAI_API_KEY')
        config.IMAGE_API_URL = "https://api.ideogram.ai/generate"

    elif "BFL+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
        config.IMAGE_EXPLICIT_STYLE = "computer collage art"
        config.IMAGE_OUTPUT_FORMAT = "png"
        config.IMAGE_SEED = 0
        config.IMAGE_SAFETY_TOLERANCE = 6  # 0-6, 6 = least strict

        # Example branching by model
        if config.IMAGE_MODEL_ID == "flux-pro-1.1-ultra":
            config.IMAGE_RAW = False
            config.IMAGE_ASPECT_RATIO = "4:3" # between 21:9 and 9:21
        elif config.IMAGE_MODEL_ID == "flux-pro-1.1":
            config.IMAGE_HEIGHT = 1024
            config.IMAGE_WIDTH = 1024
            config.IMAGE_PROMPT_UPSAMPLING = False
        elif config.IMAGE_MODEL_ID == "flux-pro":
            config.IMAGE_HEIGHT = 1024
            config.IMAGE_WIDTH = 1024
            config.IMAGE_STEPS = 28
            config.IMAGE_INTERVAL = 2
            config.IMAGE_PROMPT_UPSAMPLING = False
            config.IMAGE_GUIDANCE = 3
        elif config.IMAGE_MODEL_ID == "flux-dev":
            config.IMAGE_HEIGHT = 1024
            config.IMAGE_WIDTH = 1024
            config.IMAGE_STEPS = 28
            config.IMAGE_PROMPT_UPSAMPLING = False
            config.IMAGE_GUIDANCE = 3
        else:
            raise Exception("Error: Unknown Flux image model")

        config.IMAGE_KEY_HEADER_TEXT = "x-key"
        config.IMAGE_KEY_HEADER_VALUE = os.getenv('BFL_API_KEY')
        config.IMAGE_API_URL = "https://api.bfl.ml/v1/"

    elif "RECRAFTAI+" in CLOUD_TYPE_IMAGE:
        config.IMAGE_MODEL_ID = CLOUD_TYPE_IMAGE.split("+")[-1]
        config.IMAGE_API_URL = "https://external.api.recraft.ai/v1/images/generations"
        config.IMAGE_KEY_HEADER_TEXT = "Authorization"
        config.IMAGE_KEY_HEADER_VALUE = "Bearer " + (os.getenv('RECRAFT_API_TOKEN') or "")
        config.IMAGE_SIZE = "1024x1024"  # 1024x1024, 1365x1024, 1024x1365, 1536x1024, 1024x1536, 1820x1024, 1024x1820, 1024x2048, 2048x1024, 1434x1024, 1024x1434, 1024x1280, 1280x1024, 1024x1707, 1707x1024"
        config.IMAGE_RESPONSE_FORMAT = "url" # url, b64_json
        config.IMAGE_EXPLICIT_STYLE = ""
        config.IMAGE_SUBSTYLE = ""

        if config.IMAGE_MODEL_ID == "recraftv3":

            # IMAGE_STYLE = "digital_illustration"
            # IMAGE_SUBSTYLE = "2d_art_poster" # 2d_art_poster, 2d_art_poster_2, engraving_color, grain, hand_drawn, hand_drawn_outline, handmade_3d, infantile_sketch, pixel_art
            
            config.IMAGE_STYLE = "realistic_image"
            config.IMAGE_SUBSTYLE = "enterprise"
            
            # IMAGE_STYLE = "vector_illustration"
            # IMAGE_SUBSTYLE = "engraving" # engraving, line_art, line_circuit, linocut

        elif config.IMAGE_MODEL_ID == "recraft20b":
            
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
        raise Exception("Error: Unknown CLOUD_TYPE_IMAGE")

    return config



# only used for action = DEEPL (translation)


CLOUD_TYPE_TRANSLATION = 'DEEPL'

@dataclass
class TranslationConfig:
    CLOUD_TYPE_TRANSLATION: Optional[str] = None
    DEEPL_API_KEY: Optional[str] = None
    DEEPL_BASE_URL: Optional[str] = None
    KEY_HEADER_TEXT_TRANSLATION: Optional[str] = None
    KEY_HEADER_VALUE_TRANSLATION: Optional[str] = None


def get_translation_config(CLOUD_TYPE_TRANSLATION: str) -> TranslationConfig:
    config = TranslationConfig(CLOUD_TYPE_TRANSLATION=CLOUD_TYPE_TRANSLATION)

    if "DEEPL" in CLOUD_TYPE_TRANSLATION:
        config.DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
        # config.DEEPL_BASE_URL = "https://api.deepl.com/v2/translate"  # paid version
        config.DEEPL_BASE_URL = "https://api-free.deepl.com/v2/translate"  # free version
        config.KEY_HEADER_TEXT_TRANSLATION = "Authorization"
        config.KEY_HEADER_VALUE_TRANSLATION = f"DeepL-Auth-Key {config.DEEPL_API_KEY or ''}"

    else:
        raise Exception("Error: Unknown CLOUD_TYPE_TRANSLATION")

    return config

