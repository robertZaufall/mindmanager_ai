import config

from openai import AzureOpenAI
from azure.identity import get_bearer_token_provider, InteractiveBrowserCredential

def call_llm_azure_entra(str_user):
    token_provider = get_bearer_token_provider(
        InteractiveBrowserCredential(),
        "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        azure_endpoint = config.OPENAI_API_URL,
        azure_ad_token_provider = token_provider,
        api_version = config.OPENAI_API_VERSION
    )
    
    response = client.chat.completions.create(
        model = config.OPENAI_DEPLOYMENT,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": str_user},
        ]
    )

    result = response.choices[0].message.content.replace("```mermaid", "").replace("```", "").lstrip("\n")    
    return result
