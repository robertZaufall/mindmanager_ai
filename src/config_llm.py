import os
import sys
from types import SimpleNamespace
from file_helper import load_env

# Azure serverless models, !use your model deployment name, ie. gpt-4o!
CLOUD_TYPE = 'AZURE+model-router'                                     #
# CLOUD_TYPE = 'AZURE+gpt-5'                                            # best in class
# CLOUD_TYPE = 'AZURE+gpt-5-mini'                                       # best
# CLOUD_TYPE = 'AZURE+gpt-5-nano'                                       # best
# CLOUD_TYPE = 'AZURE+gpt-4.1'                                          # best in class
# CLOUD_TYPE = 'AZURE+gpt-4.1-mini'                                     # best
# CLOUD_TYPE = 'AZURE+gpt-4.1-nano'                                     # best
# CLOUD_TYPE = 'AZURE+gpt-4o'                                           # best
# CLOUD_TYPE = 'AZURE+gpt-4o-mini'                                      # best

# CLOUD_TYPE = 'AZURE+o4-mini-high'                                     # best
# CLOUD_TYPE = 'AZURE+o4-mini-medium'                                   # best
# CLOUD_TYPE = 'AZURE+o4-mini-low'                                      # best
# CLOUD_TYPE = 'AZURE+o4-mini'                                          # best
# CLOUD_TYPE = 'AZURE+o3-mini-high'                                     # good
# CLOUD_TYPE = 'AZURE+o3-mini-medium'                                   # good
# CLOUD_TYPE = 'AZURE+o3-mini-low'                                      # good
# CLOUD_TYPE = 'AZURE+o3-mini'                                          # good
# CLOUD_TYPE = 'AZURE+o1'                                               # best

# OpenAI
# CLOUD_TYPE = 'OPENAI+gpt-5.1-2025-11-13-none'                         # best ($  1.25, $ 10.00)
# CLOUD_TYPE = 'OPENAI+gpt-5.1-2025-11-13-low'                          # best ($  1.25, $ 10.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5.1-2025-11-13-medium'                       # best ($  1.25, $ 10.00 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5.1-2025-11-13-high'                         # best ($  1.25, $ 10.00 +++ reasoning tokens)

# CLOUD_TYPE = 'OPENAI+gpt-5.1-codex-low'                               # best ($  1.25, $ 10.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5.1-codex-medium'                            # best ($  1.25, $ 10.00 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5.1-codex-high'                              # best ($  1.25, $ 10.00 +++ reasoning tokens)

# CLOUD_TYPE = 'OPENAI+gpt-5-2025-08-07'                                # best ($  1.25, $ 10.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-2025-08-07-minimal'                        # best ($  1.25, $ 10.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-2025-08-07-low'                            # best ($  1.25, $ 10.00 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-2025-08-07-medium'                         # best ($  1.25, $ 10.00 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-2025-08-07-high'                           # best ($  1.25, $ 10.00 +++ reasoning tokens)

# CLOUD_TYPE = 'OPENAI+gpt-5-mini-2025-08-07'                           # ok   ($  0.25, $  2.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-mini-2025-08-07-low'                       # ok   ($  0.25, $  2.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-mini-2025-08-07-medium'                    # best ($  0.25, $  2.00 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-mini-2025-08-07-high'                      # best ($  0.25, $  2.00 +++ reasoning tokens)

# CLOUD_TYPE = 'OPENAI+gpt-5-nano-2025-08-07'                           # ok   ($  0.05, $  0.40 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-nano-2025-08-07-low'                       # ok   ($  0.05, $  0.40 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-nano-2025-08-07-medium'                    # best ($  0.05, $  0.40 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+gpt-5-nano-2025-08-07-high'                      # best ($  0.05, $  0.40 +++ reasoning tokens)

# CLOUD_TYPE = 'OPENAI+o3-pro-2025-06-10'                               # best ($ 20.00, $ 80.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o3-2025-04-16'                                   # best ($  2.00, $  8.00 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o3-2025-04-16-flex'                              # best ($  1.00, $  4.00 + reasoning tokens)

# CLOUD_TYPE = 'OPENAI+o4-mini-2025-04-16'                              # best ($  1.10, $  4.40 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o4-mini-2025-04-16-low'                          # best ($  1.10, $  4.40 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o4-mini-2025-04-16-high'                         # best ($  1.10, $  4.40 +++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o4-mini-2025-04-16-medium'                       # best ($  1.10, $  4.40 ++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o3-mini-2025-01-31'                              # best ($  1.10, $  4.40 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o3-mini-2025-01-31-low'                          # best ($  1.10, $  4.40 + reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o3-mini-2025-01-31-high'                         # best ($  1.10, $  4.40 +++ reasoning tokens)
# CLOUD_TYPE = 'OPENAI+o3-mini-2025-01-31-medium'                       # best ($  1.10, $  4.40 ++ reasoning tokens)

# CLOUD_TYPE = 'OPENAI+gpt-4.1-2025-04-14'                              # best ($ 2.00, $  8.00)
# CLOUD_TYPE = 'OPENAI+gpt-4.1-mini-2025-04-14'                         # best ($ 0.40, $  1.60)
# CLOUD_TYPE = 'OPENAI+gpt-4.1-nano-2025-04-14'                         # best ($ 0.10, $  0.40)
# CLOUD_TYPE = 'OPENAI+gpt-4o-2024-11-20'                               # best ($ 2.50, $ 10.00)
# CLOUD_TYPE = 'OPENAI+gpt-4o-2024-08-06'                               # best ($ 2.50, $ 10.00) (OpenAI's 4o default) 
# CLOUD_TYPE = 'OPENAI+gpt-4o-search-preview-2025-03-11'                # best ($ 2.50, $ 10.00)
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini-2024-07-18'                          # best ($ 0.15, $  0.60)
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini-search-preview-2025-03-11'           # best ($ 0.15, $  0.60)

# Github Models
# CLOUD_TYPE = 'GITHUB+openai/gpt-4.1-nano'                             # 33k
# CLOUD_TYPE = 'GITHUB+openai/gpt-4.1-mini'                             # 33k
# CLOUD_TYPE = 'GITHUB+openai/gpt-4.1'                                  # 33k
# CLOUD_TYPE = 'GITHUB+openai/gpt-4o'                                   # 16k
# CLOUD_TYPE = 'GITHUB+openai/gpt-4o-mini'                              # 4k
# CLOUD_TYPE = 'GITHUB+microsoft/Phi-4'                                 # 16k
# CLOUD_TYPE = 'GITHUB+microsoft/Phi-4-mini-instruct'                   # 4k
# CLOUD_TYPE = 'GITHUB+meta/Llama-3.3-70B-Instruct'                     # 4k
# CLOUD_TYPE = 'GITHUB+deepseek/DeepSeek-R1'                            # 4k / slow
# CLOUD_TYPE = 'GITHUB+deepseek/DeepSeek-R1-0528'                       # 4k / slow
# CLOUD_TYPE = 'GITHUB+xai/grok-3-mini'                                 # 4k
# CLOUD_TYPE = 'GITHUB+xai/grok-3'                                      # 4k
# CLOUD_TYPE = 'GITHUB+mistral-ai/mistral-medium-2505'                  # 4k

# Anthropic     
# CLOUD_TYPE = 'ANTHROPIC+claude-haiku-4-5-20251001'                    # best ($  1.00, $  5.00)
# CLOUD_TYPE = 'ANTHROPIC+claude-sonnet-4-5-20250929'                   # best ($  3.00, $ 15.00)
# CLOUD_TYPE = 'ANTHROPIC+claude-sonnet-4-20250514'                     # best ($  3.00, $ 15.00)
# CLOUD_TYPE = 'ANTHROPIC+claude-opus-4-1-20250805'                     # best ($ 15.00, $ 75.00)
# CLOUD_TYPE = 'ANTHROPIC+claude-3-7-sonnet-20250219'                   # best ($  3.00, $ 15.00)
# CLOUD_TYPE = 'ANTHROPIC+claude-3-5-sonnet-20241022'                   # best ($  3.00, $ 15.00)
# CLOUD_TYPE = 'ANTHROPIC+claude-3-5-haiku-20241022'                    # best ($  0.80, $  4.00)

# Google Gemini
# CLOUD_TYPE = 'GEMINI+gemini-2.5-flash-preview-09-2025'                # ($ 0.30, $  2.50 (non-thinking) / 3.50 (thinking)) best
# CLOUD_TYPE = 'GEMINI+gemini-2.5-flash-lite-preview-09-2025'           # ($ 0.10, $  0.40) bad
# CLOUD_TYPE = 'GEMINI+gemini-2.5-flash'                                # ($ 0.30, $  2.50 (non-thinking) / 3.50 (thinking)) best
# CLOUD_TYPE = 'GEMINI+gemini-2.5-flash-lite'                           # ($ 0.10, $  0.40) good
# CLOUD_TYPE = 'GEMINI+gemini-2.5-pro'                                  # ($ 1.25, $ 10.00) best
# CLOUD_TYPE = 'GEMINI+gemini-2.0-flash-lite'                           # ($ 0.08, $  0.30) best
# CLOUD_TYPE = 'GEMINI+gemini-2.0-flash'                                # ($ 0.10, $  0.40) best

# CLOUD_TYPE = 'GEMINI+gemma-3-27b-it'                                  # best
# CLOUD_TYPE = 'GEMINI+gemma-3n-e4b-it'                                 # good

# Google Gemini Vertex AI (OAuth2)     
# CLOUD_TYPE = 'VERTEXAI+gemini-2.5-flash-preview-09-2025'              # best
# CLOUD_TYPE = 'VERTEXAI+gemini-2.5-flash-lite-preview-09-2025'         # bad
# CLOUD_TYPE = 'VERTEXAI+gemini-2.5-flash'                              # best
# CLOUD_TYPE = 'VERTEXAI+gemini-2.5-flash-lite'                         # good
# CLOUD_TYPE = 'VERTEXAI+gemini-2.5-pro'                                # best
# CLOUD_TYPE = 'VERTEXAI+gemini-2.0-flash'                              # best
# CLOUD_TYPE = 'VERTEXAI+anthropic/claude-sonnet-4'                     # *** implementation does not work ***

# AWS Bedrock
# CLOUD_TYPE = 'BEDROCK+amazon.nova-premier-v1:0'                       # ok
# CLOUD_TYPE = 'BEDROCK+amazon.nova-pro-v1:0'                           # best, max token output only 5120
# CLOUD_TYPE = 'BEDROCK+amazon.nova-lite-v1:0'                          # best, max token output only 5120
# CLOUD_TYPE = 'BEDROCK+us.anthropic.claude-sonnet-4-5-20250929-v1:0'   # best
# CLOUD_TYPE = 'BEDROCK+us.anthropic.claude-sonnet-4-20250514-v1:0'     # best
# CLOUD_TYPE = 'BEDROCK+mistral.mistral-large-2402-v1:0'                # ok

# xAI     
# CLOUD_TYPE = 'XAI+grok-4-fast-reasoning'                              # ($ 0.20, $  0.50), best in class
# CLOUD_TYPE = 'XAI+grok-4-fast-non-reasoning'                          # ($ 0.20, $  0.50), best
# CLOUD_TYPE = 'XAI+grok-4-0709'                                        # ($ 3.00, $ 15.00), best
# CLOUD_TYPE = 'XAI+grok-3'                                             # ($ 3.00, $ 15.00), best
# CLOUD_TYPE = 'XAI+grok-3-mini'                                        # ($ 0.30, $  0.50), best
# CLOUD_TYPE = 'XAI+grok-2-vision-1212'                                 # ($ 2.00, $ 10.00), best

# DeepSeek
# CLOUD_TYPE = 'DEEPSEEK+deepseek-chat'                                 # best
# CLOUD_TYPE = 'DEEPSEEK+deepseek-reasoner'                             # best (slow)

# STACKIT
# CLOUD_TYPE = 'STACKIT+cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic'     # good

# Alibaba Cloud
# CLOUD_TYPE = 'ALIBABACLOUD+qwen-plus-2025-07-28'                      # best (Qwen3)
# CLOUD_TYPE = 'ALIBABACLOUD+qwen3-max-preview'                         # best (Qwen3)
# CLOUD_TYPE = 'ALIBABACLOUD+qwen-max-2025-01-25'                       # best (Qwen2.5)
# CLOUD_TYPE = 'ALIBABACLOUD+qwen3-235b-a22b-instruct-2507'             # good

# Mistral AI
# CLOUD_TYPE = 'MISTRAL+mistral-large-latest'                           # best in class
# CLOUD_TYPE = 'MISTRAL+ministral-3b-latest'                            # ok
# CLOUD_TYPE = 'MISTRAL+ministral-8b-latest'                            # ok
# CLOUD_TYPE = 'MISTRAL+mistral-small-latest'                           # best
# CLOUD_TYPE = 'MISTRAL+pixtral-large-latest'                           # best
# CLOUD_TYPE = 'MISTRAL+pixtral-12b-2409'                               # good, free
# CLOUD_TYPE = 'MISTRAL+open-mistral-nemo'                              # not working, free

# Minimax
# CLOUD_TYPE = 'MINIMAX+MiniMax-M2'                                     # good, slow

# groq     
# CLOUD_TYPE = 'GROQ+qwen/qwen3-32b'                                    # best
# CLOUD_TYPE = 'GROQ+deepseek-r1-distill-llama-70b'                     # best
# CLOUD_TYPE = 'GROQ+llama-3.3-70b-versatile'                           # good
# CLOUD_TYPE = 'GROQ+moonshotai/kimi-k2-instruct'                       # best
# CLOUD_TYPE = 'GROQ+openai/gpt-oss-120b-medium'                        # best

# Perplexity     
# CLOUD_TYPE = 'PERPLEXITY+sonar'                                       # best ($ 1.00, $  1.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-search'                                # best ($ 1.00, $  1.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-pro'                                   # best ($ 3.00, $ 15.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-reasoning-low'                         # best ($ 1.00, $  5.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-reasoning-medium'                      # best ($ 1.00, $  5.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-reasoning-high'                        # best ($ 1.00, $  5.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-reasoning-pro-low'                     # best ($ 2.00, $  8.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-reasoning-pro-medium'                  # best ($ 2.00, $  8.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-reasoning-pro-high'                    # best ($ 2.00, $  8.00)
# CLOUD_TYPE = 'PERPLEXITY+sonar-deep-research-low'                     # best ($ 2.00, $  8.00) (+++ $2, $5, $3)

# Firekworks.ai
# CLOUD_TYPE = 'FIREWORKS+qwen2p5-72b-instruct'                         # good
# CLOUD_TYPE = 'FIREWORKS+qwen3-235b-a22b'                              # good
# CLOUD_TYPE = 'FIREWORKS+qwen3-30b-a3b'                                # good
# CLOUD_TYPE = 'FIREWORKS+llama4-maverick-instruct-basic'               # good
# CLOUD_TYPE = 'FIREWORKS+llama4-scout-instruct-basic'                  # good

# Openrouter.ai
# CLOUD_TYPE = 'OPENROUTER+openrouter/auto'                             # best
# CLOUD_TYPE = 'OPENROUTER+moonshotai/kimi-k2-0905'                     # best
# CLOUD_TYPE = 'OPENROUTER+moonshotai/kimi-k2-thinking'                 # best, slow, rate-limited
# CLOUD_TYPE = 'OPENROUTER+z-ai/glm-4.6'                                # best, slow
# CLOUD_TYPE = 'OPENROUTER+z-ai/glm-4.5v'                               # best
# CLOUD_TYPE = 'OPENROUTER+openai/gpt-5-mini'                           # best, slow
# CLOUD_TYPE = 'OPENROUTER+openai/gpt-oss-120b'                         # best

# Hugging Face
# CLOUD_TYPE = 'HF+meta-llama/Meta-Llama-3-8B-Instruct'                 # good
# CLOUD_TYPE = 'HF+meta-llama/Llama-3.1-70B-Instruct'                   # needs pro-subscription
# CLOUD_TYPE = 'HF+meta-llama/Llama-3.1-8B-Instruct'                    # needs pro-subscription

# Cerebras.ai
# CLOUD_TYPE = 'CEREBRAS+gpt-oss-120b-medium'                           # best
# CLOUD_TYPE = 'CEREBRAS+qwen-3-235b-a22b-instruct-2507'                # best (deprecated)
# CLOUD_TYPE = 'CEREBRAS+zai-glm-4.6'                                   # best

# Ollama (local models), best results *** not up-to-date ***
# CLOUD_TYPE = 'OLLAMA+qwen3'                                           # good (8b)
# CLOUD_TYPE = 'OLLAMA+qwen3:4b'                                        # good
# CLOUD_TYPE = 'OLLAMA+qwen3:7b'                                        # good
# CLOUD_TYPE = 'OLLAMA+qwen3:14b'                                       # good
# CLOUD_TYPE = 'OLLAMA+qwen3:32b'                                       # good
# CLOUD_TYPE = 'OLLAMA+qwen3:30b-a3b'                                   # good
# CLOUD_TYPE = 'OLLAMA+phi4:14b'                                        # best
# CLOUD_TYPE = 'OLLAMA+nemotron'                                        # best, slow
# CLOUD_TYPE = 'OLLAMA+wizardlm2'                                       # best
# CLOUD_TYPE = 'OLLAMA+llama3.2:3b'                                     # ok
# CLOUD_TYPE = 'OLLAMA+llama3.3:70b'                                    # best, slow
# CLOUD_TYPE = 'OLLAMA+mistral:7b'                                      # good
# CLOUD_TYPE = 'OLLAMA+mistral-small3.1:24b'                            # best
# CLOUD_TYPE = 'OLLAMA+mixtral'                                         # ok
# CLOUD_TYPE = 'OLLAMA+dolphin-mixtral'                                 # good
# CLOUD_TYPE = 'OLLAMA+gemma3:27b'                                      # best, slow
# CLOUD_TYPE = 'OLLAMA+gemma3:12b'                                      # does not work, most of the time (indentation problem)
# CLOUD_TYPE = 'OLLAMA+gemma3:12b-it-q8_0'                              # does not work, most of the time (indentation problem)
# CLOUD_TYPE = 'OLLAMA+gemma3:4b'                                       # does not work, most of the time (indentation problem)
# CLOUD_TYPE = 'OLLAMA+gemma3:1b'                                       # does not work

# LMStudio
# CLOUD_TYPE = 'LMSTUDIO+mlx-community/phi-4'                           # best
# CLOUD_TYPE = 'LMSTUDIO+nvidia_llama-3.1-nemotron-70b-instruct-hf'     # best, slow
# CLOUD_TYPE = 'LMSTUDIO+llama-3.3-70b-instruct'                        # best, slow
# CLOUD_TYPE = 'LMSTUDIO+qwen2.5-14b-instruct'                          # best
# CLOUD_TYPE = 'LMSTUDIO+qwen2.5-32b-instruct'                          # ok
# CLOUD_TYPE = 'LMSTUDIO+mlx-community/meta-llama-3.1-8b-instruct'      # ok
# CLOUD_TYPE = 'LMSTUDIO+lmstudio-community/meta-llama-3.1-8b-instruct' # ok

# GPT4All
# CLOUD_TYPE = 'GPT4ALL+Llama-3.2-1B-Instruct-Q4_0.gguf'                #
# CLOUD_TYPE = 'GPT4ALL+Llama-3.2-3B-Instruct-Q4_0.gguf'                # ok
# CLOUD_TYPE = 'GPT4ALL+Llama-3.3-70B-Instruct-Q4_K_M.gguf'             # best, slow

if sys.platform.startswith('win'):
    platform = "win"
elif sys.platform.startswith('darwin'):
    platform = "darwin"

def get_config(CLOUD_TYPE: str = CLOUD_TYPE) -> SimpleNamespace:
    config = SimpleNamespace(
        CLOUD_TYPE=CLOUD_TYPE
    )

    config.LOG = True
    config.TURBO_MODE = True # just generate text topics
    config.LLM_TEMPERATURE = 0.5
    config.MAX_RETRIES = 3


    config.SYSTEM_PROMPT = """
    You are a highly experienced business consultant with expertise in 
    strategic planning, financial analysis, marketing, and organizational development.
    Provide detailed, insightful, and professional advice tailored to the needs of business clients.
    Your responses should reflect the latest industry trends and best practices. /no_think
    """

    model = CLOUD_TYPE.split("+")[-1]
    config.MODEL_ID = model
    system = CLOUD_TYPE.split("+")[0]

    load_env(system)

    config.MULTIMODAL = False
    config.MULTIMODAL_MIME_TYPES = []
    config.MULTIMODAL_PDF_TO_IMAGE_DPI = 200
    config.MARKDOWN_OPTIMIZATION_LEVEL = 2
    config.OPENAI_COMPATIBILITY = True
    config.MAX_TOKENS = 4000
    config.HEADERS = {"Content-Type": "application/json"}
    config.REASONING_EFFORT = ""
    config.SEARCH_MODE = ""

    if "OPENAI+" in CLOUD_TYPE or "AZURE+" in CLOUD_TYPE or "OPENROUTER+" in CLOUD_TYPE or "GITHUB+" in CLOUD_TYPE:
        config.REASONING_EFFORT = ""
        reasoning_effort_value = ""
        reasoning_effort = model.split("-")[-1]
        if reasoning_effort in ["none", "minimal", "low", "medium", "high"]:
            reasoning_effort_value = reasoning_effort
        
        if "gpt-5" in model :
            config.MAX_TOKENS = 128000
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
            if reasoning_effort_value:
                config.REASONING_EFFORT = reasoning_effort_value
                config.MODEL_ID = model.replace(f"-{reasoning_effort_value}", "")
            else:
                config.REASONING_EFFORT = "low"
        elif "gpt-4o" in model:
            config.MAX_TOKENS = 16383
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
        elif "gpt-4.1" in model :
            config.MAX_TOKENS = 32767
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
        elif "o1-mini" in model:
            config.MAX_TOKENS = 65535
        elif "o1-" in model or "o3-" in model or "o4-" in model or model == "o1" or model == "o3" or model == "o4":
            config.MAX_TOKENS = 100000
            if reasoning_effort_value:
                config.REASONING_EFFORT = reasoning_effort_value
                config.MODEL_ID = model.replace(f"-{reasoning_effort_value}", "")
            else:
                config.REASONING_EFFORT = "low"
        elif "model-router" in model:
            config.MAX_TOKENS = 32768
            config.MULTIMODAL = False

    if "OPENAI+" in CLOUD_TYPE:
        config.API_URL = os.getenv('OPENAI_API_URL')

        if CLOUD_TYPE.startswith("OPENAI+o3-pro") or "+gpt-5.1" in CLOUD_TYPE:
            config.API_URL = os.getenv('OPENAI_API_URL').replace("chat/completions", "responses")
        
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('OPENAI_API_KEY') or "")}

    elif "AZURE+" in CLOUD_TYPE:
        config.USE_AZURE_ENTRA = os.getenv('AZURE_ENTRA_AUTH', '').lower() in ('true', '1', 'yes')
        config.AZURE_DEPLOYMENT = config.MODEL_ID
        config.API_VERSION = os.getenv('AZURE_API_VERSION')
        config.API_URL = (
            f"{os.getenv('AZURE_API_URL')}openai/deployments/"
            f"{config.MODEL_ID}/chat/completions"
            f"?api-version={config.API_VERSION}"
        )
        config.HEADERS = {**config.HEADERS, "api-key": os.getenv('AZURE_API_KEY') or ""}

    elif "OPENROUTER+" in CLOUD_TYPE:
        config.REASONING_EFFORT = ""
        config.MAX_TOKENS = 16384
        config.API_URL = os.getenv('OPENROUTER_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('OPENROUTER_API_KEY') or "")}
        config.PROVIDER_ORDER = None
        config.PROVIDER_ALLOW_FALLBACKS = False
        config.PROVIDER_DATA_COLLECTION = "deny"
        config.PROVIDER_SORT = "price"
        model_provider = model.split("/")[0]
        if model.lower() == "openrouter/auto":
            config.MAX_TOKENS = 16384
            # config.PROVIDER_ORDER = ["anthropic", "openai"]
        if model_provider.lower() == "moonshotai":
            config.MAX_TOKENS = 130000
        elif model_provider.lower() == "x-ai":
            if "4.6" in model:
                config.MAX_TOKENS = 128000
            elif "4.5v" in model:
                config.MAX_TOKENS = 16000
            elif "4.5" in model:
                config.MAX_TOKENS = 96000

    elif "GITHUB+" in CLOUD_TYPE:
        config.API_URL = os.getenv('GITHUB_MODELS_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('GITHUB_MODELS_TOKEN') or "")}

    elif "GEMINI" in CLOUD_TYPE or "VERTEXAI" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = False
        config.TOP_P = 0.95
        if "gemini-2.5" in model:
            config.MAX_TOKENS = 64000
            config.THINKING_BUDGET = 2048
        else:
            config.MAX_TOKENS = 8191
        config.MULTIMODAL = True
        config.MULTIMODAL_MIME_TYPES = ["application/pdf"]

        if system == "GEMINI":
            config.API_URL = f"{os.getenv('GEMINI_API_URL')}{model}:generateContent?key={os.getenv('GEMINI_API_KEY')}"
        elif system == "VERTEXAI":
            config.PROJECT_ID = os.getenv('VERTEXAI_PROJECT_ID')
            config.API_ENDPOINT = os.getenv('VERTEXAI_API_ENDPOINT')
            config.LOCATION_ID = os.getenv('VERTEXAI_LOCATION_ID')
            config.GCP_MODEL_VERSION_KEY = ""
            config.GCP_MODEL_VERSION_TEXT = ""
            if "anthropic/" in model:
                config.LOCATION_ID = "europe-west1"
                config.MAX_TOKENS = 64000
                model = model.replace("anthropic/", "")
                config.API_URL = (
                    f"https://{config.API_ENDPOINT}/v1/projects/{config.PROJECT_ID}/"
                    f"locations/{config.LOCATION_ID}/publishers/anthropic/models/{model}:rawPredict"
                )
                config.GCP_MODEL_VERSION_KEY = "anthropic_version"
                config.GCP_MODEL_VERSION_TEXT = "vertex-2023-10-16"
            else:
                config.API_URL = (
                    f"https://{config.API_ENDPOINT}/v1/projects/{config.PROJECT_ID}/"
                    f"locations/{config.LOCATION_ID}/publishers/google/models/{model}:generateContent"
                )
            config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('VERTEXAI_ACCESS_TOKEN') or "")}
            
            # Example GCP environment fields
            config.GCP_CLIENT_ID = os.getenv('GCP_CLIENT_ID')
            config.GCP_CLIENT_SECRET = os.getenv('GCP_CLIENT_SECRET')
            config.GCP_PROJECT_ID = config.PROJECT_ID
            config.GCP_ENDPOINT = config.API_ENDPOINT
            config.GCP_LOCATION = config.LOCATION_ID

    elif "BEDROCK" in CLOUD_TYPE:
        config.OPENAI_COMPATIBILITY = False
        config.AWS_ACCOUNT_ID = ""
        if model.startswith("amazon.titan-"):
            config.MAX_TOKENS = 3000
        elif model.startswith("amazon.nova-premier-"):
            config.MAX_TOKENS = 32000
            config.AWS_ACCOUNT_ID = os.getenv("BEDROCK_ACCOUNT_ID")
        elif model.startswith("amazon.nova-pro-"):
            config.MAX_TOKENS = 5120
        elif model.startswith("amazon.nova-lite-"):
            config.MAX_TOKENS = 5120
        elif "-sonnet-4-" in model:
            config.MAX_TOKENS = 64000
        config.AWS_ACCESS_KEY = os.getenv("BEDROCK_ACCESS_KEY")
        config.AWS_SECRET_KEY = os.getenv("BEDROCK_SECRET_KEY")
        config.AWS_SERVICE_NAME = "bedrock-runtime"
        config.AWS_MODEL_VERSION_KEY = ""
        config.AWS_MODEL_VERSION_TEXT = ""
        config.AWS_REGION = "us-east-1"
        if model.startswith("anthropic.") or ".anthropic." in model:
            config.AWS_MODEL_VERSION_KEY = "anthropic_version"
            config.AWS_MODEL_VERSION_TEXT = "bedrock-2023-05-31"

    elif "ANTHROPIC" in CLOUD_TYPE:
        if "claude-opus-4" in model:
            config.MAX_TOKENS = 32000
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["application/pdf"]
        elif "claude-sonnet-4" in model or "claude-haiku-4" in model:
            config.MAX_TOKENS = 64000
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["application/pdf"]
        elif "claude-3-7-sonnet" in model:
            config.MAX_TOKENS = 64000
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["application/pdf"]
        elif "claude-3-5" in model:
            config.MAX_TOKENS = 8192
            if "sonnet" in model:
                config.MULTIMODAL = True
                config.MULTIMODAL_MIME_TYPES = ["application/pdf"]
        config.ANTHROPIC_VERSION = os.getenv('ANTHROPIC_VERSION')
        config.API_URL = os.getenv('ANTHROPIC_API_URL')
        config.HEADERS = {
            **config.HEADERS, 
            "x-api-key": os.getenv('ANTHROPIC_API_KEY') or "", 
            "anthropic-version": os.getenv('ANTHROPIC_VERSION') or ""
        }

    elif "XAI+" in CLOUD_TYPE:
        if "-vision-" in model:
            config.MULTIMODAL = True
            config.MULTIMODAL_MIME_TYPES = ["image/jpeg", "image/png"]
        if "grok-4-fast-" in model:
            config.MAX_TOKENS = 128000
        config.API_URL = os.getenv('XAI_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('XAI_API_KEY') or "")}

    elif "MINIMAX+" in CLOUD_TYPE:
        config.MAX_TOKENS = 128000
        config.API_URL = os.getenv('MINIMAX_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('MINIMAX_API_KEY') or "")}

    elif "GROQ+" in CLOUD_TYPE:
        config.REASONING_EFFORT = ""
        if "qwen/qwen3" in model:
            config.MAX_TOKENS = 130000
        elif "deepseek-r1" in model:
            config.MAX_TOKENS = 130000
        elif "llama-3.3-70b-versatile" in model:
            config.MAX_TOKENS = 32766
        elif "moonshot/kimi-k2-instruct" in model:
            config.MAX_TOKENS = 16384
        elif "openai/gpt-oss-" in model:
            config.MAX_TOKENS = 32766
            reasoning_effort = model.split("-")[-1]
            if reasoning_effort in ["low", "medium", "high"]:
                config.REASONING_EFFORT = reasoning_effort
                config.MODEL_ID = model.replace(f"-{reasoning_effort}", "")
        config.API_URL = os.getenv('GROQ_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('GROQ_API_KEY') or "")}

    elif "CEREBRAS+" in CLOUD_TYPE:
        config.MAX_TOKENS = 64000
        config.API_URL = os.getenv('CEREBRAS_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('CEREBRAS_API_KEY') or "")}
        config.REASONING_EFFORT = ""
        reasoning_effort = model.split("-")[-1]
        if reasoning_effort == "pro":
            reasoning_effort = ""
        if reasoning_effort in ["low", "medium", "high"]:
            config.REASONING_EFFORT = reasoning_effort
            config.MODEL_ID = model.replace(f"-{reasoning_effort}", "")

    elif "PERPLEXITY+" in CLOUD_TYPE:
        config.MAX_TOKENS = 8000
        config.API_URL = os.getenv('PERPLEXITY_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('PERPLEXITY_API_KEY') or "")}
        if "-reasoning-" in model or "-research-" in model:
            reasoning_effort = model.split("-")[-1]
            if reasoning_effort in ["low", "medium", "high"]:
                config.REASONING_EFFORT = reasoning_effort
                config.MODEL_ID = model.replace(f"-{reasoning_effort}", "")
            else:
                config.REASONING_EFFORT = "low"
        if "-search" in model:
            config.SEARCH_MODE = "web"
            config.SEARCH_MAX_RESULTS = 5
            config.SEARCH_RECENCY_FILTER = "week"
            config.MODEL_ID = model.replace(f"-search", "")

    elif "STACKIT+" in CLOUD_TYPE:
        config.MAX_TOKENS = 4096
        config.API_URL = f"{os.getenv('STACKIT_API_URL')}/chat/completions"
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('STACKIT_API_KEY') or "")}

    elif "DEEPSEEK+" in CLOUD_TYPE:
        config.MAX_TOKENS = 8000
        if "deepseek-reasoner" in model:
            config.MAX_TOKENS = 64000
        config.API_URL = os.getenv('DEEPSEEK_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('DEEPSEEK_API_KEY') or "")}

    elif "ALIBABACLOUD+" in CLOUD_TYPE:
        config.MAX_TOKENS = 32768
        config.API_URL = os.getenv('ALIBABACLOUD_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('ALIBABACLOUD_API_KEY') or "")}
        config.TOP_P = 0.8
        config.ENABLE_THINKING = False
        config.THINKING_BUDGET = 0
        if model in ["qwen-max-2025-01-25", "qwen-turbo-2025-04-28"]:
            config.MAX_TOKENS = 8192

    elif "MISTRAL+" in CLOUD_TYPE:
        config.API_URL = os.getenv('MISTRAL_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('MISTRAL_API_KEY') or "")}

    elif "HF+" in CLOUD_TYPE:
        config.API_URL = f"{os.getenv('HF_API_URL')}{model}/v1/chat/completions"
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('HF_API_KEY') or "")}

    elif "FIREWORKS+" in CLOUD_TYPE:
        model_prefix = "accounts/fireworks/models/"
        config.MODEL_ID = model_prefix + model
        config.API_URL = os.getenv('FIREWORKS_API_URL')
        config.HEADERS = {**config.HEADERS, "Authorization": "Bearer " + (os.getenv('FIREWORKS_API_KEY') or "")}

    # local systems

    elif "OLLAMA+" in CLOUD_TYPE:
        config.API_URL = os.getenv('OLLAMA_API_URL')

    elif "LMSTUDIO+" in CLOUD_TYPE:
        config.API_URL = os.getenv('LMSTUDIO_API_URL')
        if not config.API_URL.endswith("/chat/completions"):
            config.API_URL += "/chat/completions"

    elif "GPT4ALL+" in CLOUD_TYPE:
        config.MAX_TOKENS = 2000
        config.DEVICE = "gpu"
        config.ALLOW_DOWNLOAD = False
        if platform == "darwin":
            config.MODEL_PATH = os.path.join(os.path.expanduser("~"),"Library","Application Support","nomic.ai","GPT4ALL")
        else: 
            model_path = os.getenv('GPT4ALL_MODEL_PATH_WINDOWS')
            if model_path != "":
                config.MODEL_PATH = model_path.upper().replace("%LOCALAPPDATA%", os.getenv('LOCALAPPDATA'))
        config.API_URL = ""

    else:
        raise Exception("Error: Unknown CLOUD_TYPE")

    return config
