import os
import sys
from datetime import datetime, timedelta
from dotenv import dotenv_values
import yfinance as yf
from crewai import Agent, Task, Crew, Process, LLM
from langchain.tools import Tool
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain.llms import Ollama
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

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
                llm = Ollama(
                    model=cloud_type.split("+")[-1],
                    base_url=os.getenv('OLLAMA_API_URL'),
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
        import yfinance as yf

        from crewai import Agent, Task, Crew, Process, LLM

        from langchain.tools import Tool
        from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults

        import pandas as pd

        def fetch_stock_price(ticket):
            if not isinstance(ticket, str):
                raise ValueError(f"Expected ticket to be a string, but got {type(ticket)}: {ticket}")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            stock = yf.download(ticket, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            if not isinstance(stock, pd.DataFrame) or stock.empty:
                raise ValueError(f"Imvalid stock data for {ticket}: {stock}")
            return stock

        yahoo_finance_tool = Tool(
            name="Yahoo Finance Tool",
            description="Fetches stocks prices for a given stock ticker symbol (e.g., AAPL) from Yahoo Finance API for the last month. **Input should be a string representing the ticker symbol.**",
            func=fetch_stock_price  # Direct function call, Tool handles the input
        )

        stockPriceAnalyst = Agent(
            role="Senior Stock Price Analyst",
            goal="Find the current trend of the {ticket} stock price (up, down, or sideways) by analyzing recent price history. **Use the 'Yahoo Finance Tool' to get the price data. Remember the tool requires the stock ticker as a simple string (e.g., 'AAPL').**",
            backstory="""You're highly experienced in analyzing the price of a specific stock
            and identifying its current trend based on recent price movements. You are meticulous about using tools correctly and understand that the 'Yahoo Finance Tool' requires a plain string as input for the stock ticker symbol. You will ensure to provide the ticker in the correct format.""",
            verbose=True,
            llm=self.llm,
            max_iter=5,
            memory=True,
            tools=[yahoo_finance_tool],
            allow_delegation=False
        )

        getStockPrice = Task(
            description="Analyze the recent stock price history for {ticket} and determine the current trend: up, down, or sideways. **Use the 'Yahoo Finance Tool' to fetch the stock data. When using the tool, provide the stock ticker symbol as a plain text string (e.g., 'AAPL'). Do not pass a dictionary or any other complex object.**",
            expected_output="""
            The current trend of the stock price (up, down, or sideways).
            Example: 'The current trend for AAPL is UP.'
            """,
            agent=stockPriceAnalyst
        )

        search_tool = Tool(
            name="DuckDuckGoNewsSearch",
            description="Searches DuckDuckGo for recent news articles about a given query. **Input should be a string representing the search query.**",
            func=lambda query: DuckDuckGoSearchResults(backend='news', num_results=5).run(query)
        )

        newsAnalyst = Agent(
            role="Stock News Analyst",
            goal="""Create a concise summary of recent market news related to the stock {ticket} company.
            Determine the overall market sentiment (fear or greed) and assign a fear/greed score between 0 and 100 for each asset. **Use the 'DuckDuckGoNewsSearch' tool to find relevant news. Remember the tool requires a search query string.**""",
            backstory="""You're highly experienced in analyzing market trends and news, having tracked assets for over 10 years.
            You have a deep understanding of market sentiment and human psychology, especially as it relates to financial markets.
            You analyze news articles critically, considering the source and potential biases. You understand that the 'DuckDuckGoNewsSearch' tool requires a text-based search query.""",
            verbose=True,
            llm=self.llm,
            max_iter=10,
            memory=True,
            tools=[search_tool],
            allow_delegation=False
        )

        current_datetime = datetime.now()
        get_news = Task(
            description=f"""Search for recent news articles related to {{ticket}}. **Use the 'DuckDuckGoNewsSearch' tool for this. Construct appropriate search queries the stock ticker.**
            Analyze the news to determine the market sentiment for each asset and assign a fear/greed score (0-100).
            The current date is {current_datetime}.
            Compose the results into a helpful report. Focus on the most impactful news.""",
            expected_output="""
            Report summarizing the news for {{ticket}}, including a fear/greed score for each.
            Format:
            {{ticket}}: <SUMMARY BASED ON NEWS>, Fear/Greed Score: <SCORE>
            """,
            agent=newsAnalyst
        )

        stockAnalystWrite = Agent(
            role="Senior Stock Analyst Writer",
            goal="""Analyze the provided stock price trend and news report to write an insightful and informative 3-paragraph newsletter about the {ticket} company.""",
            backstory="""You are a widely respected stock analyst known for your ability to synthesize complex information into compelling and easily understandable narratives.
            You understand macro factors and combine various analytical approaches to provide well-rounded insights.
            You can present balanced perspectives even when analyzing volatile market situations.
        """,
            verbose=True,
            llm=self.llm,
            max_iter=5,
            memory=True,
            allow_delegation=True
        )

        writeAnalyses = Task(
            description="""Using the provided stock price trend and news report for {ticket}, create a brief newsletter (3 paragraphs) highlighting the most important points.
            Focus on the stock price trend, relevant news, and the fear/greed score. Discuss potential near-future considerations for investors.
            Incorporate the previous analysis of the stock trend and the news summary in your newsletter.
        """,
            expected_output="""
            A concise 3-paragraph newsletter in markdown format. It should contain:

            - **Executive Summary:** 2-3 bullet points summarizing key findings.
            - **Introduction:** Briefly set the stage and pique the reader's interest.
            - **Analysis:**  Present the core analysis, integrating the stock price trend, news summary, and fear/greed score.
            - **Outlook:** Conclude with key takeaways and a concise prediction of the near-term trend (up, down, or sideways).
        """,
            agent=stockAnalystWrite,
            context=[getStockPrice, get_news]
        )

        crew = Crew(
            agents=[stockPriceAnalyst, newsAnalyst, stockAnalystWrite],
            tasks=[getStockPrice, get_news, writeAnalyses],
            verbose=False,
            process=Process.hierarchical,
            full_output=False,
            share_crew=False,
            manager_llm=self.llm,
            max_iter=15
        )

        results = crew.kickoff(inputs={'ticket': argument})

        if simple_result:
            return results.raw
        return results

def main():
    m_agent = MAgent()
    results = m_agent.execute(simple_result=False)
    print(results)

if __name__ == "__main__":
    main()
