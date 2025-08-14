from typing import Optional, List, Literal
from pydantic import BaseModel

from src.agents.core.states import MessagesState


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


class AttendantState(MessagesState):
    responsible_info: ResponsibleInfo
    events_info = List[EventInfo]
    status_final: Optional[Literal["ESCALADO", "RESOLVIDO"]] = None
