# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An **agentic FastAPI service** designed to **detect, engage, and extract intelligence from scam conversations**.
Built for the *Agentic Honey-Pot Hackathon*, the system autonomously interacts with scammers to harvest actionable fraud intelligence while returning structured, machine-readable outputs.

A live deployment with interactive API documentation is available here:
👉 https://intelligence-extraction.onrender.com/docs

---

## 🎯 Project Overview

This project implements an **AI-assisted honey-pot** that:

* Receives scam conversation events via a webhook
* Detects scam intent using hybrid heuristics and optional LLM reasoning
* Switches into an autonomous, phase-aware persona when a scam is detected
* Engages scammers over multiple turns to extract intelligence
* Normalizes and returns structured fraud artifacts in JSON format

The service is designed to be **stateless at the API layer**, with **in-memory conversational state** managing engagement flow and extraction continuity.

---

## 🔍 Core Capabilities

### Scam Detection

* Hybrid detection engine combining:

  * Heuristic keyword and pattern analysis
  * Optional LLM-based classification
* Produces a confidence score, signals, and reasoning summary
* Supports early exit for non-scam conversations

### Agentic Engagement

* Autonomous scam-engagement persona
* Phase-aware state machine:

  * **HOOK** – gain trust and confirm intent
  * **PROBE** – elicit sensitive operational details
  * **HARVEST** – extract financial and infrastructure intel
* Deterministic fallback responses when no LLM is enabled

### Intelligence Extraction

Regex-first extraction with light normalization for:

* Bank account numbers + IFSC codes
* UPI IDs
* Phishing URLs
* Monetary amounts

Each extracted artifact includes an individual confidence score.

---

## 🧠 Phase-Aware Intelligence Flow

The system advances through engagement phases based on:

* Scam confidence score
* Detected signals (urgency, payment requests, links, etc.)
* Conversation history and prior extraction success

This prevents premature harvesting and improves data quality.

---

## 📡 API Interface

### Endpoint

**POST** `/webhook`

### Request Body

```json
{
  "conversation_id": "string",
  "message_id": "string (optional)",
  "message": "string",
  "history": [
    {
      "role": "user | agent",
      "message": "string"
    }
  ]
}
```

### Response Body

```json
{
  "conversation_id": "demo-1",
  "scam_detected": true,
  "confidence": 0.87,
  "phase": "HARVEST",
  "reply": "Ok, I can do that. To avoid mistakes, send me the exact UPI ID or bank account number with IFSC you want me to use.",
  "extracted": {
    "bank_accounts": [
      { "value": "123456789012", "ifsc": "ABCD0123456", "confidence": 0.8 }
    ],
    "upi_ids": [
      { "value": "name@okhdfc", "confidence": 0.8 }
    ],
    "urls": [
      { "value": "https://phishy-link.example/refund", "confidence": 0.75 }
    ],
    "amounts": [
      { "value": "INR 27500", "confidence": 0.4 }
    ]
  },
  "engagement": {
    "turns": 3,
    "last_user_msg": "Pay the processing fee via UPI to receive your refund today",
    "last_agent_msg": "Ok, I can do that. To avoid mistakes, send me the exact UPI ID or bank account number with IFSC you want me to use."
  },
  "reasoning": "Signals: fee, upi, urgent, currency, link",
  "signals": ["fee", "upi", "urgent", "currency", "link"]
}
```

---

## 🏗️ Internal Architecture

* **`app/main.py`**
  API routing, authentication, request/response models

* **`app/state.py`**
  In-memory conversation state:

  * Turn history
  * Engagement phase
  * Deduplicated extracted intelligence
  * TTL-based cleanup and idempotency

* **`app/detector.py`**
  Hybrid scam detection engine:

  * Heuristic scoring
  * Optional LLM classification
  * Outputs confidence, signals, and phase hints

* **`app/agent.py`**
  Autonomous agent controller:

  * Deterministic phase logic
  * Optional LLM-powered persona
  * Tactical prompting per engagement phase

* **`app/extraction.py`**
  Regex-first intelligence extraction with normalization

* **`app/config.py`**
  Centralized configuration and thresholds

---

## 🔐 Design Principles

* **Explainable detection** — clear signals and reasoning
* **Progressive engagement** — avoid early over-extraction
* **LLM-optional** — fully functional without external models
* **Structured intelligence output** — ready for downstream pipelines
* **Hackathon-friendly** — minimal surface area, fast iteration

---

## 🚀 Use Cases

* Scam intelligence collection
* Fraud pattern analysis
* Threat actor infrastructure mapping
* Research and experimentation with agentic deception systems
* Integration into SOC, SIEM, or fraud-monitoring pipelines

---

