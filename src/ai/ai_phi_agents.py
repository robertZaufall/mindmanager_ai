import os
import sys

from typing import Iterator

from phi.agent import Agent
#from phi.model.openai import OpenAIChat
from phi.model.azure import AzureOpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config as cfg

config = cfg.get_config("AZURE+gpt-4o-mini")

azure_model = AzureOpenAIChat(
    id=config.OPENAI_DEPLOYMENT,
    api_key=config.OPENAI_API_KEY,
    azure_endpoint=config.OPENAI_API_URL,
    azure_deployment=config.OPENAI_DEPLOYMENT
)

web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    #model=OpenAIChat(id="gpt-4o"),
    mode=azure_model,
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=False,
    markdown=False,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    #model=OpenAIChat(id="gpt-4o"),
    model=azure_model,
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=False,
    markdown=False,
)

agent_team = Agent(
    team=[web_agent, finance_agent],
    #model=OpenAIChat(id="gpt-4o"),
    model=azure_model,
    instructions=["Return the relevant information as a mermaid mindmap with no additional information or text in the response"],
    show_tool_calls=False,
    markdown=False,
)

agent_team.print_response("Summarize analyst recommendations and share the latest news for NVDA, TSLA", stream=False)
