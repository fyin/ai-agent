import logging
from typing import List

from langchain_community.chat_models import ChatAnthropic, ChatOllama, ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai.chat_models.base import BaseChatOpenAI

from earning_report_analyst_agent.src.earning_downloader import SecDownloader
from earning_report_analyst_agent.src.logger import configure_logging
from earning_report_analyst_agent.src.vector_db import ChromaDB

logger = configure_logging(log_file = "log/er_analyst.log", module_name="agent_workflow", log_level=logging.INFO)

class ERAgentWorkflow:
    def __init__(self, config: RunnableConfig):
        self.config = config
        self.llm = self.get_llm()

    def get_llm(self) -> BaseChatOpenAI:
        model_type = self.config["configurable"].get("model_type", "openai")
        # Chat models supported by LangChain: https://python.langchain.com/docs/integrations/chat/
        model_type = model_type.lower()
        if model_type == "google":
            logger.info("Using google ('gemini-1.5-flash').")
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        elif model_type == "anthropic":
            logger.info("Using Anthropic (claude-3-opus-20240229).")
            llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0)
        elif model_type == "ollama":
            logger.info("Using Ollama (deepseek-r1:7b).")
            llm = ChatOllama(model="deepseek-r1:7b", temperature=0)
        else:
            logger.info("Using OpenAI (gpt-4o-mini).")
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

        return llm

    def generate_answer(self, question: str, context: List[str]) -> str:
        context_text = "\n".join(context)
        prompt = f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer:"
        response = self.llm.invoke(prompt)
        return response.content

    def pipeline(self,ticker: str, queries: List[str]) -> List[str]:
        downloader = SecDownloader("Individual Researcher", "user@gmail.com", "sec_filings")
        file_path = downloader.download_recent_earning_report(ticker=ticker, form_type="10-Q", max_filings=1)
        if file_path is None:
            raise ValueError(f"No 10-Q filings found for {ticker}.")
        collection_name = f"{ticker}_earnings"
        persist_dir = "./chroma_db"
        chromadb = ChromaDB()
        text = chromadb.extract_text_from_html(file_path)
        vectorstore = chromadb.create_chroma_vectorstore(text, collection_name, persist_dir)
        if vectorstore is None:
            raise ValueError(f"Failed to create Chroma vector store for {ticker}.")
        llm_responses = []
        for query in queries:
            query_result = chromadb.query_earnings(vectorstore, query)
            query_result_str = [doc.page_content for doc in query_result]
            llm_response = self.generate_answer(query, query_result_str)
            llm_responses.append(llm_response)
        return llm_responses