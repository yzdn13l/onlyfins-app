
import os

from dotenv import load_dotenv
load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

from datetime import datetime, timedelta
import requests
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from agents import function_tool
from agents import WebSearchTool
from pydantic import BaseModel
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import asyncio
from typing import Optional, List, Dict

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

class StockData(BaseModel):
    symbol: str
    dates: List[str]
    prices: List[Dict[str, float]]
    news: List[Dict[str, str]]
    start_date: str
    end_date: str

@function_tool
async def get_stock_data(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> StockData:
    """
    Get the price and related news of the specified stock within the given time range
    
    Args:
        symbol: Stock symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    # If no date is specified, default to the last 30 days
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # Convert date strings to datetime objects for comparison
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # Get stock price data
    price_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    price_response = requests.get(price_url)
    price_data = price_response.json()

    # Process price data
    prices = []
    dates = []
    if "Time Series (Daily)" in price_data:
        time_series = price_data["Time Series (Daily)"]
        for date, values in time_series.items():
            date_dt = datetime.strptime(date, '%Y-%m-%d')
            if start_date_dt <= date_dt <= end_date_dt:
                dates.append(date)
                prices.append({
                    "close": float(values["4. close"]),
                    "volume": float(values["5. volume"])
                })

    try:
        # Get news data
        start_date_api = datetime.strftime(start_date_dt, '%Y%m%dT0000')
        end_date_api = datetime.strftime(end_date_dt, '%Y%m%dT0000')
        news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&time_from={start_date_api}&time_to={end_date_api}&sort=RELEVANCE&limit=10&apikey={ALPHA_VANTAGE_API_KEY}"
        news_response = requests.get(news_url)
        news_data = news_response.json()

        # Process news data
        news = []
        # only keep top 5 news
        if "feed" in news_data:
            for article in news_data["feed"]:
                if len(news) >= 5:
                    break
                article_date = article["time_published"][:-2] # in format '20250316T180000'
                article_date = datetime.strptime(article_date, '%Y%m%dT%H%M')
                if start_date_dt <= article_date <= end_date_dt:
                    news.append({
                        "date": article_date.strftime('%Y-%m-%d'),
                        "title": article["title"],
                        "summary": article["summary"],
                        "url": article["url"],
                        "sentiment": str(article.get("overall_sentiment_score", 0)),
                    })
                
    except Exception as e:
        print(f"Error getting news data: {str(e)}")

    return StockData(
        symbol=symbol,
        dates=dates,
        prices=prices,
        news=news,
        start_date=start_date,
        end_date=end_date
    )



# First, define the output model
class NewsEvent(BaseModel):
    date: str
    title: str
    summary: str
    sentiment: float
    importance_score: float

class VisualizationOutput(BaseModel):
    plot_html: str

# # Create visualization function tool
# @function_tool
# async def create_interactive_plot(stock_data: StockData, news_events: List[NewsEvent]) -> str:
#     """Create an interactive chart"""
    
#     # Create price data
#     df = pd.DataFrame(dates=stock_data.dates, prices=stock_data.prices)
    
#     # Create main chart
#     fig = make_subplots(rows=2, cols=1, 
#                         row_heights=[0.7, 0.3],
#                         shared_xaxes=True)
    
#     # Add price line
#     fig.add_trace(
#         go.Scatter(x=df['date'], y=df['close'], 
#                   name='Stock Price',
#                   line=dict(color='#17BECF')),
#         row=1, col=1
#     )
    
#     # Add volume
#     fig.add_trace(
#         go.Bar(x=df['date'], y=df['volume'],
#                name='Volume'),
#         row=2, col=1
#     )
    
#     # Add news event markers
#     for event in news_events:
#         fig.add_trace(
#             go.Scatter(
#                 x=[event.date],
#                 y=[df[df['date'] == event.date]['close'].values[0]],
#                 mode='markers',
#                 marker=dict(
#                     size=10,
#                     symbol='star',
#                     color='red',
#                 ),
#                 name=event.title,
#                 text=event.summary,
#                 hoverinfo='text'
#             ),
#             row=1, col=1
#         )
    
#     # Update layout
#     fig.update_layout(
#         title=f"Stock Price Analysis for {stock_data.symbol}",
#         hovermode='x unified',
#         showlegend=True
#     )
    
#     # save the plot locally
#     save_path = 'stock_analysis_plot.html'
#     fig.write_html(save_path)
    
#     return VisualizationOutput(plot_html=save_path)

class NewsAnalysisOutput(BaseModel):
    major_events: List[NewsEvent]
    summary_report: str


# Create Stock Analysis Agent
stock_analyzer_agent = Agent(
    name="Stock Analyzer",
    instructions="""
    Analyze stock-related news within a given time period:
    1. Identify the 3-5 most important news events
    2. Evaluate the importance of each event based on the news content and sentiment score
    3. Generate a concise summary report explaining how these events impact the stock price
    4. Attach the link to 3-5 most important news events to the output
    
    Your summary report should follow this structure if the user asks about a stock:
    - Stock price trend analysis
    - Top news events related to the stock
    - Impact of news events on the stock price
    """,
    # output_type=NewsAnalysisOutput,
    tools=[get_stock_data]
)

# Create News Analyzer Agent
news_analyzer_agent = Agent(
    name="News Analyzer",
    instructions="""
    Given the news mentioned by the user, do each of the following:
    1. Search the internet for the exact time of the news event that happens. If the 
       news event is not specific, retrieve the most recent event.
    2. Decide a reasonable timeframe for the news event before and after the exact time
    3. Return the news event and the stock price data within the timeframe
    4. Generate a report on the impact of the news event on the stock price
    
    Your summary report should follow this structure if the user mentions a news event:
    - News event details
    - Stock price trend analysis around the news event
    - Impact of the news event on the stock price
    """,
    # output_type=NewsAnalysisOutput,
    tools=[WebSearchTool(), get_stock_data]
)

# # Create Visualization Agent
# visualization_agent = Agent(
#     name="Visualization Agent",
#     instructions="""
#     Create an interactive time series visualization:
#     1. Use Plotly to plot the stock price trend
#     2. Mark important news events on the chart
#     3. Add hover tips to display news details
#     4. Ensure the visual presentation is clear and intuitive
    
#     The output will be an HTML string that saved locally containing the interactive chart.
#     """,
#     output_type=VisualizationOutput,
#     tools=[get_stock_data, 
#            news_analyzer_agent.as_tool(
#                tool_name="news_analyzer",
#                tool_description="Analyze stock-related news within a given time period"
#            )]
# )

# Create event trace back agent


# Create input guardrail
class EventTraceBackOutput(BaseModel):
    is_stock: bool
    is_news: bool
    reason: str
    
guardrail_agent = Agent(
    name="Guardrail Agent",
    instructions="Check if the user is asking for a stock related analysis or a news event analysis",
    output_type=EventTraceBackOutput,
)

async def guardrail_function(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(EventTraceBackOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_stock and not final_output.is_news
    )

# Main Agent
orchestrator = Agent(
    name="Orchestrator",
    instructions="""
    You are a financial expert who can provide insights on stock analysis and news events.
    You will analyze the user's input and provide relevant information based on the context.
    
    If the user is interested in the volatility of a stock during a specific time period, pass the request to the stock analyzer agent.
    
    If the user mentions a news event without specifying a specific time, pass the request
       to the news analyzer agent to analyze the impact of the news event on the stock price.
    
    Provide a summary report with the key findings and insights.
    """,
    handoffs=[
        stock_analyzer_agent,
        news_analyzer_agent
    ],
    # input_guardrails=[
    #     InputGuardrail(guardrail_function=guardrail_function)
    # ],
)

async def main():
    print("Stock Analysis Chatbot")
    print("Enter 'quit' to exit")
    
    while True:
        # Get user input
        user_input = input("\nWhat would you like to know about stocks? ")
        
        # Check for quit command
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
            
        try:
            # Run the agent with user input
            print("\nAnalyzing... Please wait...")
            result = await Runner.run(orchestrator, user_input)
            print("\nAnalysis Result:")
            print(result.final_output)
            
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())