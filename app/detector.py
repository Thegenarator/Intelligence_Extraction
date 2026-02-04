import json
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from app import config
from app.state import HistoryEntry


SCAM_KEYWORDS = [
    "otp",
    "kyc",
    "refund",
    "verification",
    "gift card",
    "fee",
    "processing charge",
    "wire",
    "bank transfer",
    "upi",
    "ifsc",
    "crypto",
    "wallet",
    "payment link",
    "secure link",
    "one-time password",
    "settlement",
    "compensation",
    "prize",
    "insurance",
]

URGENCY_PHRASES = [
    "immediately",
    "urgent",
    "right now",
    "asap",
    "today",
    "instantly",
]

ACCOUNT_HINTS = {"upi", "ifsc", "bank transfer", "account number", "iban", "routing", "swift"}


@dataclass
class DetectionResult:
    scam_detected: bool
    confidence: float
    reasoning: str
    phase_hint: str
    signals: List[str]


def _score_text(text: str) -> Tuple[float, List[str]]:
    text_lower = text.lower()
    score = 0.0
    signals: List[str] = []

    for kw in SCAM_KEYWORDS:
        if kw in text_lower:
            score += 0.08
            signals.append(kw)

    for phrase in URGENCY_PHRASES:
        if phrase in text_lower:
            score += 0.05
            signals.append(phrase)

    # Long digit sequences indicate account/amount/OTP-like content
    if re.search(r"\d{6,}", text_lower):
        score += 0.08
        signals.append("long_digits")

    # Currency tokens suggest payment context
    if re.search(r"\b(inr|usd|rs\.?|rupees|dollars?)\b", text_lower):
        score += 0.05
        signals.append("currency")

    # Links hint at phishing
    if re.search(r"https?://", text_lower):
        score += 0.07
        signals.append("link")

    return min(score, 1.0), signals


def _maybe_llm_detect(text: str) -> Optional[Tuple[bool, float, str, str]]:
    """
    Optional LLM-based detector. Returns (is_scam, confidence, reasoning, phase_hint)
    or None if unavailable.
    """
    api_key = config.get_openai_key()
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)
        prompt = (
            "Classify if the message is part of a scam attempt. "
            "Reply ONLY with strict JSON: "
            '{"scam": true|false, "confidence": 0-1, "phase": "HOOK|HARVEST|NONE", "reason": "<short>"}'
        )
        completion = client.chat.completions.create(
            model=config.get_model_names().get("detector", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
            timeout=config.get_timeout_seconds(),
        )
        raw = completion.choices[0].message.content or "{}"
        data = json.loads(raw)
        return (
            bool(data.get("scam", False)),
            float(data.get("confidence", 0.0)),
            str(data.get("reason", "")),
            str(data.get("phase", "NONE")),
        )
    except Exception:
        # On any failure, fall back to heuristic
        return None


def detect_intent(message: str, history: List[HistoryEntry]) -> DetectionResult:
    all_text = " ".join([h.message for h in history] + [message])
    score, signals = _score_text(all_text)

    llm_result = _maybe_llm_detect(all_text)
    thresholds = config.get_thresholds()

    if llm_result:
        llm_scam, llm_conf, llm_reason, llm_phase = llm_result
        scam_detected = llm_scam or score >= thresholds["scam_detect"]
        confidence = max(llm_conf, score)
        phase_hint = llm_phase if llm_phase in {"HOOK", "HARVEST"} else "HARVEST" if any(
            s in ACCOUNT_HINTS for s in signals
        ) else "HOOK"
        reasoning = f"LLM: {llm_reason}; Heuristic signals: {', '.join(signals) or 'none'}"
    else:
        scam_detected = score >= thresholds["scam_detect"]
        phase_hint = (
            "HARVEST"
            if score >= thresholds["harvest_hint"] or any(s in ACCOUNT_HINTS for s in signals)
            else "HOOK"
        )
        confidence = round(score, 2)
        reasoning = f"Signals: {', '.join(signals) if signals else 'none'}"

    return DetectionResult(
        scam_detected=scam_detected,
        confidence=round(confidence, 2),
        reasoning=reasoning,
        phase_hint=phase_hint if scam_detected else "NOT_SCAM",
        signals=signals,
    )

