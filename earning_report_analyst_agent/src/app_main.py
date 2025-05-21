import logging
from typing import List

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

from earning_report_analyst_agent.src.agent_workflow import ERAgentWorkflow
from earning_report_analyst_agent.src.logger import configure_logging

logger = configure_logging(log_file = "log/er_analyst.log", module_name="app_main", log_level=logging.INFO)
def main(ticker: str, queries: List[str]) -> List[str]:
    logger.info("Starting Earning Report Analyst Agent")
    load_dotenv()
    config = RunnableConfig(configurable={"model_type": "google"})
    try:
        era = ERAgentWorkflow(config)
        return era.pipeline(ticker, queries)
    except Exception as e:
        logger.exception(f"Error while running Earning Report Analyst Agent: {e}")
        raise e

if __name__ == '__main__':
    ticker = "AAPL"
    queries = [
        f"What are the key financial highlights for {ticker} in the report?"
    ]
    llm_responses = main(ticker, queries)
    for response in llm_responses:
        print(response)