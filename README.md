# Agentic Honey-Pot for Scam Detection & Intelligence Extraction
## Overview

Agentic Honey-Pot is a lightweight FastAPI service designed for scam detection, autonomous engagement, and intelligence extraction.
It simulates a responsive victim persona that detects scam intent, adapts its behavior across conversation phases, and harvests actionable scammer intelligence over multiple turns.

The system operates as a webhook-driven API that can be embedded into messaging platforms, moderation pipelines, or fraud-analysis workflows.

A live deployment with interactive API documentation is available here:
👉 https://intelligence-extraction.onrender.com/docs

## Core Capabilities
### 1. Scam Detection

Identifies scam intent from incoming conversation events

Uses a hybrid approach:

Heuristic signals (keywords, urgency, currency patterns, links, long numeric strings)

Optional LLM-based classification

Produces a confidence score and interpretable signals

### 2. Autonomous Engagement

Once scam intent is detected, the system switches into an agentic persona that engages the scammer intentionally.

The agent operates as a phase-aware state machine:

HOOK – signals compliance and interest

PROBE – asks clarification questions to elicit sensitive details

HARVEST – maximizes extraction of financial and infrastructural data

Engagement continues across turns while maintaining conversation context.

### 3. Intelligence Extraction

During engagement, the service extracts and normalizes actionable artifacts using a regex-first pipeline, including:

Bank account numbers + IFSC codes

UPI IDs

Phishing URLs

Monetary amounts

Each extracted item is returned with an associated confidence score.

### 4. Structured Output

Every webhook response returns a machine-readable JSON payload containing:

Scam detection result and confidence

Current engagement phase

Generated agent reply

Extracted intelligence artifacts

Conversation engagement metadata

Detection signals and reasoning summary

This makes the service suitable for:

Fraud dashboards

Automated reporting pipelines

Downstream enrichment or blacklisting systems

## API Interface
Endpoint

POST /webhook

## Purpose

Processes the latest scammer message, updates conversation state, decides whether to engage, and returns detection + intelligence results.

## Request Fields

conversation_id – Unique identifier per scammer thread

message_id – Optional idempotency key

message – Latest scammer message

history – Optional prior turns (user / agent)

metadata – Reserved for future use (source, locale, channel)

## Response Structure

The response includes:

Detection

scam_detected

confidence

signals

reasoning

Engagement

Current phase

Generated reply

Turn count and last messages

Extracted Intelligence

Bank accounts

UPI IDs

URLs

Amounts
(each with confidence scores)

## Conversation State Management

Each conversation is tracked independently with:

Full turn history

Current engagement phase

Deduplicated extracted artifacts

TTL-based cleanup

Message-level idempotency

This enables long-running scam engagements without cross-thread contamination.

## Architecture Overview
### Key Components

API Layer

Request validation

API-key authentication

Response serialization

Detector

Heuristic scoring engine

Optional LLM classification

Outputs detection confidence, phase hints, and signals

Agent

Autonomous persona controller

Phase-based engagement logic (HOOK → PROBE → HARVEST)

LLM-driven or deterministic fallback responses

Extraction Engine

Regex-first artifact detection

Light normalization (IFSC casing, URL cleanup, currency formatting)

State Store

In-memory conversation tracking

TTL cleanup and deduplication

## Design Goals

Minimal, fast, and webhook-friendly.

Safe, controlled scammer engagement

High signal-to-noise intelligence extraction

LLM-optional (works with or without model access)

Easy integration into existing fraud pipelines

Agentic Honey-Pot for Scam Detection & Intelligence Extraction
Minimal FastAPI service for the Agentic Honey-Pot hackathon that:

Accepts scam conversation events via /webhook
Detects scam intent and switches to an autonomous persona
Engages scammers over multiple turns to harvest intel
Extracts actionable intel (bank accounts, UPI IDs, phishing links, amounts)
Returns structured JSON with detection, engagement, and extracted artifacts
Now extended with:

Optional LLM-powered detector/agent (via OPENAI_API_KEY)
Phase-aware persona (HOOK → PROBE → HARVEST)
Regex-first extraction with normalization (bank + IFSC, UPI, URLs, amounts)
Structured response including heuristic/LLM signals and reasoning
Local Setup (Windows-friendly)
Python: 3.11 (recommended – 3.14 is too new for pydantic-core at the moment)
Clone the repo
git clone https://github.com/Thegenarator/Intelligence_Extraction.git
cd Intelligence_Extraction
Create and activate a virtualenv (Python 3.11)
py -3.11 -m venv .venv
.\.venv\Scripts\activate
Install deps
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Configure environment
Option A – via PowerShell env vars:
setx API_KEY "your-long-random-secret"
setx SERVICE_NAME "agentic-honeypot"
:: Optional: enable LLM behavior
setx OPENAI_API_KEY "sk-..."
setx DETECTOR_MODEL "gpt-4o-mini"
setx AGENT_MODEL "gpt-4o-mini"
Option B – using the provided env.example (recommended for local dev):
Copy env.example → .env (same folder)
Fill in values, e.g.
API_KEY=Pf+xQaA1iffufrKVZTsaPmDbSDQkOABoQpXNimobb7o=
SCAM_THRESHOLD=0.1 (more aggressive scam detection for testing)
The app uses python-dotenv to load .env automatically.
Run the API server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Explore the API
Health check: open in browser
http://localhost:8000/health
Interactive docs (Swagger UI):
http://localhost:8000/docs
From Swagger UI, you can use POST /webhook directly (see usage below).

API Usage
Endpoint: POST /webhook
Auth header (required): X-API-Key: <your-API_KEY>
Request body (application/json):

conversation_id: string – unique id per scammer thread
message_id: string (optional) – for idempotency; duplicate ids are ignored
message: string – latest scammer message
history: optional array of previous turns, items:
role: "user" or "agent"
message: string
metadata: optional object – reserved for future use (locale, source, etc.)
Example:

{
  "conversation_id": "demo-1",
  "message_id": "1",
  "message": "Pay the processing fee via UPI to receive your refund today",
  "history": []
}
Response body:

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
Curl examples
Simple one-liner (PowerShell):

curl -X POST "http://localhost:8000/webhook" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: YOUR_API_KEY_HERE" `
  -d "{ \"conversation_id\": \"demo-1\", \"message_id\": \"1\", \"message\": \"Pay the processing fee via UPI to receive your refund today\", \"history\": [] }"
Replace YOUR_API_KEY_HERE with exactly the same value you configured via .env or setx.

Internals & Architecture
app/main.py: FastAPI wiring, request models, API-key auth, response schema.
app/state.py: in-memory conversation store with:
history of turns
phase (SCREEN/HOOK/PROBE/HARVEST/NOT_SCAM)
deduped extracted intel
TTL-based cleanup + message_id idempotency
app/detector.py: hybrid detector
Heuristic scoring (keywords, urgency, long digits, currency, links)
Optional LLM classification (if OPENAI_API_KEY is set)
Outputs DetectionResult with scam_detected, confidence, phase_hint, signals
app/agent.py: autonomous agent persona
Simple state machine: NOT_SCAM → HOOK → PROBE → HARVEST
LLM persona prompting (if configured) with HOOK/PROBE/HARVEST tactics
Deterministic templates as fallback (for no-LLM environments)
app/extraction.py: regex-first intel extraction
Bank accounts, IFSC, UPI IDs, URLs, amounts
Light normalization (e.g., URL trim, uppercase IFSC)
app/config.py: environment config helpers (keys, thresholds, timeouts).
Deployment to Render
This project is configured for easy deployment to Render. See DEPLOYMENT.md for detailed instructions.

Quick Start
Push to GitHub

git add .
git commit -m "Ready for deployment"
git push origin main
Deploy on Render

Go to https://dashboard.render.com
Click "New +" → "Blueprint"
Connect your GitHub repository
Render will auto-detect render.yaml and configure everything
Set Environment Variables

In Render dashboard → Environment, add:
API_KEY: Your secret API key (required)
OPENAI_API_KEY: Optional, for LLM features
Your service will be live at: https://your-service-name.onrender.com

Testing Your Live Service
Health check: https://your-service-name.onrender.com/health
API docs: https://your-service-name.onrender.com/docs
Webhook endpoint: https://your-service-name.onrender.com/webhook
Note: Free tier services may spin down after inactivity. First request after spin-down may take 30-60 seconds.
