import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

load_dotenv()


def get_recent_messages(state: Any, limit: int = 30) -> List:
    return state['messages'][-limit:]


def create_node(system_message: str, tools: List[Any] = None, node_type: str = "generic"):
    llm = ChatOpenAI(
        temperature=0,
        model_name=os.getenv('OPENAI_LLM_MODEL_NAME')
    )

    def node(state: Any, config: Dict = None) -> Dict:
        messages = [SystemMessage(content=system_message)]
        messages.extend(get_recent_messages(state))

        try:
            if tools:
                llm_with_tools = llm.bind_tools(tools=tools, tool_choice='auto')
                result = llm_with_tools.invoke(messages, config)
            else:
                result = llm.invoke(messages, config)

            return {
                'messages': [AIMessage(content=result.content, tool_calls=result.tool_calls)]
            }
        except Exception as e:
            print(f'Erro no {node_type}: {e}')
            return {}

    return node


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
