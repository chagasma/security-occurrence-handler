from typing import Optional, List, Literal, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel


class ResponsibleInfo(BaseModel):
    name: str
    phone_number: str
    question: str
    correct_answer: str
    panic_answer: str
    function: Optional[str] = None


class EventInfo(BaseModel):
    name: str
    description: str
    date_time: str
    zone_code: str
    partition_code: Optional[str] = None


class GraphState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    responsible_info: ResponsibleInfo
    events_info: List[EventInfo]
    status_final: Optional[Literal["ESCALADO", "RESOLVIDO"]] = None

    def __getitem__(self, item):
        return getattr(self, item, None)
