from typing import Dict
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.graph import create_workflow
from src.agents.states import GraphState, ResponsibleInfo, EventInfo
from src.api.storage import storage
from src.api.models import Message


def parse_input_to_state(data: Dict) -> GraphState:
    test_case = data["test_cases"][0]
    client_context = test_case["client_context"]

    responsible_data = client_context["client_details"]["responsibles_details"][0]
    responsible_info = ResponsibleInfo(
        name=responsible_data["name"],
        phone_number=responsible_data["phone_number_1"],
        question=responsible_data["question"],
        correct_answer=responsible_data["correct_answer"],
        panic_answer=responsible_data["panic_answer"],
        function=responsible_data.get("function", "")
    )

    events_info = []
    for event in test_case["events_details"]:
        events_info.append(EventInfo(
            name=event["name"],
            description=event["description"],
            date_time=event["date_time"],
            zone_code=event["zone_code"],
            partition_code=event.get("partition_code", "")
        ))

    return GraphState(
        messages=[HumanMessage(content="Iniciando atendimento de ocorrência")],
        responsible_info=responsible_info,
        events_info=events_info,
        status_final=None
    )


async def process_occurrence_async(hash_id: str, data: Dict):
    try:
        initial_state = parse_input_to_state(data)
        config = {"configurable": {"thread_id": hash_id}}
        graph = create_workflow(initial_state, config=config)

        messages = []
        final_status = None

        for output in graph.stream(initial_state, config=config):
            for node_name, node_output in output.items():
                if node_name == 'attendant_node' and 'messages' in node_output:
                    for msg in node_output['messages']:
                        if isinstance(msg, AIMessage) and msg.content.strip():
                            messages.append(Message(de="atendente", mensagem=msg.content))

                elif node_name == 'client_node' and 'messages' in node_output:
                    for msg in node_output['messages']:
                        if isinstance(msg, AIMessage) and msg.content.strip():
                            messages.append(Message(de="cliente", mensagem=msg.content))

                if 'status_final' in node_output:
                    final_status = node_output['status_final']

        final_status = final_status or "ESCALADO"

        storage.update_occurrence(
            hash_id,
            status=final_status,
            messages=messages
        )

    except Exception as e:
        print(f"Erro no processamento da ocorrência {hash_id}: {e}")
        storage.update_occurrence(hash_id, status="ESCALADO")
