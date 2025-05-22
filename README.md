# OnlyFins
This is an educational economic event tracker agent. We aim to help rookie investors to connect the dots between macro/microeconomic events and their impact on the asset prices. In this version, the agent is designed to be a learning tool that integrates the leading financial and economic data platforms with LLMs to provide a comprehensive overview of the economic landscape. 

### Main Features

0. **Data Collection**: The agent can collect data from various apis, including:
 - [x] Alpha Vantage: e.g. [Alpha Vantage](https://www.alphavantage.co/)

1. **Event Impact Analysis**: The agent can analyze the impact of various economic events on asset prices, including:
 - [ ] Macro Event Impact Analysis: e.g. How does the Fed's interest rate decision affect the S&P 500? How does the CPI report impact the Apple stock price?
 - [ ] Micro Event Impact Analysis: e.g. How does the release of a new iPhone affect Apple's stock price? How does the release of DeepSeek impact the stock price of Nvidia?
 - [ ] Policy Speech Impact Analysis: e.g. How does the Powell's speech impact the S&P 500, the gold price, and the USDT price?
 - [ ] Earnings Report Impact Analysis: e.g. How does the earnings report of Nvidia impact the stock price of AMD? 
 - [ ] Geopolitical Event Impact Analysis: e.g. How does the US-China trade war impact the stock price of Apple? How does the Russia-Ukraine war impact the stock price of oil? 

2. **Data Visualization**: The agent can visualize the data using various libraries, including:
 - [ ] Plotly: e.g. [Plotly](https://plotly.com/python/)

### Project Structure
```
project-root/
├── src/
│   ├── openbb_data/            # Wrappers around OpenBB Platform REST & SDK
│   ├── custom_data/            # Alpha Vantage client, other bespoke connectors
│   ├── events/                 # Macro, micro, policy, earnings, geopolitical analyzers
│   ├── backtester/             # Strategy parser, Plotly visualizer, feedback engine
│   ├── agents/                 # LangChain Agent & Tool definitions
│   ├── api/                    # FastAPI app combining OpenBB and custom endpoints
│   └── common/                 # Config, logging, error handling utilities
├── tests/                      # pytest suites for each module
└── README.md
```

### Requirements
```
conda create -n llmagent python=3.12
conda activate llmagent
pip install openai-agents
pip install python-dotenv
pip install pandas
pip install pydantic
pip install plotly
pip install asyncio
pip install langchain
pip install langchain-openai
pip install langchain-core
pip install langgraph
```

### Usage
```
python demo.py
```

### Example
![Demo](assets/demo.gif)