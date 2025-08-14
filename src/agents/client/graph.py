from typing import Dict

from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langchain_core.messages import SystemMessage

from src.agents.client.prompts import CLIENT_PROMPT
from src.agents.client.states import ClientState
from src.agents.core.nodes import SimpleLLMNode
from src.agents.core.utils import save_graph_as_png

client_node = SimpleLLMNode(name='client_node', system_message=CLIENT_PROMPT)


def create_workflow(config: Dict = None):
    workflow = StateGraph(ClientState)

    # nodes
    workflow.add_node(client_node.name, client_node.process)

    # edges
    workflow.add_edge(START, client_node.name)
    workflow.add_edge(client_node.name, END)

    return workflow.compile()


def run_graph():
    config = {"configurable": {"thread_id": "client_id"}}

    graph = create_workflow(config=config)
    save_graph_as_png(graph, '../../../docs/client_graph.png')

    initial_state = {
        'messages': SystemMessage(content='Abra um chamado de emergência para a Auria AI')
    }

    try:
        for output in graph.stream(initial_state, config=config, subgraphs=True):
            print(f'output: {output}')

    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    run_graph()
