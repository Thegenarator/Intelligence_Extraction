import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from app import config
from app.agent import generate_reply, select_phase
from app.detector import DetectionResult, detect_intent
from app.extraction import extract_intel
from app.state import HistoryEntry, InMemoryStore


SERVICE_NAME = config.get_service_name()
API_KEY = config.get_api_key()

app = FastAPI(title=SERVICE_NAME, version="0.1.0")
store = InMemoryStore()


class HistoryItem(BaseModel):
    role: str = Field(pattern="^(user|agent)$")
    message: str


class WebhookRequest(BaseModel):
    conversation_id: str
    message_id: Optional[str] = None
    message: str
    history: List[HistoryItem] = []
    metadata: Optional[Dict[str, Any]] = None


def api_key_auth(x_api_key: str = Header(...)) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/webhook")
def webhook(event: WebhookRequest, _: None = Depends(api_key_auth)) -> Dict[str, Any]:
    state = store.get_or_create(
        event.conversation_id,
        [HistoryEntry(role=h.role, message=h.message) for h in event.history],
    )

    # Guardrail: stop after max turns to avoid runaway loops
    if state.turns >= config.get_max_turns():
        return {
            "conversation_id": event.conversation_id,
            "scam_detected": True,
            "confidence": 1.0,
            "phase": state.phase,
            "reply": "Okay, I’ll check and get back to you shortly.",
            "extracted": state.extracted,
            "engagement": {"turns": state.turns, "last_user_msg": event.message, "last_agent_msg": ""},
            "reasoning": "Max turns reached",
            "signals": [],
        }

    # Idempotency: ignore duplicate message events if message_id is provided
    if event.message_id:
        if event.message_id in state.processed_message_ids:
            return {
                "conversation_id": event.conversation_id,
                "scam_detected": None,
                "confidence": 0.0,
                "phase": state.phase,
                "reply": "",
                "extracted": state.extracted,
                "engagement": {"turns": state.turns, "last_user_msg": "", "last_agent_msg": ""},
                "reasoning": "Duplicate message_id ignored",
                "signals": [],
            }
        state.processed_message_ids.add(event.message_id)

    # Append latest scammer message
    state.append_message("user", event.message)

    detection: DetectionResult = detect_intent(event.message, state.history)
    phase = select_phase(detection, prior_phase=state.phase, turns=state.turns)
    state.phase = phase

    reply = generate_reply(event.message, state.history, phase)
    state.append_message("agent", reply)

    # Extract intelligence from latest scammer text (and optionally previous)
    extracted = extract_intel(event.message)
    store.merge_extracted(state, extracted)

    response = {
        "conversation_id": event.conversation_id,
        "scam_detected": detection.scam_detected,
        "confidence": detection.confidence,
        "phase": phase,
        "reply": reply,
        "extracted": state.extracted,
        "engagement": {
            "turns": state.turns,
            "last_user_msg": event.message,
            "last_agent_msg": reply,
        },
        "reasoning": detection.reasoning,
        "signals": detection.signals,
    }

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )

