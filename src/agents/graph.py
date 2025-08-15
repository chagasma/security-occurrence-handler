from typing import Dict

from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langchain_core.messages import HumanMessage

from src.agents.core.nodes import SimpleLLMNode, ToolCallingNode
from src.agents.core.routes import should_use_tools
from src.agents.core.utils import save_graph_as_png
from src.agents.prompts import get_attendant_prompt, get_client_prompt
from src.agents.states import GraphState, ResponsibleInfo, EventInfo
from src.agents.tools import set_final_status, validate_security_keyword


def create_workflow(initial_state: GraphState, config: Dict = None):
    workflow = StateGraph(GraphState)

    attendant_prompt = get_attendant_prompt(initial_state.responsible_info, initial_state.events_info)
    client_prompt = get_client_prompt(initial_state.responsible_info)

    # nodes
    client_node = SimpleLLMNode(name='client_node', system_message=client_prompt)
    workflow.add_node(client_node.name, lambda state: client_node.process(state, config))

    attendant_tools = [set_final_status, validate_security_keyword]
    attendant_node = SimpleLLMNode(name='attendant_node', system_message=attendant_prompt, tools=attendant_tools)
    workflow.add_node(attendant_node.name, lambda state: attendant_node.process(state, config))

    attendant_tools_node = ToolCallingNode(name='attendant_tools_node', tools=attendant_tools)
    workflow.add_node(attendant_tools_node.name, attendant_tools_node.process)

    # edges
    workflow.add_edge(START, attendant_node.name)
    workflow.add_conditional_edges(attendant_node.name, lambda state: should_use_tools(state, attendant_tools_node.name, client_node.name), path_map=[attendant_tools_node.name, client_node.name])
    workflow.add_edge(attendant_tools_node.name, attendant_node.name)
    workflow.add_edge(client_node.name, attendant_node.name)

    return workflow.compile()


def create_test_initial_state():
    responsible_info = ResponsibleInfo(
        name="Carlos",
        phone_number="11987654321",
        question="Qual seu hobby favorito?",
        correct_answer="Caminhada",
        panic_answer="Natação",
        function="ZELADOR"
    )

    events_info = [
        EventInfo(
            name="ALARME DE ZONA SENSOR PORTA VEICULAR",
            description="Disparo de alarme na zona de acesso veicular.",
            date_time="2025-02-22T08:45:00-03:00",
            zone_code="6 - SENSOR PORTA VEICULAR",
            partition_code="02"
        )
    ]

    return GraphState(
        messages=[HumanMessage(content="Iniciando atendimento de ocorrência")],
        responsible_info=responsible_info,
        events_info=events_info,
        status_final=None
    )


def run_graph():
    config = {"configurable": {"thread_id": "client_id"}}
    initial_state = create_test_initial_state()

    graph = create_workflow(initial_state, config=config)
    save_graph_as_png(graph, '../../docs/graph.png')

    try:
        for output in graph.stream(initial_state, config=config):
            print(f'output: {output}')

    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    run_graph()
