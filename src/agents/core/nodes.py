import os
from abc import ABC, abstractmethod
from typing import Optional, Any, Callable, List, Dict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

load_dotenv()


class Node(ABC):
    def __init__(
            self,
            name: str,
            tools: Optional[List] = None,
            state_update_fn: Optional[Callable] = None
    ):
        self.name = name
        self.tools = tools
        self.state_update_fn = state_update_fn

    @abstractmethod
    def process(self, state: Any, config: Dict) -> Dict:
        pass

    def update_state(self, state: Any):
        if self.state_update_fn:
            self.state_update_fn(state)


class LLMNode(Node, ABC):
    def __init__(
            self,
            name: str,
            system_message: str = '',
            msgs_to_extend: int = -12,
            output_model: Optional[Any] = None,
            tool_choice: str = 'auto',
            tools: Optional[List] = None,
            state_update_fn: Optional[Callable] = None
    ):
        super().__init__(name=name, tools=tools, state_update_fn=state_update_fn)
        self.system_message = system_message
        self.msgs_to_extend = msgs_to_extend
        self.output_model = output_model
        self.tool_choice = tool_choice
        self.llm = ChatOpenAI(
            temperature=0,
            model_name=os.getenv('OPENAI_LLM_MODEL_NAME')
        )

    def _get_messages(self, state: Any) -> List:
        messages = [SystemMessage(content=self.system_message)]

        start_index = len(state['messages']) + self.msgs_to_extend if self.msgs_to_extend < 0 else self.msgs_to_extend
        start_index = max(0, start_index)

        candidate_messages = state['messages'][start_index:]
        valid_messages = self._validate_message_sequence(candidate_messages)

        messages.extend(valid_messages)
        return messages

    @staticmethod
    def _validate_message_sequence(messages: List) -> List:
        valid_messages = []
        i = 0
        tool_call_ids_to_match = set()

        while i < len(messages):
            current_msg = messages[i]

            if hasattr(current_msg, 'tool_calls') and current_msg.tool_calls:
                for tool_call in current_msg.tool_calls:
                    tool_call_ids_to_match.add(tool_call.get('id'))
                valid_messages.append(current_msg)

            elif isinstance(current_msg, ToolMessage):
                if current_msg.tool_call_id in tool_call_ids_to_match:
                    valid_messages.append(current_msg)
                    tool_call_ids_to_match.remove(current_msg.tool_call_id)

            else:
                valid_messages.append(current_msg)

            i += 1

        return valid_messages


class SimpleLLMNode(LLMNode):
    def process(self, state: Any, config: Dict) -> Dict:
        messages = self._get_messages(state)

        try:
            llm_instance = self.llm

            if self.tools:
                llm_instance = self.llm.bind_tools(
                    tools=self.tools,
                    tool_choice=self.tool_choice
                )

            result = llm_instance.invoke(messages, config)

            return {
                'messages': [AIMessage(content=result.content, tool_calls=result.tool_calls)]
            }
        except Exception as e:
            print(f'Erro ao gerar resposta: {e}')
            return {}


class StructuredOutputLLMNode(LLMNode):
    def process(self, state: Any, config: Dict) -> Dict:
        messages = self._get_messages(state)

        try:
            llm_instance = self.llm.with_structured_output(
                self.output_model,
                method='function_calling'
            )
            result = llm_instance.invoke(messages, config)
            return result.model_dump()
        except Exception as e:
            print(f'Erro ao gerar resposta estruturada: {e}')
            return {}


class ToolCallingNode(Node):
    def __init__(self, name: str, tools: List[Any]):
        super().__init__(name=name)
        self.tools = tools
        self.tool_node = ToolNode(self.tools)

    def process(self, state: Any, config: Dict):
        try:
            tool_result = self.tool_node
            return tool_result
        except Exception as e:
            return {
                "messages": [SystemMessage(content=f"Ocorreu um erro ao processar essa solicitação: {e}")]
            }
