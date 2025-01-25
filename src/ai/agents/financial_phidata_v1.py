import os
import sys
from typing import Iterator
from phi.agent import Agent
from phi.model.azure import AzureOpenAIChat
from phi.model.openai import OpenAIChat
from phi.model.ollama import Ollama
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from dotenv import dotenv_values

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import file_helper as fh

CLOUD_TYPE = "AZURE+gpt-4o-mini"

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
                llm = AzureOpenAIChat(
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
                    host=os.getenv('OLLAMA_API_URL'),
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

    def execute(self, argument: str = 'NVDA', simple_result: bool = True):
        web_agent = Agent(
            name="Web Agent",
            role="Search the web for information",
            model=self.llm,
            tools=[DuckDuckGo()],
            #instructions=["Always include sources"],
            show_tool_calls=False,
            markdown=True,
        )

        finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data",
            model=self.llm,
            tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
            #instructions=["Use tables to display data"],
            show_tool_calls=False,
            markdown=True,
        )

        agent_team = Agent(
            team=[web_agent, finance_agent],
            model=self.llm,
            #instructions=["Always include sources", "Use tables to display data"],
            show_tool_calls=False,
            markdown=True,
        )

        response = agent_team.run(f"Summarize analyst recommendations and share the latest news for {argument}", stream=False)
        if simple_result:
            return response.content
        else:
            print(response)
            return

def main():
    m_agent = MAgent()
    results = m_agent.execute(simple_result=False)
    print(results)

if __name__ == "__main__":
    main()
