import os
import sys

from crewai import LLM
from langchain.llms import Ollama

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import file_helper as fh

def load_model(cloud_type: str):
    system = cloud_type.split("+")[0]
    model = cloud_type.split("+")[-1]
    llm = None
    if system.lower() == "azure":
        llm = LLM(
            model = f"{system.lower()}/{model.lower()}",
            api_version = os.getenv('AZURE_API_VERSION'),
            api_key = os.getenv('AZURE_API_KEY'),
            base_url = os.getenv('AZURE_API_URL')
        )
    elif system.lower() == "openai":
        llm = LLM(
            model = f"{system.lower()}/{model.lower()}",
            api_key = os.getenv('OPENAI_API_KEY')
        )
    elif system.lower() == "ollama":
        llm = LLM(
            model = f"{system.lower()}/{model.lower()}",
            base_url = os.getenv('OLLAMA_API_URL').replace("/v1/chat/completions", "")
        )
    elif system.lower() == "xai":
        llm = LLM(
            model = f"{system.lower()}/{model.lower()}",
            api_key = os.getenv('XAI_API_KEY'),
            base_url = os.getenv('XAI_API_URL').replace("/chat/completions", "")
        )
    elif system.lower() == "deepseek":
        llm = LLM(
            model = f"{system.lower()}/{model.lower()}",
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
