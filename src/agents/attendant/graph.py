from typing import Dict

from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langchain_core.messages import SystemMessage

from src.agents.attendant.prompts import ATTENDANT_PROMPT
from src.agents.attendant.states import AttendantState
from src.agents.attendant.tools import set_final_status
from src.agents.core.nodes import SimpleLLMNode, ToolCallingNode
from src.agents.core.routes import should_use_tools
from src.agents.core.utils import save_graph_as_png


def create_workflow(config: Dict = None):
    workflow = StateGraph(AttendantState)

    # nodes
    attendant_node = SimpleLLMNode(name='attendant_node', system_message=ATTENDANT_PROMPT)
    workflow.add_node(attendant_node.name, lambda state: attendant_node.process(state, config))

    attendant_tools = [set_final_status]
    attendant_tools_node = ToolCallingNode(name='attendant_tools_node', tools=attendant_tools)
    workflow.add_node(attendant_tools_node.name, attendant_tools_node.process)

    # edges
    workflow.add_edge(START, attendant_node.name)
    workflow.add_conditional_edges(attendant_node.name, lambda state: should_use_tools(state, attendant_tools_node.name, END), path_map=[attendant_tools_node.name, END])

    return workflow.compile()


def run_graph():
    config = {"configurable": {"thread_id": "attendant_id"}}

    graph = create_workflow(config=config)
    save_graph_as_png(graph, '../../../docs/attendant_graph.png')

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
