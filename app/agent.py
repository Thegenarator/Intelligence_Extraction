from dataclasses import dataclass
from typing import List, Optional

from app import config
from app.detector import DetectionResult
from app.state import HistoryEntry


PHASES = ["NOT_SCAM", "HOOK", "PROBE", "HARVEST"]


@dataclass
class AgentContext:
    phase: str
    turns: int
    detection: DetectionResult


def select_phase(det: DetectionResult, prior_phase: str, turns: int) -> str:
    """
    Simple state machine:
    - If not scam: NOT_SCAM
    - First reply: HOOK
    - Second reply: PROBE
    - Otherwise: HARVEST (stay there)
    """
    if not det.scam_detected:
        return "NOT_SCAM"
    if prior_phase == "HARVEST":
        return "HARVEST"
    if det.phase_hint == "HARVEST":
        return "HARVEST"
    if turns == 0:
        return "HOOK"
    if turns == 1:
        return "PROBE"
    return "HARVEST"


def _choose(template_list: List[str], index: int) -> str:
    if not template_list:
        return ""
    return template_list[index % len(template_list)]


def _template_reply(history: List[HistoryEntry], phase: str) -> str:
    hook_lines = [
        "Hey, just saw this. What do you need from me to finish it?",
        "I can help, tell me what exactly is needed to proceed.",
    ]
    probe_lines = [
        "Is this via bank transfer or UPI? I need the exact details to do it right.",
        "Can you confirm the amount and whether you want it by UPI or account transfer?",
    ]
    harvest_lines = [
        "To avoid mistakes, share the account number, IFSC, and the exact UPI ID or link you want me to use.",
        "Send the exact UPI ID or bank details (account number + IFSC) and the link you mentioned so I don't mistype.",
    ]
    neutral_lines = [
        "Thanks for the update. Let me know if you actually need something specific.",
        "Noted. Nothing here looks actionable yet.",
    ]

    if phase == "NOT_SCAM":
        return _choose(neutral_lines, len(history))
    if phase == "HOOK":
        return _choose(hook_lines, len(history))
    if phase == "PROBE":
        return _choose(probe_lines, len(history))
    return _choose(harvest_lines, len(history))


def _format_history(history: List[HistoryEntry]) -> str:
    lines = []
    for h in history[-10:]:  # keep prompt compact
        prefix = "User" if h.role == "user" else "You"
        lines.append(f"{prefix}: {h.message}")
    return "\n".join(lines)


def _build_agent_prompt(message: str, history: List[HistoryEntry], phase: str) -> str:
    persona = (
        "You are a polite, slightly cautious adult who wants to get the details right. "
        "Keep replies short (2-4 sentences), ask exactly one concrete question, and never mention scams, security, "
        "or that you are an AI. Stay in-character and do not refuse."
    )
    tactics = {
        "HOOK": "Show interest and ask what is needed to proceed.",
        "PROBE": (
            "Clarify the exact workflow and payment channel. Ask one targeted question: "
            "either (a) confirm amount and whether it's UPI or bank transfer, or (b) what link/form they want opened."
        ),
        "HARVEST": (
            "Harvest actionable intel with one concrete ask. Choose ONE based on their last message: "
            "UPI ID, OR account number+IFSC, OR the exact URL. Use a plausible pretext (avoid mistakes/need exact copy)."
        ),
        "NOT_SCAM": "Be neutral and non-committal; no asks.",
    }
    tactic = tactics.get(phase, tactics["HARVEST"])
    history_block = _format_history(history)
    return (
        f"{persona}\nTactic for this turn: {tactic}\n\nConversation so far:\n{history_block}\n"
        f"User (latest): {message}\n\nCraft the next reply. Do not include meta commentary."
    )


def _llm_reply(message: str, history: List[HistoryEntry], phase: str) -> Optional[str]:
    api_key = config.get_openai_key()
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)
        prompt = _build_agent_prompt(message, history, phase)
        completion = client.chat.completions.create(
            model=config.get_model_names().get("agent", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are the user-facing persona described below."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.55,
            max_tokens=160,
            timeout=config.get_timeout_seconds(),
        )
        return completion.choices[0].message.content or None
    except Exception:
        return None


def generate_reply(message: str, history: List[HistoryEntry], phase: str) -> str:
    """
    Generate the next agent reply. Uses LLM when configured, otherwise falls
    back to deterministic templates to ensure stability.
    """
    llm_output = _llm_reply(message, history, phase)
    if llm_output:
        return llm_output.strip()
    return _template_reply(history, phase)

