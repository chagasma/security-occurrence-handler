import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

load_dotenv()


def create_llm():
    return ChatOpenAI(
        temperature=0,
        model_name=os.getenv('OPENAI_LLM_MODEL_NAME')
    )


def get_recent_messages(state: Any, limit: int = 12) -> List:
    messages = state['messages']
    start_index = max(0, len(messages) - limit)
    return validate_message_sequence(messages[start_index:])


def validate_message_sequence(messages: List) -> List:
    valid_messages = []
    tool_call_ids_to_match = set()

    for msg in messages:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_call_ids_to_match.add(tool_call.get('id'))
            valid_messages.append(msg)
        elif isinstance(msg, ToolMessage):
            if msg.tool_call_id in tool_call_ids_to_match:
                valid_messages.append(msg)
                tool_call_ids_to_match.remove(msg.tool_call_id)
        else:
            valid_messages.append(msg)
    
    return valid_messages


def create_attendant_node(system_message: str, tools: List[Any]):
    llm = create_llm()
    
    def attendant_node(state: Any, config: Dict = None) -> Dict:
        messages = [SystemMessage(content=system_message)]
        messages.extend(get_recent_messages(state))
        
        try:
            llm_with_tools = llm.bind_tools(tools=tools, tool_choice='auto')
            result = llm_with_tools.invoke(messages, config)
            
            return {
                'messages': [AIMessage(content=result.content, tool_calls=result.tool_calls)]
            }
        except Exception as e:
            print(f'Erro no atendente: {e}')
            return {}
    
    return attendant_node


def create_client_node(system_message: str):
    llm = create_llm()
    
    def client_node(state: Any, config: Dict = None) -> Dict:
        messages = [SystemMessage(content=system_message)]
        messages.extend(get_recent_messages(state))
        
        try:
            result = llm.invoke(messages, config)
            return {
                'messages': [AIMessage(content=result.content, tool_calls=result.tool_calls)]
            }
        except Exception as e:
            print(f'Erro no cliente: {e}')
            return {}
    
    return client_node


def create_tools_node(tools: List[Any]):
    tool_node = ToolNode(tools)
    
    def tools_node(state: Any, config: Dict = None):
        try:
            return tool_node
        except Exception as e:
            return {
                "messages": [SystemMessage(content=f"Erro ao processar ferramenta: {e}")]
            }
    
    return tools_node