import os
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """API key used to authenticate inbound webhook calls."""
    return os.getenv("API_KEY", "change-me")


def get_service_name() -> str:
    return os.getenv("SERVICE_NAME", "agentic-honeypot")


def get_model_names() -> Dict[str, str]:
    """
    Model selection (env override friendly). The code falls back to templated
    replies if no agent model is configured.
    """
    return {
        "detector": os.getenv("DETECTOR_MODEL", "local-heuristic"),
        "agent": os.getenv("AGENT_MODEL", "template-agent"),
    }


def get_openai_key() -> Optional[str]:
    """Optional OpenAI key to enable LLM-based detector/agent."""
    return os.getenv("OPENAI_API_KEY")


def get_thresholds() -> Dict[str, float]:
    """Thresholds centralised for easy tuning."""
    return {
        "scam_detect": float(os.getenv("SCAM_THRESHOLD", "0.35")),
        "harvest_hint": float(os.getenv("HARVEST_HINT_THRESHOLD", "0.55")),
    }


def get_timeout_seconds() -> float:
    """LLM call timeout budget."""
    return float(os.getenv("LLM_TIMEOUT", "8.0"))


def get_max_turns() -> int:
    """Hard cap on engagement turns per conversation for safety/stability."""
    return int(os.getenv("MAX_TURNS", "16"))


def get_state_ttl_seconds() -> int:
    """TTL for in-memory conversation state (seconds)."""
    return int(os.getenv("STATE_TTL_SECONDS", "7200"))

