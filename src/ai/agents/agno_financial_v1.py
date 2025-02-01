import os
import sys
from typing import Iterator
from dotenv import dotenv_values

from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.models.xai import xAI
from agno.models.deepseek import DeepSeek
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import file_helper as fh

# CLOUD_TYPE = 'AZURE+gpt-4o-mini'
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini'
# CLOUD_TYPE = 'OLLAMA+llama3.2:3b'
# CLOUD_TYPE = 'XAI+grok-2-1212'
CLOUD_TYPE = 'DEEPSEEK+deepseek-chat'

class MAgent:
    def __init__(self, cloud_type: str = CLOUD_TYPE, secondary_cloud_type: str = CLOUD_TYPE):

        def load_env(cloud_type: str):
            system = cloud_type.split("+")[0]
            fh.load_env(system)

        def load_model(cloud_type: str):
            system = cloud_type.split("+")[0]
            model = cloud_type.split("+")[-1]
            llm = None
            if system.lower() == "azure":
                llm = AzureOpenAI(
                    id = f"{system.lower()}/{model.lower()}",
                    api_version = os.getenv('AZURE_API_VERSION'),
                    api_key = os.getenv('AZURE_API_KEY'),
                    azure_endpoint=os.getenv('AZURE_API_URL'),
                    azure_deployment=model,
                )
            elif system.lower() == "openai":
                llm = OpenAIChat(
                    id=cloud_type.split("+")[-1],
                    api_key=os.getenv('OPENAI_API_KEY')
                )
            elif system.lower() == "ollama":
                llm = Ollama(
                    id=cloud_type.split("+")[-1],
                    host=os.getenv('OLLAMA_API_URL').replace("/v1/chat/completions", "")
                )
            elif system.lower() == "xai":
                llm = xAI(
                    id=cloud_type.split("+")[-1],
                    api_key=os.getenv('XAI_API_KEY'),
                    base_url=os.getenv('XAI_API_URL').replace("/chat/completions", "")
                )
            elif system.lower() == "deepseek":
                llm = DeepSeek(
                    id=cloud_type.split("+")[-1],
                    api_key=os.getenv('DEEPSEEK_API_KEY'),
                    base_url=os.getenv('DEEPSEEK_API_URL').replace("/beta/chat/completions", "")
                )
            else:
                raise ValueError("Invalid system specified.")
            return llm
                
        os.environ["OTEL_SDK_DISABLED"] = "true"
        load_env(cloud_type)
        load_env(secondary_cloud_type)
        self.llm = load_model(cloud_type)
        if cloud_type != secondary_cloud_type:
            self.secondary_llm = load_model(secondary_cloud_type)
        else:
            self.secondary_llm = self.llm

    def execute(self, argument: str = 'NVDA', simple_result: bool = True, show_tool_calls: bool = False) -> str:
        web_agent = Agent(
            name="Web Agent",
            role="Search the web for information",
            model=self.llm,
            tools=[DuckDuckGoTools()],
            #instructions=["Always include sources"],
            show_tool_calls=show_tool_calls,
            markdown=True,
        )

        finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data",
            model=self.llm,
            tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
            #instructions=["Use tables to display data"],
            show_tool_calls=show_tool_calls,
            markdown=True,
        )

        agent_team = Agent(
            team=[web_agent, finance_agent],
            model=self.llm,
            #instructions=["Always include sources", "Use tables to display data"],
            show_tool_calls=show_tool_calls,
            markdown=True,
        )

        strTopic = f"Summarize analyst recommendations and share the latest news for {argument}"
        if simple_result:
            response = agent_team.run(strTopic, stream=False)
            return response.content
        else:
            agent_team.print_response(strTopic, stream=True)
            return

def main():
    m_agent = MAgent()
    results = m_agent.execute(simple_result=False, show_tool_calls=True)
    print(results)

if __name__ == "__main__":
    main()
