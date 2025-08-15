from typing import List, Optional, Literal
from pydantic import BaseModel


class OccurrenceRequest(BaseModel):
    test_cases: List[dict]
    test_suite_id: str


class OccurrenceResponse(BaseModel):
    hash: str


class Message(BaseModel):
    de: str
    mensagem: str


class StatusResponse(BaseModel):
    status_final: Optional[Literal["ESCALADO", "RESOLVIDO", "PROCESSANDO"]]
    mensagens: List[Message]
