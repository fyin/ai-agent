# ai-agent
A practice project to build a stock analyst agent using [langgraph](https://www.langchain.com/langgraph). 
The agent uses ReAct architecture, which revolves around iterative cycles of thought, action, and observation.

## Dependency Management
Use [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html) to manage the environment and 3rd party libraries.
All the required dependencies are put in requirements.txt.
* Create an environment `conda create -n aa python=3.12`
* Activate the environment `conda activate aa`
* * Install the dependencies 
`pip3 install -r stock_analyst_agent/requirements.txt`
* To install ta-lib, follow the instructions [here](https://github.com/TA-Lib/ta-lib-python) Ex: in mac,
* *  brew install ta-lib
* *  pip3 install ta-lib

## Usage
Before running the agent, set up the environment variable `OPENAI_API_KEY`/`GOOGLE_API_KEY`/`ANTHROPIC_API_KEY`/etc 
if you want to use OpenAI/Google Generative AI/Claude/other LLM model API keys accordingly.
Check https://python.langchain.com/docs/integrations/providers/ for more information
* Run the agent `python stock_analyst_agent/src/stock_analyst_agent.py`

## References:
https://python.langchain.com/docs
https://github.com/langchain-ai/langchain-academy
https://langchain-ai.github.io/langgraph/
