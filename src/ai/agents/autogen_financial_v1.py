import os
import sys
from datetime import datetime, timedelta
import asyncio

import yfinance as yf
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

import llms.autogen as ai

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import file_helper as fh

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
        model_client = self.llms[0]
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
