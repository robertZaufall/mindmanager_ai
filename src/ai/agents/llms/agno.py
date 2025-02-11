import os
import sys

from agno.models.azure import AzureOpenAI
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.models.deepseek import DeepSeek

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import file_helper as fh

def load_model(cloud_type: str):
    system = cloud_type.split("+")[0]
    model = cloud_type.split("+")[-1]
    llm = None
    if system.lower() == "azure":
        llm = AzureOpenAI(
            id = f"{system.lower()}/{model.lower()}",
            api_version = os.getenv('AZURE_API_VERSION'),
            api_key = os.getenv('AZURE_API_KEY'),
            azure_endpoint = os.getenv('AZURE_API_URL'),
            azure_deployment = model,
        )
    elif system.lower() == "openai":
        llm = OpenAIChat(
            id = model,
            api_key = os.getenv('OPENAI_API_KEY')
        )
    elif system.lower() == "ollama":
        llm = Ollama(
            id = model,
            host = os.getenv('OLLAMA_API_URL').replace("/v1/chat/completions", "")
        )
    elif system.lower() == "xai":
        llm = xAI(
            id = model,
            api_key = os.getenv('XAI_API_KEY'),
            base_url = os.getenv('XAI_API_URL').replace("/chat/completions", "")
        )
    elif system.lower() == "deepseek":
        llm = DeepSeek(
            id = model,
            api_key = os.getenv('DEEPSEEK_API_KEY'),
            base_url = os.getenv('DEEPSEEK_API_URL').replace("/beta/chat/completions", "")
        )
    else:
        raise ValueError("Invalid system specified.")
    return llm

def load_models(cloud_types: list[str]):
    os.environ["OTEL_SDK_DISABLED"] = "true"
    llms = []
    for cloud_type in cloud_types:
        system = cloud_type.split("+")[0]
        fh.load_env(system)
        llms.append(load_model(cloud_type))
    return llms
