from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from stock_analyst_agent.src.agent_workflow import AgentWorkflow

def main():
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

if __name__ == '__main__':
    main()