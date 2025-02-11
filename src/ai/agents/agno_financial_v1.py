from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

import llms.agno as ai

CLOUD_TYPE = 'AZURE+gpt-4o-mini'
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini'
# CLOUD_TYPE = 'OLLAMA+llama3.2:3b'
# CLOUD_TYPE = 'XAI+grok-2-1212'
# CLOUD_TYPE = 'DEEPSEEK+deepseek-chat'

class MAgent:
    def __init__(self, cloud_type: str = CLOUD_TYPE, secondary_cloud_type: str = CLOUD_TYPE):
        self.llms = ai.load_models([cloud_type, secondary_cloud_type])
        if len(self.llms) == 0:
            raise ValueError("No models loaded")

    def execute(self, argument: str = 'NVDA', simple_result: bool = True, show_tool_calls: bool = False) -> str:
        web_agent = Agent(
            name="Web Agent",
            role="Search the web for information",
            model=self.llms[0],
            tools=[DuckDuckGoTools()],
            #instructions=["Always include sources"],
            show_tool_calls=show_tool_calls,
            markdown=True,
        )

        finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data",
            model=self.llms[0],
            tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
            #instructions=["Use tables to display data"],
            show_tool_calls=show_tool_calls,
            markdown=True,
        )

        agent_team = Agent(
            team=[web_agent, finance_agent],
            model=self.llms[0],
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
