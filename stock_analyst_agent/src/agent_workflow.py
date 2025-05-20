from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_community.tools import YahooFinanceNewsTool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from langgraph.constants import START
from langgraph.graph import add_messages, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools import get_valuation_measures
from langchain_community.chat_models import ChatOllama, ChatAnthropic

class StockAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    stock: str

class AgentWorkflow:
    def __init__(self, config: RunnableConfig):
        self.config = config
        self.llm = self.get_llm()

    def get_llm(self) -> BaseChatOpenAI:
        model_type = self.config["configurable"].get("model_type", "openai")
        # Chat models supported by LangChain: https://python.langchain.com/docs/integrations/chat/
        model_type = model_type.lower()
        if model_type == "google":
            print("Using google ('gemini-1.5-flash').")
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        elif model_type == "anthropic":
            print("Using Anthropic (claude-3-opus-20240229).")
            llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0)
        elif model_type == "ollama":
            print("Using Ollama (deepseek-r1:7b).")
            llm = ChatOllama(model="deepseek-r1:7b", temperature=0)
        else:
            print("Using OpenAI (gpt-4o-mini).")
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

        return llm

    def build_stock_analyst_graph(self) -> CompiledStateGraph:
        def collect_tools():
            tools = [get_valuation_measures, YahooFinanceNewsTool()]
            return tools

        def stock_analyst(state: StockAgentState):
            llm_with_tool = self.llm.bind_tools(collect_tools())
            STOCK_ANALYST_PROMPT = """
            You are a financial assistant. Given a stock ticker: {company}, get valuation measures
            using the available tools "get_valuation_measures", get financial news using tool "YahooFinanceNewsTool".
            Once the data is fetched, generate a clear summary for the user in a professional tone.
            """
            messages = [
                           SystemMessage(content=STOCK_ANALYST_PROMPT.format(company=state['stock'])),
                       ] + state['messages']
            return {
                'messages': llm_with_tool.invoke(messages)
            }

        graph_builder = StateGraph(StockAgentState)
        graph_builder.add_node('stock_analyst', stock_analyst)
        graph_builder.add_node('tools', ToolNode(collect_tools()))

        graph_builder.add_edge(START, 'stock_analyst')
        graph_builder.add_conditional_edges('stock_analyst', tools_condition)
        graph_builder.add_edge('tools', 'stock_analyst')

        graph = graph_builder.compile()
        return graph

    def invoke_stock_analyst_graph(self, state: StockAgentState):
        load_dotenv()
        graph = self.build_stock_analyst_graph()
        response = graph.invoke(state)
        return response['messages']

if __name__ == '__main__':
    config = RunnableConfig(configurable={"model_type": "google"})
    workflow = AgentWorkflow(config)
    stock_ticker = 'hood'
    user_message = f'Analyze stock: {stock_ticker}'
    state = {
        'messages': [HumanMessage(content=user_message)],
        'stock': stock_ticker
    }

    messages = workflow.invoke_stock_analyst_graph(state)
    for m in messages:
        m.pretty_print()

