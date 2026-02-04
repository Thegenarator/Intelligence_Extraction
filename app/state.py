from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app import config


@dataclass
class HistoryEntry:
    role: str  # "user" or "agent"
    message: str


@dataclass
class ConversationState:
    conversation_id: str
    phase: str = "SCREEN"
    history: List[HistoryEntry] = field(default_factory=list)
    extracted: Dict[str, List[Dict]] = field(
        default_factory=lambda: {"bank_accounts": [], "upi_ids": [], "urls": [], "amounts": []}
    )
    last_seen_ts: float = field(default_factory=lambda: time.time())
    processed_message_ids: set[str] = field(default_factory=set)

    def append_message(self, role: str, message: str) -> None:
        self.history.append(HistoryEntry(role=role, message=message))
        self.last_seen_ts = time.time()

    @property
    def turns(self) -> int:
        """Count agent replies to approximate engagement turns."""
        return len([h for h in self.history if h.role == "agent"])


class InMemoryStore:
    def __init__(self) -> None:
        self._store: Dict[str, ConversationState] = {}

    def _gc(self) -> None:
        """Best-effort TTL cleanup to keep memory bounded."""
        ttl = config.get_state_ttl_seconds()
        if ttl <= 0:
            return
        now = time.time()
        expired = [cid for cid, st in self._store.items() if now - st.last_seen_ts > ttl]
        for cid in expired:
            self._store.pop(cid, None)

    def get_or_create(
        self, conversation_id: str, initial_history: Optional[List[HistoryEntry]] = None
    ) -> ConversationState:
        self._gc()
        if conversation_id not in self._store:
            state = ConversationState(conversation_id=conversation_id)
            if initial_history:
                state.history.extend(initial_history)
            self._store[conversation_id] = state
        return self._store[conversation_id]

    def merge_extracted(
        self, state: ConversationState, new_data: Dict[str, List[Dict]]
    ) -> None:
        for key, items in new_data.items():
            existing_values = {item["value"] for item in state.extracted.get(key, [])}
            for item in items:
                if item["value"] not in existing_values:
                    state.extracted[key].append(item)
                    existing_values.add(item["value"])

