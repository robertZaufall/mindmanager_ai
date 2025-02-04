import os
import sys
from datetime import datetime, timedelta
from typing import Iterator
from dotenv import dotenv_values
import yfinance as yf

import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import file_helper as fh

CLOUD_TYPE = 'AZURE+gpt-4o-mini'
# CLOUD_TYPE = 'OPENAI+gpt-4o-mini'
# CLOUD_TYPE = 'OLLAMA+llama3.2:3b'
# CLOUD_TYPE = 'XAI+grok-2-1212'
# CLOUD_TYPE = 'DEEPSEEK+deepseek-chat'

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
                
        os.environ["OTEL_SDK_DISABLED"] = "true"
        load_env(cloud_type)
        load_env(secondary_cloud_type)
        self.llm = load_model(cloud_type)
        if cloud_type != secondary_cloud_type:
            self.secondary_llm = load_model(secondary_cloud_type)
        else:
            self.secondary_llm = self.llm

    def analyze_stock(self, ticker: str) -> dict:
        # Create a yfinance Ticker object
        stock = yf.Ticker(ticker)
        
        # Get historical data for the past 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return {"error": f"No historical data available for ticker '{ticker}'."}
        
        # Compute the starting and current (latest) closing prices
        start_price = hist["Close"].iloc[0]
        current_price = hist["Close"].iloc[-1]
        
        # Calculate the percentage change over the period
        pct_change = ((current_price - start_price) / start_price) * 100
        
        # Return the analysis results in a dictionary
        return {
            "ticker": ticker,
            "start_price": start_price,
            "current_price": current_price,
            "pct_change": pct_change
        }

    # Define the asynchronous financial analyst function using AutoGen AgentChat.
    async def financial_analyst(self, ticker: str) -> str:
        model_client = self.llm
        analyst_agent = AssistantAgent("FinancialAnalyst", model_client)
        
        # Use the tool function to fetch stock data and perform basic analysis.
        stock_info = self.analyze_stock(ticker)
        if "error" in stock_info:
            return stock_info["error"]
        
        # Construct a report message that includes the key figures and plot path.
        report = (
            f"Financial Analysis for {stock_info['ticker']}:\n\n"
            f"Starting Price (30 days ago): ${stock_info['start_price']:.2f}\n"
            f"Current Price: ${stock_info['current_price']:.2f}\n"
            f"Percentage Change: {stock_info['pct_change']:.2f}%\n\n"
            "Please provide a brief commentary on these figures."
        )
        
        # Have the agent process the report message (this call may augment or rephrase the analysis).
        analysis_response = await analyst_agent.run(task=report)

        result = analysis_response.messages[-1].content
        return result

    async def run(self, argument: str = 'NVDA'):
        result = await self.financial_analyst(argument)
        return result

    def execute(self, argument: str = 'NVDA'):
        result = asyncio.run(self.run())
        return result.replace("TERMINATE", "").strip()

def main():
    m_agent = MAgent()
    results = m_agent.execute()
    print(results)

if __name__ == "__main__":
    main()
