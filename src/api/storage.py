import hashlib
import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from src.api.models import Message


@dataclass
class OccurrenceState:
    hash_id: str
    status: str = "PROCESSANDO"
    messages: list[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class OccurrenceStorage:
    def __init__(self):
        self._storage: Dict[str, OccurrenceState] = {}

    @staticmethod
    def generate_hash(data: dict) -> str:
        timestamp = str(time.time())
        content = f"{timestamp}_{str(data)}"
        return hashlib.md5(content.encode()).hexdigest()

    def create_occurrence(self, data: dict) -> str:
        hash_id = self.generate_hash(data)
        self._storage[hash_id] = OccurrenceState(hash_id=hash_id)
        return hash_id

    def get_occurrence(self, hash_id: str) -> Optional[OccurrenceState]:
        return self._storage.get(hash_id)

    def update_occurrence(self, hash_id: str, status: str = None, messages: list[Message] = None):
        occurrence = self._storage.get(hash_id)
        if occurrence:
            if status:
                occurrence.status = status
            if messages:
                occurrence.messages = messages


storage = OccurrenceStorage()
