import os
import sys

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import file_helper as fh

def load_model(cloud_type: str):
    system = cloud_type.split("+")[0]
    model = cloud_type.split("+")[-1]
    llm = None
    if system.lower() == "azure":
        llm = AzureOpenAIChatCompletionClient(
            azure_deployment = model,
            model = model,
            api_version = os.getenv('AZURE_API_VERSION'),
            azure_endpoint = os.getenv('AZURE_API_URL'),
            api_key = os.getenv('AZURE_API_KEY'),
        )
    elif system.lower() == "openai":
        llm = OpenAIChatCompletionClient(
            model = model,
            api_key = os.getenv('OPENAI_API_KEY')
        )
    elif system.lower() == "ollama":
        llm = OpenAIChatCompletionClient(
            model = model,
            base_url = os.getenv('OLLAMA_API_URL').replace("/chat/completions", ""),
            api_key = "placeholder",
            model_info = {
                "vision": False,
                "function_calling": True,
                "json_output": False,
                "family": "unknown",
            },
        )
    elif system.lower() == "xai":
        llm = OpenAIChatCompletionClient(
            model = model,
            base_url = os.getenv('XAI_API_URL').replace("/chat/completions", ""),
            api_key = os.getenv('XAI_API_KEY'),
            model_info = {
                "vision": False,
                "function_calling": True,
                "json_output": False,
                "family": "unknown",
            },
        )
    elif system.lower() == "deepseek":
        llm = OpenAIChatCompletionClient(
            model = model,
            base_url = os.getenv('DEEPSEEK_API_URL').replace("/beta/chat/completions", ""),
            api_key = os.getenv('DEEPSEEK_API_KEY'),
            model_info = {
                "vision": False,
                "function_calling": True,
                "json_output": False,
                "family": "unknown",
            },
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
